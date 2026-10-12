#!/usr/bin/env python3
"""Bounded cached-weight CUDA DoRA normalizer; CPU-only deferred join."""
import os
import sys
# Select physical device before importing torch; joining never creates CUDA state.
_JOIN = '--join' in sys.argv
_DEVICE = sys.argv[sys.argv.index('--gpu')+1] if '--gpu' in sys.argv else '5'
os.environ['CUDA_VISIBLE_DEVICES'] = '' if _JOIN else _DEVICE
for _name in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[_name] = '2'
import argparse
import csv
import gzip
import gc as garbage_collection
import weakref
import hashlib
import inspect
import json
import math
import platform
import resource
import subprocess
import time
from pathlib import Path
import numpy as np
import torch
import peft
import safetensors
from safetensors import safe_open
from peft.tuners.lora.dora import DoraLinearLayer

torch.set_num_threads(2)
torch.set_num_interop_threads(2)
CHECKS = []
ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT/'docs/diagnostics/radial-activity-2026-10-11'
RAW = Path('./artifacts')
BUDGET = 2*1024**3


def check(name, condition, detail=None):
    CHECKS.append({'name':name,'pass':bool(condition),'detail':detail})
    if not condition:
        raise RuntimeError(f'{name}: {detail}')


def sha(path):
    h = hashlib.sha256()
    with open(path,'rb') as f:
        while b := f.read(8*1024**2): h.update(b)
    return h.hexdigest()


def dump(path, obj):
    Path(path).write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')


def smi():
    out = subprocess.check_output(['nvidia-smi','--query-gpu=index,uuid,name,memory.total,memory.free,memory.used,utilization.gpu,driver_version','--format=csv,noheader,nounits'],text=True)
    fields = ['index','uuid','name','total_mib','free_mib','used_mib','utilization_percent','driver']
    return [dict(zip(fields,[v.strip() for v in line.split(',')])) for line in out.strip().splitlines()]


def own_process_vram():
    out = subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,used_memory','--format=csv,noheader,nounits'],text=True)
    vals = [int(line.split(',')[1].strip()) for line in out.splitlines() if line.split(',')[0].strip()==str(os.getpid()) and line.split(',')[1].strip().isdigit()]
    return max(vals,default=0)


def header(path):
    with open(path,'rb') as f:
        n = int.from_bytes(f.read(8),'little')
        return json.loads(f.read(n))


def inputs():
    cfgpath = ROOT/'configs/shadow_qwen3_4b_gsm8k.json'
    dlpath = ROOT/'results/shadow_4b_gsm8k-downloads.json'
    cfg,dl = json.loads(cfgpath.read_text()),json.loads(dlpath.read_text())
    base,adapter = (Path(dl['artifacts'][k]['snapshot_path']) for k in ('base','dora'))
    for k,p in [('base',base),('dora',adapter)]:
        check(k+' pinned revision',p.name==cfg['artifacts'][k]['revision']==dl['artifacts'][k]['revision'])
    indexpath = base/'model.safetensors.index.json'
    index = json.loads(indexpath.read_text())['weight_map']
    ac = json.loads((adapter/'adapter_config.json').read_text())
    check('supported configuration',ac['r']==32 and ac['lora_alpha']==32 and ac['use_dora'] and not ac.get('use_rslora') and not ac.get('rank_pattern') and not ac.get('alpha_pattern') and not ac.get('fan_in_fan_out') and ac.get('bias')=='none' and not ac.get('modules_to_save'))
    ah = header(adapter/'adapter_model.safetensors')
    modules = [f'base_model.model.model.layers.{i}.self_attn.{p}_proj' for i in range(36) for p in ('q','k','v','o')]
    suffixes = ['.lora_A.weight','.lora_B.weight','.lora_magnitude_vector']
    expected = {m+s for m in modules for s in suffixes}
    check('exact 432 adapter keys',set(ah)-{'__metadata__'}==expected)
    bh = {sh:header(base/sh) for sh in sorted({index[m.removeprefix('base_model.model.')+'.weight'] for m in modules})}
    dims = {'q':(4096,2560),'k':(1024,2560),'v':(1024,2560),'o':(2560,4096)}
    for m in modules:
        p = m.split('.')[-1][0]; out,inp = dims[p]
        key = m.removeprefix('base_model.model.')+'.weight'
        b = bh[index[key]][key]
        check(m+' base shape/dtype',b['shape']==[out,inp] and b['dtype']=='BF16')
        for suffix,shape in zip(suffixes,([32,inp],[out,32],[out])):
            v = ah[m+suffix]
            check(m+suffix+' shape/dtype',v['shape']==shape and v['dtype']=='F32')
    paths = [cfgpath,dlpath,indexpath,base/'config.json',adapter/'adapter_config.json',adapter/'adapter_model.safetensors']+[base/sh for sh in bh]
    hashes = {str(p):sha(p) for p in paths}
    for k,p in [('base',base),('dora',adapter)]:
        for f in cfg['artifacts'][k]['files']:
            path = str(p/f['path'])
            if path in hashes and f['sha256']:
                check(k+'/'+f['path']+' pinned hash',hashes[path]==f['sha256'])
    return base,adapter,index,modules,hashes


def valid(n):
    check('strict positive finite denominator',bool(torch.all(torch.isfinite(n)&(n>0))))


def norm_path(w,a,b,m):
    with torch.autocast('cuda',dtype=torch.bfloat16):
        eye = torch.eye(a.shape[1],device='cuda',dtype=torch.float32)
        first = torch.nn.functional.linear(eye,a)
        lid = torch.nn.functional.linear(first,b).T
        u = w.float()+lid*1.
        n = torch.linalg.norm(u,dim=1).to(u.dtype)
        g = m/n
        actual = DoraLinearLayer(False).get_weight_norm(w.float(),lid,1.)
    valid(n)
    check('installed PEFT norm bitwise agreement',torch.equal(n,actual))
    trace = {k:str(v.dtype) for k,v in dict(identity=eye,first_linear=first,second_linear_transposed=lid,base=w,addition=u,norm=n,magnitude=m,quotient=g).items()}
    check('dtype trace',all(trace[k]=='torch.float32' for k in ('identity','addition','norm','magnitude','quotient')) and all(trace[k]=='torch.bfloat16' for k in ('first_linear','second_linear_transposed','base')))
    return u,n,g,lid,trace


def toys():
    w = torch.tensor([[3.,4.],[0.,2.]],device='cuda',dtype=torch.bfloat16)
    a = torch.tensor([[.1,.2]],device='cuda'); b = torch.tensor([[.2],[.3]],device='cuda')
    m = torch.ones(2,device='cuda')
    u,n,g,_,trace = norm_path(w,a,b,m)
    check('toy g1',torch.equal(n/n,torch.ones_like(n)))
    check('toy g1 radialzero',bool(torch.all(((n/n-1)[:,None]*u)==0)))
    scales = torch.tensor([2.,.5],device='cuda')
    measured = (n*scales)/n
    check('toy known scaling',torch.equal(measured,scales))
    check('toy known scaled row norms',torch.allclose(torch.linalg.norm(measured[:,None]*u,dim=1),scales*n,rtol=8*torch.finfo(torch.float32).eps,atol=0))
    return trace


def flags():
    return dict(cuda_matmul_allow_tf32=torch.backends.cuda.matmul.allow_tf32,cudnn_allow_tf32=torch.backends.cudnn.allow_tf32,cudnn_deterministic=torch.backends.cudnn.deterministic,cudnn_benchmark=torch.backends.cudnn.benchmark,deterministic_algorithms=torch.are_deterministic_algorithms_enabled(),float32_matmul_precision=torch.get_float32_matmul_precision(),allow_fp16_reduced_precision_reduction=torch.backends.cuda.matmul.allow_fp16_reduced_precision_reduction,allow_bf16_reduced_precision_reduction=torch.backends.cuda.matmul.allow_bf16_reduced_precision_reduction,CUBLAS_WORKSPACE_CONFIG=os.environ.get('CUBLAS_WORKSPACE_CONFIG'),autocast_dtype='torch.bfloat16',autocast_cache_enabled=torch.is_autocast_cache_enabled())


def measure(args):
    start = time.perf_counter()
    check('installed PEFT Dora source pinned hash',sha(inspect.getfile(DoraLinearLayer))=='07d514fd057d8aa9ec7b89bec3f3fbd04862951c1a8ff73153e833096481ecf5')
    base,adapter,index,modules,hashes = inputs()
    hash_seconds = time.perf_counter()-start
    if args.pilot: modules = modules[:4]
    raw = RAW/('cuda-pilot' if args.pilot else 'cuda-full'); raw.mkdir(parents=True,exist_ok=True)
    pre = smi(); selected = next(x for x in pre if x['index']==args.gpu)
    check('known device state/free >=4GiB',int(selected['free_mib'])>=4096,selected)
    torch.cuda.set_per_process_memory_fraction(BUDGET/(int(selected['total_mib'])*1024**2),0)
    torch.cuda.reset_peak_memory_stats()
    trace = toys()
    torch.cuda.synchronize()
    records=[]; timings=[]; process_peak=own_process_vram(); rowpath=raw/'cuda-row-activity.csv.gz'
    fields=['module','projection','row','n_cuda','g_cuda','m','n_cpu_same_cuda_product','g_cpu_same_cuda_product']
    with gzip.open(rowpath,'wt',newline='') as f, safe_open(adapter/'adapter_model.safetensors',framework='pt',device='cpu') as ad:
        writer=csv.DictWriter(f,fieldnames=fields); writer.writeheader()
        for module in modules:
            t0=time.perf_counter(); key=module.removeprefix('base_model.model.')+'.weight'
            with safe_open(base/index[key],framework='pt',device='cpu') as sh:
                wc=sh.get_slice(key)[:,:]
            ac,bc,mc=(ad.get_tensor(module+s) for s in ('.lora_A.weight','.lora_B.weight','.lora_magnitude_vector'))
            check(module+' finite inputs',all(bool(torch.all(torch.isfinite(v))) for v in (wc,ac,bc,mc)))
            io=time.perf_counter()-t0
            torch.cuda.synchronize(); t1=time.perf_counter(); ev0=torch.cuda.Event(enable_timing=True); ev1=torch.cuda.Event(enable_timing=True); ev0.record()
            w,a,b,m=(v.to('cuda') for v in (wc,ac,bc,mc))
            u,n,g,p,dt=norm_path(w,a,b,m)
            check(module+' finite quotient',bool(torch.all(torch.isfinite(g))))
            ssr=ssd=ssrm=0.
            # FP64 reductions of explicit FP32 tensors, bounded row blocks.
            n0=torch.linalg.norm(w.float(),dim=1)
            for lo in range(0,w.shape[0],128):
                ub=u[lo:lo+128]; wb=w[lo:lo+128].float(); gb=g[lo:lo+128,None]
                ssr+=float(((gb-1)*ub).double().square().sum())
                ssd+=float((gb*ub-wb).double().square().sum())
                ssrm+=float((((m[lo:lo+128]-n0[lo:lo+128])/n[lo:lo+128])[:,None]*ub).double().square().sum())
            nc=n.cpu().numpy().copy(); gc=g.cpu().numpy().copy(); pc=p.cpu(); mm=mc.numpy().copy()
            ev1.record(); torch.cuda.synchronize(); tensor_wall=time.perf_counter()-t1; event_seconds=ev0.elapsed_time(ev1)/1000
            allocated=torch.cuda.max_memory_allocated(); reserved=torch.cuda.max_memory_reserved()
            check('allocator budget <=2GiB',allocated<=BUDGET and reserved<=BUDGET,dict(allocated=allocated,reserved=reserved))
            # CPU norm of exactly the CUDA-produced BF16 product isolates reductions.
            t2=time.perf_counter(); ns=torch.linalg.norm(wc.float()+pc*1.,dim=1); valid(ns); gs=mc/ns
            cpu_same=time.perf_counter()-t2
            for row in range(len(nc)):
                writer.writerow(dict(module=module,projection=module.split('.')[-1][0],row=row,n_cuda=float(nc[row]),g_cuda=float(gc[row]),m=float(mm[row]),n_cpu_same_cuda_product=float(ns[row]),g_cpu_same_cuda_product=float(gs[row])))
            records.append(dict(module=module,projection=module.split('.')[-1][0],rows=len(nc),cuda_R_ss=ssr,cuda_Delta_ss=ssd,cuda_Rm_ss=ssrm))
            process_peak=max(process_peak,own_process_vram())
            timings.append(dict(module=module,read_seconds=io,cuda_tensor_wall_seconds=tensor_wall,cuda_stream_event_seconds=event_seconds,cpu_same_product_norm_seconds=cpu_same))
            own_refs=[weakref.ref(v) for v in (w,a,b,m,u,n,g,p,n0)]
            del w,a,b,m,u,n,g,p,n0,ub,wb,gb,pc,wc,ac,bc,mc,ns,gs
            garbage_collection.collect()
            check(module+' own CUDA tensors released',all(ref() is None for ref in own_refs))
            torch.cuda.empty_cache()
            print(json.dumps({'module':module,'cuda_tensor_wall_seconds':tensor_wall,'allocated_peak_bytes':allocated,'reserved_peak_bytes':reserved}),flush=True)
    torch.cuda.synchronize()
    garbage_collection.collect()
    before_workspace_cleanup_allocated=torch.cuda.memory_allocated()
    torch.cuda.empty_cache()
    post_allocated=torch.cuda.memory_allocated();post_reserved=torch.cuda.memory_reserved()
    check('all own Python CUDA tensors released',all(ref() is None for ref in own_refs))
    srcpaths=[Path(inspect.getfile(DoraLinearLayer)),Path(inspect.getfile(peft)),Path(inspect.getfile(torch))]
    metadata=dict(mode='pilot' if args.pilot else 'full',modules=len(records),rows=sum(x['rows'] for x in records),checks=CHECKS,records=records,timings=timings,input_hashes=hashes,library_source_hashes={str(p):sha(p) for p in srcpaths},versions=dict(python=platform.python_version(),torch=torch.__version__,cuda=torch.version.cuda,peft=peft.__version__,numpy=np.__version__,safetensors=safetensors.__version__),flags=flags(),dtype_trace=trace,gpu=selected,pid=os.getpid(),threads=2,allocator_budget_bytes=BUDGET,allocated_peak_bytes=torch.cuda.max_memory_allocated(),reserved_peak_bytes=torch.cuda.max_memory_reserved(),nvidia_process_peak_mib=process_peak,before_workspace_cleanup_allocated_bytes=before_workspace_cleanup_allocated,cublas_workspace_cleanup_available=False,post_release_allocated_bytes=post_allocated,post_release_reserved_bytes=post_reserved,nvidia_before=pre,nvidia_after_tensor_release=smi(),hash_io_seconds=hash_seconds,process_wall_seconds=time.perf_counter()-start,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,raw_rows=dict(path=str(rowpath),sha256=sha(rowpath)),code_sha256=sha(__file__),spec_hashes={str(DOC/f):sha(DOC/f) for f in ['SPEC.md','INVENTORY.md','PRECISION_REVIEW.md','CUDA_PROBE_SPEC.md']},scheduler_observation='squeue,sinfo,qstat absent; /etc/slurm,/etc/slurm.conf,/etc/pbs.conf absent; no /etc/motd allocation notice; user explicitly authorizes occupied GPUs')
    dump(raw/'run.json',metadata)
    print(json.dumps({'complete':True,'metadata':str(raw/'run.json'),'rows':metadata['rows'],'wall_seconds':metadata['process_wall_seconds'],'allocated_peak_bytes':metadata['allocated_peak_bytes'],'reserved_peak_bytes':metadata['reserved_peak_bytes'],'nvidia_process_peak_mib':process_peak}),flush=True)


def readrows(path):
    with gzip.open(path,'rt') as f: return list(csv.DictReader(f))


def desc(x,prefix):
    x=np.asarray(x,dtype=np.float64)
    return {prefix+'_'+k:float(np.quantile(x,q)) for k,q in [('min',0),('median',.5),('p90',.9),('p99',.99),('max',1)]}|{prefix+'_mean':float(np.mean(x))}


def csvwrite(path,rows):
    with open(path,'w',newline='') as f:
        wr=csv.DictWriter(f,fieldnames=list(rows[0]));wr.writeheader();wr.writerows(rows)


def join(args):
    t0=time.perf_counter()
    meta=json.loads((RAW/'cuda-full/run.json').read_text());pilot=json.loads((RAW/'cuda-pilot/run.json').read_text())
    process_pids=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader,nounits'],text=True).split()
    check('pilot and full GPU processes exited',str(meta['pid']) not in process_pids and str(pilot['pid']) not in process_pids,{'pilot_pid':pilot['pid'],'full_pid':meta['pid']})
    cr=readrows(meta['raw_rows']['path']); pr=readrows(pilot['raw_rows']['path']); cpupath=Path(args.cpu_rows)
    check('CUDA raw hash',sha(meta['raw_rows']['path'])==meta['raw_rows']['sha256'])
    check('pilot raw hash',sha(pilot['raw_rows']['path'])==pilot['raw_rows']['sha256'])
    cpu=readrows(cpupath)
    def key(x): return x['module'],int(x['row'])
    lookup={key(r):r for r in cpu}; full={key(r):r for r in cr}
    check('unique complete matched rows',len(lookup)==len(cpu)==313344 and len(full)==len(cr)==313344 and lookup.keys()==full.keys())
    for field in ['n_cuda','g_cuda']:
        errors=[abs(float(p[field])-float(full[key(p)][field])) for p in pr]
        scales=[abs(float(p[field])) for p in pr]
        check('pilot/full '+field+' within8FP32eps',all(e<=8*np.finfo(np.float32).eps*s for e,s in zip(errors,scales)),{'max_absolute_error':max(errors),'rtol':8*float(np.finfo(np.float32).eps),'atol':0})
    check('all identical m for joined rows',all(float(r['m'])==float(lookup[key(r)]['m']) for r in cr))
    vals=[]
    for r in cr:
        c=lookup[key(r)];m=float(r['m'])
        vals.append(dict(module=r['module'],projection=r['projection'],g=float(r['g_cuda']),ideal=float(c['g']),cpu=float(c['surrogate_g']),same=float(r['g_cpu_same_cuda_product']),m=m,n=float(r['n_cuda']),n_cpu=float(c['surrogate_n']),n_ideal=float(c['n']),same_n=float(r['n_cpu_same_cuda_product']),n0=float(c['base_norm_fp32'])))
    with open(DOC/'module-activity.csv') as f: idealrecords={r['module']:r for r in csv.DictReader(f)}
    cudarecords={r['module']:r for r in meta['records']}
    def summary(selected,name):
        g=np.array([r['g'] for r in selected]);m=np.array([r['m'] for r in selected]);n=np.array([r['n'] for r in selected]);n0=np.array([r['n0'] for r in selected]);mods=sorted({r['module'] for r in selected})
        result={'group':name,'modules':len(mods),'rows':len(selected),'g_equals_one':int(np.count_nonzero(g==1)),'g_below_one':int(np.count_nonzero(g<1)),'g_above_one':int(np.count_nonzero(g>1)),'g_negative':int(np.count_nonzero(g<0)),'m_zero':int(np.count_nonzero(m==0)),'bf16_g_equals_one_counterfactual':int(np.count_nonzero(torch.from_numpy(g.astype(np.float32)).to(torch.bfloat16)==1))}
        result.update(desc(g-1,'signed_g_minus_one'));result.update(desc(abs(g-1),'abs_g_minus_one'))
        result.update(desc((m-n0)/n0,'endpoint_m_base_relative_residual'))
        for source,field,nfield in [('ideal','ideal','n_ideal'),('cpu_surrogate','cpu','n_cpu'),('cpu_same_cuda_product','same','same_n')]:
            ref=np.array([r[field] for r in selected]);nr=np.array([r[nfield] for r in selected]);err=abs(g-ref)
            result.update(desc(err,'cuda_vs_'+source+'_g_abs_error'))
            rel=np.divide(err,abs(ref),out=np.zeros_like(err),where=ref!=0)
            result.update(desc(rel[ref!=0],'cuda_vs_'+source+'_g_relative_error') if np.any(ref!=0) else {('cuda_vs_'+source+'_g_relative_error_'+k):None for k in ['min','median','p90','p99','max','mean']})
            result['cuda_vs_'+source+'_relative_error_null_rows']=int(np.count_nonzero(ref==0))
            result['cuda_vs_'+source+'_g_sign_crossings']=int(np.count_nonzero((g-1)*(ref-1)<0))
            result['cuda_vs_'+source+'_g_identity_class_changes']=int(np.count_nonzero((g==1)!=(ref==1)))
            result.update(desc(abs(n-nr),'cuda_vs_'+source+'_n_abs_error'))
        for k in ['cuda_R_ss','cuda_Delta_ss','cuda_Rm_ss']:
            result[k]=sum(cudarecords[v][k] for v in mods)
        for k in ['R_ss','Delta_ss','Rm_ss']:
            result['ideal_'+k]=sum(float(idealrecords[v][k]) for v in mods)
        for source in ['cuda','ideal']:
            for numerator in ['R','Rm']:
                den=result[source+'_Delta_ss'];result[source+'_'+numerator+'_norm_over_Delta']=math.sqrt(result[source+'_'+numerator+'_ss']/den) if den>0 else None
        return result
    bymodule=[]
    for module in cudarecords:
        s=summary([r for r in vals if r['module']==module],module);s['module']=s.pop('group');bymodule.append(s)
    groups=[summary(vals,'all')]+[summary([r for r in vals if r['projection']==p],p.upper()) for p in ('q','k','v','o')]
    check('144 module/5 group outputs',len(bymodule)==144 and len(groups)==5)
    check('global count consistency',groups[0]['rows']==sum(r['rows'] for r in groups[1:])==313344)
    csvwrite(DOC/'cuda-module-activity.csv',bymodule);csvwrite(DOC/'cuda-group-activity.csv',groups)
    resources={k:meta[k] for k in ['gpu','pid','threads','allocator_budget_bytes','allocated_peak_bytes','reserved_peak_bytes','nvidia_process_peak_mib','before_workspace_cleanup_allocated_bytes','cublas_workspace_cleanup_available','post_release_allocated_bytes','post_release_reserved_bytes','nvidia_before','nvidia_after_tensor_release','hash_io_seconds','process_wall_seconds','peak_rss_kib']}
    failure_paths=sorted(RAW.glob('cuda-pilot-failed-*/*'))
    failed_tensor_wall=0.
    for logpath in RAW.glob('cuda-pilot-failed-*/probe.log'):
        for line in logpath.read_text().splitlines():
            try: rec=json.loads(line)
            except json.JSONDecodeError: continue
            failed_tensor_wall+=float(rec.get('cuda_tensor_wall_seconds',0.))
    resources.update(accepted_pilot_cuda_tensor_wall_seconds=sum(x['cuda_tensor_wall_seconds'] for x in pilot['timings']),failed_attempts_recorded_cuda_tensor_wall_seconds=failed_tensor_wall,failed_attempt_full_process_times_unavailable=True,gpu_residency_upper_bound_process_minus_hashio_seconds=meta['process_wall_seconds']-meta['hash_io_seconds'],process_exit_verified=True,nvidia_snapshot_after_process_exit=smi(),cuda_tensor_wall_seconds=sum(x['cuda_tensor_wall_seconds'] for x in meta['timings']),cuda_stream_event_seconds=sum(x['cuda_stream_event_seconds'] for x in meta['timings']),cpu_same_product_norm_seconds=sum(x['cpu_same_product_norm_seconds'] for x in meta['timings']),read_seconds=sum(x['read_seconds'] for x in meta['timings']),cpu_join_seconds=time.perf_counter()-t0,pilot={k:pilot[k] for k in ['process_wall_seconds','allocated_peak_bytes','reserved_peak_bytes','nvidia_process_peak_mib']},scheduler_observation=meta['scheduler_observation'],note='CUDA tensor wall and stream-event intervals include transfers, host synchronization gaps and reduction loops; neither is pure compute/utilization or total process time. Process-minus-initial-hashio bounds GPU residency approximately through metadata snapshot, excluding import startup and tiny final output writes. Failed cleanup attempts are separately disclosed; full failed process times unavailable. Weak references verify own tensors released before exit; remaining allocator bytes are backend workspace/cache, explicitly reported. Process exit separately verified by nvidia-smi PID absence; driver context released on exit.')
    dump(DOC/'cuda-resource-use.json',resources)
    validation={'pass':True,'checks_count':len(CHECKS)+len(meta['checks'])+len(pilot['checks']),'checks':CHECKS,'cuda_full_checks':meta['checks'],'cuda_pilot_checks':pilot['checks'],'modules':144,'rows':313344,'limitations':['Norm-only, no full model/activation/logit/quality measurement','Endpoint base-norm residual is not identified training movement','CPU/CUDA comparisons descriptive, no independent training repetitions'],'join_cuda_visible_devices':os.environ['CUDA_VISIBLE_DEVICES']}
    dump(DOC/'cuda-validation.json',validation)
    method='''# CUDA normalizer diagnostic\n\nCached BF16 base and saved FP32 A/B/m, scaling1, 144 GSM8K attention modules. No model construction, activation forward, generation or training. One GPU, two CPU numerical threads; allocator capped2GiB. Owned tensor release is checked via weak references; residual backend workspace allocator bytes are recorded before exit. Pilot/full PID absence in nvidia-smi verifies exit afterward. Two initial cleanup-validation attempts are retained in server-only failure directories; these did not alter norm arithmetic.\n\nUnder CUDA BF16 autocast, build full FP32 identity, apply two F.linear operations, transpose BF16 product, add to FP32 base, compute FP32 row norm and FP32 quotient. Every module norm is bitwise compared with installed PEFT DoraLinearLayer.get_weight_norm. Flags are recorded without modification. A direct B@A shortcut is not used.\n\nCUDA rows join accepted CPU idealFP32 and full two-linear CPU BF16 surrogate by exact module/row/m on server CPU after CUDA exits. Same CUDA BF16 product is separately reduced on CPU, separating norm reduction from product differences. All quantiles pool actual rows; global Frobenius ratios use sums of FP64 squares of FP32 radial/total differences. Fixed-base-norm endpoint residual and reset perturbation are separate from unknown training initialization. Relative quotient errors exclude and explicitly count reference-zero rows, yielding null if all references zero. BF16(g)==1 is a counterfactual cast: actual quotient is FP32.\n\nPilot/full reproducibility tolerance was fixed at8FP32 eps relative and0 absolute, before seeing results. Exact comparisons and measured errors are retained. CUDA tensor wall and stream-event intervals include host synchronization gaps between operations; neither measures pure compute or utilization. Process-minus-initial-hashio is an approximate residency upper bound through metadata snapshot, excluding import startup and tiny final writes. Failed cleanup attempts retain raw artifacts and separately reported measured tensor intervals, with full failed process times unavailable. No p-values over rows/modules. Normalizer agreement does not establish full-function equality or a training cause.\n\nRaw paths, hashes, library/source/input/spec/output provenance are in cuda-manifest.json. Raw rows/logs remain server-only.\n'''
    (DOC/'CUDA_METHOD.md').write_text(method)
    outs=['cuda-module-activity.csv','cuda-group-activity.csv','cuda-validation.json','cuda-resource-use.json','CUDA_METHOD.md']
    manifest={'code':{'path':str(Path(__file__)),'sha256':sha(__file__)},'spec_hashes':meta['spec_hashes'],'input_hashes':meta['input_hashes'],'library_source_hashes':meta['library_source_hashes'],'versions':meta['versions'],'flags':meta['flags'],'dtype_trace':meta['dtype_trace'],'failed_attempt_files':{str(p):sha(p) for p in failure_paths if p.is_file()},'raw_files':{str(p):sha(p) for p in [Path(meta['raw_rows']['path']),Path(pilot['raw_rows']['path']),RAW/'cuda-full/run.json',RAW/'cuda-pilot/run.json',RAW/'cuda-full/probe.log',RAW/'cuda-pilot/probe.log',cpupath]},'cpu_compact_dependencies':{str(DOC/f):sha(DOC/f) for f in ['module-activity.csv','manifest.json','validation.json']},'outputs':{f:sha(DOC/f) for f in outs},'hash_graph':'Outputs exclude this manifest; no circular hash. run.json hashes code/spec/input and raw rows.','scope':'Norm-only CUDA and CPU join; raw server-only; no model forward/training/download/install'}
    dump(DOC/'cuda-manifest.json',manifest)
    print(json.dumps({'complete':True,'checks_count':validation['checks_count'],'groups':groups}),flush=True)


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--gpu',default='5');ap.add_argument('--pilot',action='store_true');ap.add_argument('--join',action='store_true');ap.add_argument('--cpu-rows',default=str(RAW/'full/row-activity.csv.gz'));args=ap.parse_args()
    if args.join: join(args)
    else:
        with torch.inference_mode(): measure(args)
