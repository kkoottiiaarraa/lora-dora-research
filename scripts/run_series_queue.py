#!/usr/bin/env python3
"""Two independent queues, one worker per queue; compatible global 3-GPU leases."""
import argparse
import datetime
import fcntl
import json
import os
import subprocess
import sys
import time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from lora_dora_study.evaluation import sha256_file
from lora_dora_study.series_queue import idle_candidates
from lora_dora_study.series_results import compare_runs, holm
from lora_dora_study.server import gpu_snapshot, write_json

KEEPER=None
PLAN_PATH=Path('configs/two_series.json')
PRIMARY=Path('/path/to/user-user/lora-dora-research/results/pipeline-20261009T1535Z/state.json')


def record(stage,data):
    lock=Path('/tmp')/('lora-dora-series-handoff-'+str(os.getuid())+'.lock')
    with lock.open('a') as stream:
        fcntl.flock(stream,fcntl.LOCK_EX)
        path=Path('docs/HANDOFF.md')
        text='## '+stage+'\n\nUTC: '+datetime.datetime.now(datetime.timezone.utc).isoformat()
        text+='\n\n```json\n'+json.dumps(data,ensure_ascii=False,indent=2)+'\n```\n\n'
        temporary=path.with_suffix('.tmp.'+str(os.getpid()))
        temporary.write_text(text+path.read_text());temporary.replace(path)


def dependency_reason(job,root):
    if job.get('requires_primary_quality'):
        primary=json.loads(PRIMARY.read_text())
        if primary.get('status')!='quality_complete_interventions_pending':
            return 'waiting_for_primary_quality: '+primary.get('status','unknown')
    for dependency in job.get('dependencies',[]):
        path=root/'jobs'/dependency/'status.json'
        if not path.exists() or json.loads(path.read_text()).get('status')!='complete':
            return 'waiting_for_job: '+dependency
    if not job.get('implemented'):
        return job['readiness_reason']
    if any(not Path(job[k]).is_file() for k in ['dataset_manifest','downloads']):
        return 'waiting_for_pinned_downloads'
    return None


def await_gpu(state,output):
    if state.get('retained_gpu_uuid'):
        return state['retained_gpu_uuid']
    previous=set()
    while True:
        try:
            current=idle_candidates(gpu_snapshot(),json.loads(PRIMARY.read_text()))
            stable=previous & current
            previous=current
            state.update(idle_uuids=sorted(current),stable_idle_uuids=sorted(stable))
        except Exception as error:
            previous,stable=set(),set();state['probe_error']=str(error)
        state['timestamp_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
        write_json(output,state)
        if stable:
            global KEEPER
            from lora_dora_study.retention import retain_gpu
            selected=sorted(stable)[0]
            try:KEEPER=retain_gpu(selected)
            except BlockingIOError:
                previous=set();time.sleep(10);continue
            state['retained_gpu_uuid']=selected
            write_json(output,state)
            return selected
        time.sleep(10)


def run_job(job,root,queue_state,queue_output):
    destination=root/'jobs'/job['id']
    destination.mkdir(parents=True,exist_ok=True)
    state_path=destination/'status.json'
    state=json.loads(state_path.read_text()) if state_path.exists() else dict(id=job['id'],completed=[])
    command_job=destination/'job.json'
    if job.get('impact_reference'):
        reference=json.loads((root/'jobs'/job['impact_reference']/'status.json').read_text())
        job=dict(job,impact_manifest=str(Path(reference['outputs']['full/dora'])/'intervention.json'))
    write_json(command_job,job)
    for phase,limit in [('smoke',2),('full',None)]:
        for role in job['roles']:
            key=phase+'/'+role
            if key in state['completed']:continue
            attempts=0
            while True:
                attempts+=1
                queue_state.update(status='waiting_for_gpu',job=job['id'],phase=phase,role=role)
                selected=await_gpu(queue_state,queue_output)
                output=destination/(phase+'-'+role+'-attempt-'+str(attempts))
                # Preserve all previous attempts after a manual restart.
                while output.exists():
                    attempts+=1;output=destination/(phase+'-'+role+'-attempt-'+str(attempts))
                command=[sys.executable,'scripts/held_gpu_worker.py','scripts/series_worker.py','--job',str(command_job),
                    '--gpu-uuid',selected,'--role',role,'--output-dir',str(output)]
                if limit:command.extend(['--limit',str(limit)])
                queue_state.update(status='running',gpu_uuid=selected,command=command)
                state.update(status='running',phase=phase,role=role,output_path=str(output))
                write_json(queue_output,queue_state);write_json(state_path,state)
                with output.with_suffix('.log').open('x') as log:
                    from lora_dora_study.retention import lease_fds
                    process=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT,pass_fds=lease_fds())
                    queue_state['worker_pid']=process.pid;write_json(queue_output,queue_state)
                    code=process.wait()
                if code==75:
                    raise RuntimeError('Assigned GPU guard refused; inspect conflict instead of waiting or switching cards')
                if code:
                    state.update(status='failed_needs_inspection',exit_code=code)
                    write_json(state_path,state);record('Ошибка '+job['id'],state)
                    return
                result=json.loads((output/'summary.json').read_text())
                if result['status']!='complete':raise RuntimeError('Worker returned incomplete results')
                state['completed'].append(key)
                state.setdefault('outputs',{})[key]=str(output)
                if phase=='full':
                    state.setdefault('measured_gpu_seconds',0)
                    state['measured_gpu_seconds']+=result['inference_seconds']
                write_json(state_path,state)
                record(job['id']+' / '+key,dict(path=str(output.resolve()),
                    **{k:result[k] for k in ['metrics','memory','inference_seconds','predictions_completed','full_evaluation','versions']}))
                break
    if len(job['roles'])==3:
        comparisons={right+'_minus_'+left:compare_runs(state['outputs']['full/'+left],state['outputs']['full/'+right])
            for left,right in [('base','lora'),('base','dora'),('lora','dora')]}
        adjusted=holm({contrast+':'+metric:result['paired_sign_permutation_p']
            for contrast,comparison in comparisons.items() for metric,result in comparison['metrics'].items()})
        write_json(destination/'matched-comparison.json',dict(contrasts=comparisons,holm_pvalues=adjusted))
    elif job['id']=='gsm8k-unmodified-dora':
        old=Path(json.loads((root/'jobs/gsm8k-quality-greedy/status.json').read_text())['outputs']['full/dora'])/'predictions.jsonl'
        new=Path(state['outputs']['full/dora'])/'predictions.jsonl'
        a=[json.loads(line) for line in old.read_text().splitlines()]
        b=[json.loads(line) for line in new.read_text().splitlines()]
        differences=sum(x['text']!=y['text'] or x['input_ids_sha256']!=y['input_ids_sha256'] for x,y in zip(a,b))
        write_json(destination/'noop-validation.json',dict(n=len(b),different_predictions=differences))
        if len(a)!=len(b) or differences:
            state.update(status='failed_needs_inspection',error='New evaluator no-op differs from original DoRA')
            write_json(state_path,state);record('No-op требует проверки',state);return
    elif job.get('intervention','none') not in {'none','dense_reference'}:
        reference=json.loads((root/'jobs'/job.get('reference_job','gsm8k-unmodified-dora')/'status.json').read_text())['outputs']['full/'+job.get('reference_role','dora')]
        write_json(destination/'matched-comparison.json',compare_runs(reference,state['outputs']['full/'+job['roles'][0]]))
    state['status']='complete';write_json(state_path,state)
    if job['id']=='gsm8k-quality-greedy':
        primary=json.loads(PRIMARY.read_text())
        primary.update(status='quality_complete_interventions_pending',corrected_quality_outputs=state['outputs'],
                       comparison_path=str(destination/'matched-comparison.json'))
        write_json(PRIMARY,primary)
    record('Эксперимент завершён '+job['id'],state)
    # Family correction is emitted only after every prespecified intervention is complete.
    with (root/'family-analysis.lock').open('a') as stream:
        fcntl.flock(stream,fcntl.LOCK_EX)
        jobs=[j for s in json.loads(PLAN_PATH.read_text())['series'] for j in s['jobs']
              if j.get('intervention','none') not in {'none','dense_reference'}]
        paths={j['id']:root/'jobs'/j['id'] for j in jobs}
        if jobs and all((p/'status.json').exists() and json.loads((p/'status.json').read_text())['status']=='complete'
                        for p in paths.values()):
            results={key:json.loads((path/'matched-comparison.json').read_text()) for key,path in paths.items()}
            corrected=holm({key+':'+metric:r['metrics'][metric]['paired_sign_permutation_p']
                            for key,r in results.items() for metric in r['metrics']})
            write_json(root/'intervention-family-holm.json',dict(contrasts=results,holm_pvalues=corrected,
                correction_family=list(paths),ci_note='CIs unadjusted; p values Holm corrected jointly over all interventions and both fixed scorers'))


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--series',type=int,choices=[1,2,3],required=True)
    p.add_argument('--plan',type=Path,default=Path('configs/two_series.json'))
    p.add_argument('--output-root',type=Path,default=Path('results/extra-series'))
    p.add_argument('--retained-gpu')
    args=p.parse_args()
    global PLAN_PATH
    PLAN_PATH=args.plan
    plan=json.loads(args.plan.read_text())
    selected_series=next(s for s in plan['series'] if s['series']==args.series)
    tasks=selected_series['jobs']
    args.output_root.mkdir(parents=True,exist_ok=True)
    output=args.output_root/('series-'+str(args.series)+'.json')
    lock=Path('/tmp')/('lora-dora-extra-series-'+str(os.getuid())+'-'+str(args.series)+'.lock')
    with lock.open('a') as stream:
        fcntl.flock(stream,fcntl.LOCK_EX|fcntl.LOCK_NB)
        state=dict(series=args.series,pid=os.getpid(),status='starting',interval_seconds=10,
            required_consecutive_checks=2,plan_sha256=sha256_file(args.plan),
            estimated_gpu_seconds=selected_series['estimated_gpu_seconds'])
        if args.retained_gpu:
            global KEEPER
            from lora_dora_study.retention import retain_gpu
            KEEPER=retain_gpu(args.retained_gpu)
            state['retained_gpu_uuid']=args.retained_gpu
        record('Очередь '+str(args.series)+' запущена',state)
        try:
            while True:
                waiting={};ready=[];finished=[];failed=[]
                for job in tasks:
                    path=args.output_root/'jobs'/job['id']/'status.json'
                    status=json.loads(path.read_text()).get('status') if path.exists() else None
                    if status=='complete':finished.append(job['id']);continue
                    if status=='failed_needs_inspection':failed.append(job['id']);continue
                    reason=dependency_reason(job,args.output_root)
                    if reason:waiting[job['id']]=reason
                    else:ready.append(job)
                state.update(status='queued',waiting=waiting,finished=finished,failed=failed,
                    ready=[j['id'] for j in ready],timestamp_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
                write_json(output,state)
                if ready:
                    run_job(ready[0],args.output_root,state,output)
                    continue
                if not waiting:
                    state['status']='complete' if not failed else 'completed_with_failures'
                    write_json(output,state);return
                state['status']='waiting_for_dependencies_or_implementation';write_json(output,state)
                time.sleep(10)
        except Exception as error:
            state.update(status='failed_needs_inspection',error=str(error));write_json(output,state)
            record('Очередь остановлена',state);raise


if __name__=='__main__':main()
