import copy
import importlib.util
import math
import unittest

from lora_dora_study.fidelity_audit import select_cases, magnitude_gauge, without_d, metrics, convert_custom, projection_fingerprints


class SelectionTests(unittest.TestCase):
    def test_content_exclusion_and_deterministic_selection(self):
        rows=[dict(question=str(i),answer='#### 1') for i in range(20)]
        rows.insert(7,dict(rows[0]))
        selected=select_cases(rows,[rows[9]],count=5,skip=4)
        self.assertEqual([i for i,_ in selected],[4,5,6,8,10])
        self.assertEqual(selected,select_cases(rows,[rows[9]],count=5,skip=4))

    def test_queue_excludes_incident_device_and_strict_boundaries(self):
        from pathlib import Path
        from unittest.mock import patch
        path=Path(__file__).resolve().parents[1]/'execution/next-experiments/admit_queues.py'
        spec=importlib.util.spec_from_file_location('audit_admission_test',path)
        m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        with patch.object(m,'EXCLUDED_INDICES',{1}),patch.object(m,'EXCLUDED_UUIDS',{'incident'}),patch.object(m,'MAX_USED_MIB',7168):
            g=dict(index=0,uuid='ok',utilization_percent=19,used_mib=7167)
            self.assertTrue(m.eligible(g))
            for key,value in [('index',1),('uuid','incident'),('utilization_percent',20),('used_mib',7168)]:
                self.assertFalse(m.eligible(dict(g,**{key:value})))

    def test_gpu_lock_released_before_cpu_and_gpu_failure_blocks_cpu(self):
        import json,os,tempfile,fcntl
        from pathlib import Path
        from types import SimpleNamespace
        from unittest.mock import patch
        path=Path(__file__).resolve().parents[1]/'execution/next-experiments/admit_queues.py'
        spec=importlib.util.spec_from_file_location('audit_worker_test',path)
        m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        queue={'audit':{phase:[dict(name=phase,script='fixture.py',budget_seconds=1)] for phase in ['gpu','cpu']}}
        for gpu_result in [0,1]:
            with tempfile.TemporaryDirectory() as tmp:
                fd=os.open(str(Path(tmp)/'lock'),os.O_CREAT|os.O_WRONLY,0o600);calls=[]
                fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
                def run(command,**kwargs):
                    phase=command[command.index('--phase')+1];calls.append(phase)
                    if phase=='gpu':
                        os.fstat(fd);return SimpleNamespace(returncode=gpu_result)
                    probe=os.open(str(Path(tmp)/'lock'),os.O_WRONLY)
                    try:fcntl.flock(probe,fcntl.LOCK_EX|fcntl.LOCK_NB)
                    finally:os.close(probe)
                    self.assertEqual(kwargs['env']['CUDA_VISIBLE_DEVICES'],'')
                    return SimpleNamespace(returncode=0)
                with patch.object(m,'SPEC',queue),patch.object(m,'P',Path(tmp)),patch.object(m.subprocess,'run',side_effect=run):
                    self.assertEqual(m.worker('audit','GPU-test',fd),gpu_result)
                self.assertEqual(calls,['gpu','cpu'] if gpu_result==0 else ['gpu'])
                state=json.loads((Path(tmp)/'audit/state.json').read_text())
                self.assertEqual(state['status'],'complete' if gpu_result==0 else 'failed')


@unittest.skipUnless(importlib.util.find_spec('torch') and importlib.util.find_spec('peft'),'Torch/PEFT required')
class TinyModelTests(unittest.TestCase):
    def model(self):
        import torch
        from transformers import Qwen3Config,Qwen3ForCausalLM
        from peft import get_peft_model,LoraConfig
        torch.set_num_threads(2);torch.manual_seed(71)
        config=Qwen3Config(vocab_size=41,hidden_size=32,intermediate_size=64,num_hidden_layers=2,
                          num_attention_heads=4,num_key_value_heads=2,head_dim=8,attention_bias=False)
        m=get_peft_model(Qwen3ForCausalLM(config),LoraConfig(r=2,lora_alpha=2,
            target_modules=['q_proj','k_proj','v_proj','o_proj'],use_dora=True,task_type='CAUSAL_LM')).eval()
        with torch.no_grad():
            for name,p in m.named_parameters():
                if 'lora_B' in name:p.normal_(std=.03)
                if 'lora_magnitude_vector' in name:p.mul_(1.03)
        return m

    def test_both_functions_and_exact_state_restore(self):
        import torch
        m=self.model();x=torch.tensor([[1,2,3,4,5]])
        before={k:v.detach().clone() for k,v in m.state_dict().items()}
        with torch.inference_mode():
            original=m(x,use_cache=False).logits
            with without_d(m):removed=m(x,use_cache=False).logits
            for c in [.995,1.005,2.]:
                with magnitude_gauge(m,c):
                    changed=m(x,use_cache=False).logits
                    torch.testing.assert_close(original,changed,atol=2e-6,rtol=2e-5)
                    with without_d(m):
                        self.assertTrue(torch.equal(removed,m(x,use_cache=False).logits))
        self.assertTrue(all(torch.equal(v,m.state_dict()[k]) for k,v in before.items()))

    def test_exception_restores_dispatch_and_magnitude(self):
        import torch
        m=self.model();before={k:v.detach().clone() for k,v in m.state_dict().items()}
        with self.assertRaisesRegex(RuntimeError,'fixture'):
            with magnitude_gauge(m,1.005),without_d(m):raise RuntimeError('fixture')
        self.assertTrue(all(torch.equal(v,m.state_dict()[k]) for k,v in before.items()))
        for module in m.modules():
            if hasattr(module,'use_dora'):self.assertTrue(module.use_dora['default']);self.assertIn('default',module.lora_variant)

    def test_custom_and_official_fp32_merge(self):
        import torch
        a=self.model();b=copy.deepcopy(a);x=torch.tensor([[1,2,3,4]])
        with torch.inference_mode():
            before=a(x,use_cache=False).logits
            convert_custom(a);b=b.merge_and_unload(safe_merge=True)
            self.assertEqual(projection_fingerprints(a),projection_fingerprints(b))
            torch.testing.assert_close(a(x,use_cache=False).logits,b(x,use_cache=False).logits,atol=2e-6,rtol=2e-5)
            torch.testing.assert_close(a(x,use_cache=False).logits,before,atol=2e-6,rtol=2e-5)

    def test_target_alignment_and_metric_sign(self):
        import torch
        m=self.model();x=torch.tensor([[1,2,3,4,5]])
        with torch.inference_mode():
            full=m(x,use_cache=False).logits[0]
            last=m(x,use_cache=False,logits_to_keep=2).logits[0]
        torch.testing.assert_close(last,full[-2:])
        ref=torch.zeros(2,3);other=ref.clone();other[:,0]=1
        result=metrics(ref,other,[0,0]);self.assertLess(result['nll_difference'],0)
        same=metrics(ref,ref,[0,0]);self.assertEqual(same['rms'],0);self.assertEqual(same['kl_reference_to_changed'],0)
        other[0,0]=float('nan')
        with self.assertRaises(FloatingPointError):metrics(ref,other,[0,0])


if __name__=='__main__':unittest.main()
