"""No generation: check V/O symmetry on representative train/test inputs."""
import json,os,sys,time,resource
from pathlib import Path
S=Path('/path/to/user-user/lora-dora-series');P=S.parent/'lora-dora-profiling';D=P/'distributed-important'
sys.path.insert(0,str(S))
from lora_dora_study.server import gpu_snapshot,write_json
from lora_dora_study.evaluation import sha256_file,source_fingerprint
from lora_dora_study.benchmarks import user_content
from lora_dora_study.adapters import verify_loaded_adapter
from lora_dora_study import rank_symmetry as rank

def main():
 started=time.perf_counter();parent=int(os.environ['RESEARCH_GPU_KEEPER_PID']);uuid=os.environ['RESEARCH_GPU_LEASE_UUID']
 if os.getppid()!=parent or Path('/proc',str(parent)).stat().st_uid!=os.getuid():raise RuntimeError('Wrong keeper')
 paths=[os.readlink('/proc/self/fd/'+fd) for fd in os.environ['RESEARCH_GPU_LEASE_FDS'].split(',')]
 if not any(uuid+'.lock' in p for p in paths) or not any('/slot-' in p for p in paths):raise RuntimeError('Missing lease descriptors')
 if any(p['gpu_uuid']==uuid and p['pid']!=parent for p in gpu_snapshot()['compute_processes']):raise RuntimeError('Foreign GPU process')
 os.environ.update(CUDA_VISIBLE_DEVICES=uuid,OMP_NUM_THREADS='2',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
 import torch
 from transformers import AutoModelForCausalLM,AutoTokenizer
 from peft import PeftModel
 from peft.tuners.lora.layer import LoraLayer
 torch.set_num_threads(2);torch.set_num_interop_threads(1);torch.manual_seed(42)
 spec=json.loads((D/'plan.json').read_text());job=dict(spec['jobs']['gsm8k-dense-dora'])
 downloads=json.loads(Path(job['downloads']).read_text());paths={k:v['snapshot_path'] for k,v in downloads['artifacts'].items()}
 tok=AutoTokenizer.from_pretrained(paths['base'],local_files_only=True)
 model=AutoModelForCausalLM.from_pretrained(paths['base'],local_files_only=True,torch_dtype=torch.bfloat16,device_map={'':'cuda:0'},low_cpu_mem_usage=True,attn_implementation='sdpa')
 model=PeftModel.from_pretrained(model,paths['dora'],local_files_only=True,is_trainable=False);model.eval();adapter=verify_loaded_adapter(model,paths['dora'],True)
 train=Path(job['calibration']);assert sha256_file(train)==job['calibration_sha256']
 manifest=json.loads(Path(job['dataset_manifest']).read_text());test=Path(manifest['path']);assert sha256_file(test)==manifest['jsonl_sha256']
 a=[json.loads(l) for l in train.read_text().split('\n') if l];b=[json.loads(l) for l in test.read_text().split('\n') if l]
 tests=[('train',i,a[i]) for i in range(min(32,len(a)))]+[('test',i,b[i]) for i in sorted({round(k*(len(b)-1)/31) for k in range(32)})]
 inputs=[]
 for split,index,row in tests:
  prompt=tok.apply_chat_template([dict(role='user',content=user_content('gsm8k',row))],tokenize=False,add_generation_prompt=True,enable_thinking=False)
  ids=tok(prompt,add_special_tokens=False)['input_ids'][:128];inputs.append((split,index,ids))
 before_stats=[];joint_stats=[];fixed_stats=[]
 with torch.inference_mode():
  for name,m in model.named_modules():
   if isinstance(m,LoraLayer) and name.endswith('.v_proj'):
    base,value=rank.effective_weight(m);layer=int(name.split('.layers.')[1].split('.')[0]);c=[.5,1.,2.][layer%3]
    before_stats.append(rank.magnitude_direction(base,value));joint_stats.append(rank.magnitude_direction(base*c,value*c));fixed_stats.append(rank.magnitude_direction(base,value*c));del base,value
  def x(ids):return dict(input_ids=torch.tensor([ids],device='cuda:0'),attention_mask=torch.ones((1,len(ids)),device='cuda:0',dtype=torch.long))
  dense=rank.prepare(model,job,x(inputs[0][2]))
  before=[]
  for split,index,ids in inputs:before.append(model(**x(ids)).logits.detach().cpu())
  for name,m in model.named_modules():
   if '.layers.' not in name or not (name.endswith('.self_attn.v_proj') or name.endswith('.self_attn.o_proj')):continue
   layer=int(name.split('.layers.')[1].split('.')[0]);c=[.5,1.,2.][layer%3];factor=c if name.endswith('.v_proj') else 1/c
   m.weight.mul_(factor)
   if name.endswith('.v_proj') and m.bias is not None:m.bias.mul_(factor)
  cases=[]
  for (split,index,ids),old in zip(inputs,before):
   new=model(**x(ids)).logits.detach().cpu();error=float((old.float()-new.float()).abs().max());agree=float((old.argmax(-1)==new.argmax(-1)).float().mean());ok=torch.allclose(old.float(),new.float(),atol=.05,rtol=.01)
   cases.append(dict(split=split,index=index,input_tokens=len(ids),max_abs_logits_error=error,argmax_agreement=agree,allclose=ok));write_json(D/'short-vo-progress.json',dict(completed=len(cases),total=len(inputs)))
  report=dict(status='verified' if all(c['allclose'] for c in cases) else 'failed_numerical_check',full_quality_evaluation=False,generation_calls=0,cases=cases,calibration_hash=sha256_file(train),test_hash=sha256_file(test),source_sha256=source_fingerprint(S),diagnostic_sha256=sha256_file(Path(__file__)),dense_fidelity=dense['dense_fidelity'],adapter_validation={k:v for k,v in adapter.items() if k!='modules'},correlation_before=rank.pearson(before_stats),correlation_joint_base_after=rank.pearson(joint_stats),correlation_fixed_base_after=rank.pearson(fixed_stats),joint_base_rank_preserved=True,fixed_base_same_rank_not_guaranteed=True,scope='Symmetry checked relative to dense reference. Initial adapter-to-dense conversion has separately recorded numerical discrepancy. No trajectory causal claim.',wall_seconds=time.perf_counter()-started,peak_allocated_bytes=torch.cuda.max_memory_allocated(),max_process_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024)
  write_json(D/'short-vo-validation.json',report)
  if report['status']!='verified':raise RuntimeError('V/O symmetry failed representative-input check')
if __name__=='__main__':main()
