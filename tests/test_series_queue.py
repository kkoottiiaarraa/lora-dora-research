import importlib.util
import unittest
from lora_dora_study.benchmarks import score,user_content
from lora_dora_study.series_queue import balance,idle_candidates


class QueueTests(unittest.TestCase):
    def test_balance_covers_all_jobs_once(self):
        jobs=[dict(id=str(i),estimated_gpu_seconds=c) for i,c in enumerate([8,7,6,5,4])]
        queues,loads=balance(jobs)
        self.assertEqual(sorted(j['id'] for q in queues for j in q),['0','1','2','3','4'])
        self.assertLessEqual(abs(loads[0]-loads[1]),4)

    def test_primary_gpu_and_transition_get_priority(self):
        snapshot=dict(gpus=[dict(uuid='GPU-a',used_mib=0,utilization_percent=0),
            dict(uuid='GPU-b',used_mib=0,utilization_percent=0)],compute_processes=[])
        self.assertEqual(idle_candidates(snapshot,dict(status='running',gpu_uuid='GPU-a')),{'GPU-b'})
        self.assertFalse(idle_candidates(snapshot,dict(status='waiting_for_evaluation_gpu')))
        snapshot['compute_processes']=[dict(gpu_uuid='GPU-b')]
        self.assertFalse(idle_candidates(snapshot,dict(status='running',gpu_uuid='GPU-a')))

    def test_mmlu_and_squad_scoring(self):
        row=dict(question='Q',choices=['a','b','c','d'],answer=1)
        self.assertEqual(score('mmlu','Answer:B',row),dict(accuracy=1.))
        self.assertIn('ONLY the letter',user_content('mmlu',row))
        self.assertEqual(score('squadv2','The red car',dict(answers=dict(text=['red car','red automobile']))),dict(exact=1.,f1=1.))
        self.assertEqual(score('squadv2','unanswerable',dict(answers=dict(text=[]))),dict(exact=1.,f1=1.))
        self.assertEqual(score('squadv2','car',dict(answers=dict(text=['red car'])))['f1'],2/3)

    def test_float_paired_statistics_and_holm(self):
        from lora_dora_study.series_results import paired_difference,holm
        r=paired_difference([.2,.2],[.7,.7],100)
        self.assertAlmostEqual(r['difference'],.5)
        self.assertAlmostEqual(r['ci95'][0],.5)
        self.assertEqual(holm({'a':.01,'b':.04,'c':.9}),{'a':.03,'b':.08,'c':.9})


@unittest.skipUnless(importlib.util.find_spec('torch'),'GPU-host CPU venv required')
class InterventionTests(unittest.TestCase):
    def test_actual_peft_radial_and_remove_d_formulas_and_group_coverage(self):
        import torch
        from transformers import Qwen3Config,Qwen3ForCausalLM
        from peft import get_peft_model,LoraConfig
        from peft.tuners.lora.layer import LoraLayer
        from lora_dora_study.interventions import apply_intervention
        torch.set_num_threads(2)
        config=Qwen3Config(vocab_size=32,hidden_size=32,intermediate_size=64,
            num_hidden_layers=2,num_attention_heads=4,num_key_value_heads=2,head_dim=8)
        model=get_peft_model(Qwen3ForCausalLM(config),LoraConfig(r=2,lora_alpha=2,
            target_modules=['q_proj','v_proj'],use_dora=True,task_type='CAUSAL_LM')).eval()
        with torch.no_grad():
            for name,p in model.named_parameters():
                if 'lora_B' in name:p.normal_(std=.03)
        report=apply_intervention(model,'base_magnitude',{'q_proj'})
        self.assertEqual(len(report['modules']),2)
        modules=[(n,m) for n,m in model.named_modules() if isinstance(m,LoraLayer)]
        with torch.inference_mode():
            for name,module in modules:
                if not name.endswith('q_proj'):continue
                base=module.get_base_layer().weight
                update=module.lora_B['default'].weight@module.lora_A['default'].weight
                direction=base+update*module.scaling['default']
                expected=direction*(base.norm(dim=1)/direction.norm(dim=1))[:,None]
                x=torch.randn(3,32)
                torch.testing.assert_close(module(x),torch.nn.functional.linear(x,expected),atol=1e-6,rtol=1e-5)
            apply_intervention(model,'remove_d',{'q_proj'})
            for name,module in modules:
                self.assertEqual(module.use_dora['default'],not name.endswith('q_proj'))
                if name.endswith('q_proj'):
                    base=module.get_base_layer().weight
                    direction=base+module.lora_B['default'].weight@module.lora_A['default'].weight*module.scaling['default']
                    x=torch.randn(3,32)
                    torch.testing.assert_close(module(x),torch.nn.functional.linear(x,direction),atol=1e-6,rtol=1e-5)


if __name__=='__main__':unittest.main()
