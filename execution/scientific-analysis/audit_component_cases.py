"""Rebuild frozen fresh-question selection and all tokens without model loading."""
import argparse,hashlib,json,os,sys
from pathlib import Path
os.environ.update(CUDA_VISIBLE_DEVICES='',OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from lora_dora_study.evaluation import sha256_file
from lora_dora_study.fidelity_audit import content_digest
from lora_dora_study.benchmarks import user_content

def main(root):
    read=lambda p:json.loads(p.read_text())
    m=read(root/'manifest-private.json');f=read(root/'frozen.json');excluded=read(root/'exclusions-private.json');cases=read(root/'cases.json')
    if f['phase']!='validation'or len(cases)!=64:raise ValueError('Phase/coverage')
    hashes=set(excluded['content_hashes'])
    if hashlib.sha256(json.dumps(sorted(hashes)).encode()).hexdigest()!=f['exclusions_sha256']:raise ValueError('Exclusion digest')
    for item in excluded['case_files']:
        path=Path(item['path'])
        if sha256_file(path)!=item['sha256']:raise ValueError('Prior collection changed')
        old=read(path);extracted={r['prompt_content_sha256']for r in old if isinstance(r,dict)and 'prompt_content_sha256'in r}
        if len(extracted)!=item['hash_count']or not extracted<=hashes:raise ValueError('Missing exclusion')
    datasets={}
    for split in ['train','test']:
        path=Path(m[split]['path'])
        if sha256_file(path)!=m[split]['sha256']:raise ValueError('Dataset changed')
        datasets[split]=[json.loads(l)for l in path.read_text().splitlines()]
    if not {content_digest(r)for r in datasets['test']+datasets['train'][:232]}<=hashes:raise ValueError('Missing test exclusions')
    from transformers import AutoTokenizer
    tok=AutoTokenizer.from_pretrained(m['base']['snapshot_path'],local_files_only=True,trust_remote_code=False)
    expected=[];selected=set()
    for idx,row in enumerate(datasets['train']):
        h=content_digest(row)
        if h in hashes or h in selected:continue
        prompt=tok.apply_chat_template([{'role':'user','content':user_content('gsm8k',row)}],add_generation_prompt=True,tokenize=False,enable_thinking=False)
        promptids=tok.encode(prompt,add_special_tokens=False);answerids=tok.encode(row['answer'],add_special_tokens=False)[:32]
        if len(promptids)>512 or len(answerids)!=32:continue
        selected.add(h);expected.append({'train_index':idx,'prompt_content_sha256':h,'input_ids':promptids+answerids[:-1],'targets':answerids})
        if len(expected)==64:break
    if cases!=expected:raise ValueError('Not first64 eligible cases / tokens differ')
    if sha256_file(root/'cases.json')!=f['cases_sha256']:raise ValueError('Cases digest')
    result=dict(status='PASS',cases=64,unique_content_hashes=64,excluded_content_hashes=len(hashes),previous_collections=len(excluded['case_files']),
      first_eligible_selection_rebuilt=True,all_question_and_target_tokens_rebuilt=True,no_prior_or_test_content_overlap=True,
      model_loaded=False,gpu_hours=0,cases_sha256=f['cases_sha256'],exclusions_sha256=f['exclusions_sha256'])
    (root/'case-audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);main(p.parse_args().root)
