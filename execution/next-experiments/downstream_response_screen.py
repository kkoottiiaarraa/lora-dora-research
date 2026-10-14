"""Bounded CPU screen of downstream attenuation versus a dose-matched scalar."""
import argparse
import datetime
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import resource
import signal
import sys
import time

os.environ.update(CUDA_VISIBLE_DEVICES='', OMP_NUM_THREADS='8', MKL_NUM_THREADS='8',
                  OPENBLAS_NUM_THREADS='8', HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1',
                  TOKENIZERS_PARALLELISM='false')
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from lora_dora_study.server import write_json,available_memory_bytes
from lora_dora_study.evaluation import sha256_file


def main(root):
    started=time.monotonic()
    summary=dict(status='running',phase='setup',gpu_hours=0,training=False,
                 started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    def save():
        summary.update(wall_seconds=time.monotonic()-started,
                       peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024)
        write_json(root/'summary.json',summary)
    def deadline(signum,frame):raise TimeoutError('20-minute CPU screen cap')
    signal.signal(signal.SIGALRM,deadline);signal.setitimer(signal.ITIMER_REAL,1200)
    save()
    try:
        manifest=json.loads((root/'manifest-private.json').read_text())
        for rel,digest in manifest['source_sha256'].items():
            if sha256_file(ROOT/rel)!=digest:raise ValueError('Source changed: '+rel)
        import torch
        from transformers import AutoModelForCausalLM
        from peft import PeftModel
        from lora_dora_study.adapters import verify_loaded_adapter
        from lora_dora_study.fidelity_audit import convert_custom,metrics
        from lora_dora_study.downstream_response import frozen_residual,attenuation,source_denominator_logits
        torch.set_num_threads(8);torch.set_num_interop_threads(1)
        torch.manual_seed(20261014);torch.set_float32_matmul_precision('highest')
        versions={k:importlib.metadata.version(k)for k in manifest['versions']}
        if versions!=manifest['versions']:raise ValueError('Versions changed')
        if available_memory_bytes()<40*1024**3:raise BlockingIOError('Need 40GiB available RAM')
        casepath=Path(manifest['cases'])
        if sha256_file(casepath)!=manifest['cases_sha256']:raise ValueError('Cases changed')
        all_cases=json.loads(casepath.read_text())
        cases=all_cases[:24]
        if len(cases)!=24 or len({c['prompt_content_sha256']for c in cases})!=24:
            raise ValueError('Case coverage/uniqueness')
        layers=manifest['layers']
        if layers!=[0,17,35]:raise ValueError('Layer selection changed')
        write_json(root/'cases.json',cases)
        summary.update(phase='load',versions=versions,cases_sha256=sha256_file(root/'cases.json'))
        save()
        model=AutoModelForCausalLM.from_pretrained(manifest['base']['snapshot_path'],
            local_files_only=True,trust_remote_code=False,torch_dtype=torch.float32,
            device_map={'':'cpu'},low_cpu_mem_usage=True,attn_implementation='sdpa')
        model=PeftModel.from_pretrained(model,manifest['dora']['snapshot_path'],
            local_files_only=True,is_trainable=False).eval();model.requires_grad_(False)
        check=verify_loaded_adapter(model,manifest['dora']['snapshot_path'],True)
        if not check['exact_loaded_value_match']or check['adapted_module_count']!=144:
            raise ValueError('Adapter mismatch')
        summary.update(adapter_exact=True,adapted_modules=144)
        if any(p.dtype!=torch.float32 or p.device.type!='cpu'for p in model.parameters()):
            raise ValueError('CPU FP32 required')
        core=model.get_base_model()
        if core.lm_head.bias is not None:raise ValueError('Bias-free head required')

        def plain(case):
            ids=torch.tensor([case['input_ids']])
            with torch.inference_mode():
                y=model(input_ids=ids,attention_mask=torch.ones_like(ids),use_cache=False,logits_to_keep=32).logits[0]
            if not bool(y.isfinite().all()):raise FloatingPointError('Nonfinite logits')
            return y.detach().clone()

        native=[plain(c)for c in cases[:4]]
        directions={}
        for name,module in model.named_modules():
            if not hasattr(module,'use_dora'):continue
            if any(name.endswith(f'layers.{l}.self_attn.{leaf}')for l in layers for leaf in ['v_proj','o_proj']):
                if module.get_base_layer().bias is not None:raise ValueError('Bias-free V/O required')
                directions[name]=(module.get_base_layer().weight.detach().float()+
                    (module.lora_B['default'].weight.float()@module.lora_A['default'].weight.float())*
                    module.scaling['default']).clone()
        if len(directions)!=6:raise ValueError('VO coverage')
        convert_custom(model)
        dense_controls=[metrics(y,plain(c),c['targets'])for y,c in zip(native,cases[:4])]
        write_json(root/'native-dense-controls.json',dense_controls)
        originals={name:model.get_submodule(name).weight.detach().clone()for name in directions}
        del native
        state=dict(armed=False,mode=None,layer=None,alpha=None)
        captured={}
        handles=[]
        def branch_hook(layer,kind):
            def hook(module,args,output):
                if not state['armed']:return
                tensor=output[0]if isinstance(output,tuple)else output
                if kind=='attention'and state['mode']=='gain'and state['layer']==layer:
                    tensor=tensor*(1-state['alpha'])
                    output=(tensor,*output[1:])if isinstance(output,tuple)else tensor
                captured[(layer,kind)]=tensor[0,-32:].detach().clone()
                return output
            return hook
        for layer,block in enumerate(core.model.layers):
            handles.append(block.self_attn.register_forward_hook(branch_hook(layer,'attention')))
            handles.append(block.mlp.register_forward_hook(branch_hook(layer,'mlp')))
        def final_hook(module,args):
            if state['armed']:captured['final']=args[0][0,-32:].detach().clone()
        handles.append(core.model.norm.register_forward_pre_hook(final_hook))
        epsilon=core.model.norm.variance_epsilon

        def run(case,mode=None,layer=None,alpha=None):
            captured.clear();state.update(armed=True,mode=mode,layer=layer,alpha=alpha)
            changed=[]
            try:
                if mode=='remove':
                    with torch.no_grad():
                        for name,u in directions.items():
                            if f'layers.{layer}.'in name:
                                model.get_submodule(name).weight.copy_(u);changed.append(name)
                y=plain(case)
                saved={k:v for k,v in captured.items()}
                if len(saved)!=2*len(core.model.layers)+1:raise ValueError('Hook coverage')
                if any(not bool(v.isfinite().all())for v in saved.values()):
                    raise FloatingPointError('Nonfinite residual')
                return y,saved
            finally:
                state['armed']=False
                with torch.no_grad():
                    for name in changed:model.get_submodule(name).weight.copy_(originals[name])

        def readout(h):
            with torch.inference_mode():return core.lm_head(core.model.norm(h.unsqueeze(0)))[0].detach()

        calibration={l:dict(remove_energy=0.,source_attention_energy=0.)for l in layers}
        summary.update(phase='calibration',completed=0);save()
        for i,case in enumerate(cases[:8]):
            ref,src=run(case)
            for l in layers:
                _,chg=run(case,'remove',l)
                delta=chg[(l,'attention')]-src[(l,'attention')]
                calibration[l]['remove_energy']+=float(delta.double().square().sum())
                calibration[l]['source_attention_energy']+=float(src[(l,'attention')].double().square().sum())
            summary['completed']=i+1;save()
        alphas={l:(c['remove_energy']/c['source_attention_energy'])**.5 for l,c in calibration.items()}
        if not all(0<a<1 for a in alphas.values()):raise ValueError('Invalid attenuation strength')
        write_json(root/'frozen-calibration.json',dict(alphas=alphas,calibration=calibration,
            fit_count=8,evaluation_count=16,fit_targets_used=False,
            source_sha256=manifest['source_sha256'],evaluation_cases_sha256=hashlib.sha256(
                json.dumps(cases[8:],sort_keys=True).encode()).hexdigest()))
        summary.update(phase='evaluation',completed=0,frozen_calibration_sha256=sha256_file(root/'frozen-calibration.json'))
        save()
        rows=[];controls=[]
        cache=root/'logit-cache';cache.mkdir()
        for i,case in enumerate(cases[8:]):
            ref,src=run(case)
            torch.save(ref,cache/f'source-{i}.pt')
            reference_readout=readout(src['final'])
            ctrl=metrics(ref,reference_readout,case['targets'])
            controls.append(dict(case=i,kind='readout_reconstruction',**ctrl))
            if i==0:
                repeated,_=run(case)
                controls.append(dict(case=i,kind='repeat',bitwise=torch.equal(repeated,ref),
                                     **metrics(ref,repeated,case['targets'])))
                if not torch.equal(repeated,ref):raise ValueError('Nonrepeatable source')
            for l in layers:
                for mode in ['remove','gain']:
                    actual,chg=run(case,mode,l,alphas[l])
                    delta=chg[(l,'attention')]-src[(l,'attention')]
                    frozen_h=frozen_residual(src['final'],src[(l,'attention')],chg[(l,'attention')])
                    frozen=readout(frozen_h)
                    fixed=source_denominator_logits(frozen,frozen_h,src['final'],epsilon)
                    a=metrics(ref,actual,case['targets']);f=metrics(ref,frozen,case['targets'])
                    n=metrics(ref,fixed,case['targets'])
                    # Independent telescoping of all changed residual branch outputs.
                    branch_sum=torch.zeros_like(delta,dtype=torch.float64)
                    for j in range(l,len(core.model.layers)):
                        for kind in ['attention','mlp']:
                            branch_sum+=(chg[(j,kind)]-src[(j,kind)]).double()
                    total=(chg['final']-src['final']).double()
                    downstream=branch_sum-delta.double()
                    direct_energy=float(delta.double().square().sum())
                    gain_reference_energy=alphas[l]**2*float(src[(l,'attention')].double().square().sum())
                    row=dict(case=i,source_case_index=i+8,layer=l,mode=mode,
                        prompt_content_sha256=case['prompt_content_sha256'],
                        actual_kl=a['kl_reference_to_changed'],frozen_kl=f['kl_reference_to_changed'],
                        frozen_source_denominator_kl=n['kl_reference_to_changed'],
                        actual_rms=a['rms'],frozen_rms=f['rms'],
                        nll_difference=a['nll_difference'],frozen_nll_difference=f['nll_difference'],
                        attenuation=attenuation(a['kl_reference_to_changed'],f['kl_reference_to_changed']),
                        local_delta_energy=direct_energy,matched_gain_energy=gain_reference_energy,
                        dose_energy_ratio=direct_energy/gain_reference_energy,
                        residual_counteraction=-float((delta.double()*downstream).sum())/direct_energy,
                        branch_partition_max_abs=float((branch_sum-total).abs().max()),
                        branch_partition_relative=float((branch_sum-total).norm()/total.norm().clamp_min(1e-30)),
                        local_delta_rms=float(delta.square().mean().sqrt()))
                    if row['attenuation']is None:raise ValueError('Degenerate frozen effect')
                    rows.append(row)
                    torch.save(dict(actual=actual,frozen=frozen),cache/f'{mode}-{l}-{i}.pt')
                    write_json(root/'rows.json',rows)
            summary['completed']=i+1;save()
        restored,_=run(cases[8])
        expected=torch.load(cache/'source-0.pt',map_location='cpu',weights_only=True)
        controls.append(dict(case=0,kind='restoration',bitwise=torch.equal(restored,expected),
                             **metrics(expected,restored,cases[8]['targets'])))
        write_json(root/'controls.json',controls)
        if not torch.equal(restored,expected):raise ValueError('Restoration mismatch')
        for h in handles:h.remove()
        del model,core
        summary.update(status='complete',phase='terminal',rows=len(rows),control_rows=len(controls),
            native_dense_max_rms=max(c['rms']for c in dense_controls),
            projection_restored=True,cpu_threads=8,source_sha256=manifest['source_sha256'])
        save()
    except Exception as e:
        summary.update(status='failed',error=repr(e));save();raise
    finally:signal.setitimer(signal.ITIMER_REAL,0)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True)
    main(p.parse_args().root)
