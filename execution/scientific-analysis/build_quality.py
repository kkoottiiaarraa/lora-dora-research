#!/usr/bin/env python3
"""Read-only CPU analysis of immutable saved quality evidence; no model imports.

Inputs: immutable bundle tables/manifests and exact accepted raw paths.
Estimands: saved baseline contrasts and dense minus original quality only.
Output fractions retain original precision; all historical tests are copied.
"""
import argparse, collections, csv, datetime, hashlib, html, json, os
from pathlib import Path
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='2'


def sha(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):
            h.update(block)
    return h.hexdigest()


def load(path):
    with open(path) as f:
        return json.load(f)


def table(path):
    with open(path,newline='') as f:
        return list(csv.DictReader(f))


def write_csv(path, rows):
    fields=list(dict.fromkeys(k for row in rows for k in row))
    with open(path,'w',newline='') as f:
        w=csv.DictWriter(f,fields); w.writeheader(); w.writerows(rows)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--repo',type=Path,default=Path('./artifacts'))
    ap.add_argument('--out',type=Path)
    a=ap.parse_args(); repo=a.repo
    bundle=repo/'docs/analysis-preparation/2026-10-11'
    out=a.out or repo/'docs/analysis/2026-10-11/results'
    out.mkdir(parents=True,exist_ok=True)
    checks=[]; input_hashes={}
    def check(name, passed, **details):
        checks.append(dict(name=name,passed=bool(passed),**details))
        if not passed:
            raise ValueError((name,details))
    def hash_check(path, expected, scope):
        path=Path(path); actual=sha(path); input_hashes[str(path)]=actual
        check('sha256',actual==expected,path=str(path),scope=scope,sha256=actual)
    # The immutable manifest also includes historical MEMORY/AGENTS and extractors.
    # Verify everything read-only; no historical verifier is invoked.
    manifest=load(bundle/'manifests/bundle.json')
    for entry in manifest['files']:
        hash_check(repo/entry['path'],entry['sha256'],'immutable_bundle_snapshot')
    for name in ['01-corpus-quality/manifests/export.json',
                 '02-interventions/manifests/export.json',
                 '03-diagnostics/manifests/hashes.json']:
        entries=load(bundle/name)['inputs']
        if isinstance(entries,dict):
            entries=[dict(path=k,sha256=(v['sha256'] if isinstance(v,dict) else v)) for k,v in entries.items()]
        for entry in entries:
            path=entry['path']
            if path not in input_hashes:
                hash_check(path,entry['sha256'],'original_source_manifest')
            else:
                check('consistent_manifest_hash',input_hashes[path]==entry['sha256'],path=path)
    integrity=load(bundle/'01-corpus-quality/validation/integrity.json')
    iv=load(bundle/'02-interventions/validation/checks.json')
    check('saved_integrity',integrity['passed'] and all(x['passed'] for x in integrity['checks']))
    check('saved_interventions',iv['status']=='passed')
    def t(part,name):return table(bundle/part/'tables'/f'{name}.csv')
    inventory=t('01-corpus-quality','run_inventory')
    baseline=t('01-corpus-quality','baseline_metrics')
    contrasts=t('01-corpus-quality','baseline_contrasts')
    subjects=t('01-corpus-quality','mmlu_subject_metrics')
    strata=t('01-corpus-quality','squadv2_answerability')
    transitions=t('02-interventions','paired_transitions')
    im=t('02-interventions','intervention_metrics')
    nc=t('02-interventions','numerical_control_contrasts')
    fidelity=t('03-diagnostics','numerical_fidelity')
    check('accepted_count',len(inventory)==29,accepted_runs=len(inventory))
    check('baseline_count',len(baseline)==15 and len({r['run_id'] for r in baseline})==9)
    check('baseline_contrast_count',len(contrasts)==15)
    # Retain compact raw rows only in memory on the research server. Texts are
    # hashed for transitions; no raw texts/predictions go to outputs or the VM.
    runs={}; limits=[]
    for item in inventory:
        rid=item['run_id']; sm=load(item['summary_path']); rows=[]
        status=load(item['status_path']); accepted=status['outputs']['full/'+item['role']]
        accepted=Path(accepted) if Path(accepted).is_absolute() else repo/accepted
        check('accepted_path',accepted==Path(item['summary_path']).parent,run_id=rid)
        with open(item['predictions_path']) as f:
            for line in f:
                row=json.loads(line)
                row['text_hash']=hashlib.sha256(row.pop('text').encode()).hexdigest()
                rows.append(row)
        n=len(rows)
        check('complete_and_indices',sm['status']=='complete' and sm['full_evaluation'] is True
              and n==int(item['rows'])==int(item['expected_rows'])==sm['predictions_completed']
              and [r['test_row_index'] for r in rows]==list(range(n)),run_id=rid,n=n)
        check('prediction_summary_hash',input_hashes[item['predictions_path']]==sm['predictions_sha256'],run_id=rid)
        for metric,mean in sm['metrics'].items():
            check('raw_mean',abs(sum(r['metrics'][metric] for r in rows)/n-mean)<1e-12,run_id=rid,metric=metric)
        runs[rid]=(sm,rows)
        if item['intervention']=='none':
            limits.append(dict(run_id=rid,task=item['task'],role=item['role'],n=n,
                               max_input_tokens=sm['dataset']['max_input_tokens'],
                               max_new_tokens=sm['generation_config']['max_new_tokens'],
                               hit_token_limit=sum(bool(r['hit_token_limit']) for r in rows),
                               prompt_truncated=sum(bool(r['prompt_truncated']) for r in rows)))
            check('raw_token_limits',limits[-1]['hit_token_limit']==sm['hit_token_limit']
                  and limits[-1]['prompt_truncated']==sm['truncated_prompts'],run_id=rid)
    def aligned(lid,rid):
        ls,L=runs[lid]; rs,R=runs[rid]
        fields=('test_row_index','source_id','prompt_sha256','input_ids_sha256')
        good=len(L)==len(R) and all(all(x.get(k) is not None and x[k]==y.get(k) for k in fields) for x,y in zip(L,R))
        good=good and all(ls[k]==rs[k] for k in ('dataset','generation_config','versions','source_sha256'))
        check('raw_pair_alignment',good,left_run=lid,right_run=rid,n=len(L))
        return L,R
    for row in t('01-corpus-quality','comparability'):
        aligned(row['left_run'],row['right_run'])
    for row in baseline:
        sm,_=runs[row['run_id']]
        check('baseline_literal_mean',float(row['original_score'])==sm['metrics'][row['metric']])
    for row in contrasts:
        saved=load(row['source_path']);stat=saved['contrasts'][row['contrast']]['metrics'][row['metric']]
        for col,key in [('difference','difference'),('raw_p','paired_sign_permutation_p'),('n','n'),('resamples','resamples'),('seed','seed')]:
            check('historical_baseline_literal',float(row[col])==stat[key],metric=row['metric'],field=col)
        check('historical_baseline_ci',list(map(float,[row['ci95_low'],row['ci95_high']]))==stat['ci95'])
        check('historical_baseline_holm',float(row['holm_p'])==saved['holm_pvalues'][row['contrast']+':'+row['metric']]
              and int(row['family_size'])==len(saved['holm_pvalues']))
    # Independently reproduce descriptive stratified metrics; no new tests.
    for row in subjects:
        _,rows=runs[row['run_id']];groups=collections.defaultdict(list)
        for x in rows:groups[x['subject']].append(x['metrics']['accuracy'])
        if row['aggregation']=='subject': vals=groups[row['subject']]; mean=sum(vals)/len(vals)
        elif row['aggregation']=='micro':mean=sum(x['metrics']['accuracy'] for x in rows)/len(rows)
        else:mean=sum(sum(v)/len(v) for v in groups.values())/len(groups)
        check('mmlu_descriptive_reproduction',abs(mean-float(row['mean']))<1e-12)
    dataset_path=Path(strata[0]['source_path'])
    with open(dataset_path) as f:labels={x['test_row_index']:(bool(x['answers']['text']),x['id']) for x in map(json.loads,f)}
    for row in strata:
        _,rows=runs[row['run_id']]
        check('strata_source_alignment',all(labels[x['test_row_index']][1]==x['source_id'] for x in rows))
        subset=[x for x in rows if labels[x['test_row_index']][0]==(row['answerability']=='answerable')]
        mean=sum(x['metrics'][row['metric']] for x in subset)/len(subset)
        check('squad_strata_reproduction',len(subset)==int(row['n']) and abs(mean-float(row['mean']))<1e-12)
    controls=[]
    for row in im:
        if row['job_id'] not in ('gsm8k-dense-dora','gsm8k-dense-lora'):continue
        role=row['job_id'].split('-')[-1]; rid=row['job_id']+'/'+role; lid=row['actual_reference']
        L,R=aligned(lid,rid);metric=row['metric'];n=len(L)
        lm=sum(x['metrics'][metric] for x in L)/n;rm=sum(x['metrics'][metric] for x in R)/n
        check('dense_saved_means_difference',abs(lm-float(row['left_mean']))<1e-12 and abs(rm-float(row['right_mean']))<1e-12 and abs(rm-lm-float(row['difference']))<1e-12)
        tr=next(x for x in transitions if x['job_id']==row['job_id'] and x['metric']==metric)
        counts=collections.Counter((int(x['metrics'][metric]),int(y['metrics'][metric])) for x,y in zip(L,R))
        for col,pair in [('correct_to_correct',(1,1)),('correct_to_wrong',(1,0)),('wrong_to_correct',(0,1)),('wrong_to_wrong',(0,0))]:
            check('dense_transition_reproduction',counts[pair]==int(tr[col]),field=col,job=row['job_id'],metric=metric)
        changes=sum(x['text_hash']!=y['text_hash'] for x,y in zip(L,R))
        check('dense_text_changes',changes==int(tr['generated_text_changes']))
        numerical=next(x for x in nc if x['job_id']==row['job_id'] and x['metric']==metric)
        check('dense_control_exact_reference',numerical['reference']==lid and numerical['status']=='existing_exact_pair')
        f=next(x for x in fidelity if x['job']==row['job_id'])
        intervention=load(f['source']);saved=load(Path(row['right_path']).parent/'matched-comparison.json')
        fam_path=Path('./artifacts')/row['family']; family=load(fam_path)
        check('dense_literal_statistics',all(float(row[col])==saved['metrics'][metric][key] for col,key in [('existing_raw_p','paired_sign_permutation_p')])
              and [float(row['existing_ci95_low']),float(row['existing_ci95_high'])]==saved['metrics'][metric]['ci95']
              and float(row['existing_holm_p'])==family['holm_pvalues'][row['job_id']+':'+metric])
        controls.append(dict(row,reference_run=lid,intervention_run=rid,
                             **{k:tr[k] for k in ['correct_to_correct','correct_to_wrong','wrong_to_correct','wrong_to_wrong','generated_text_changes']},
                             correction_family_path=str(fam_path),
                             contrast_source_path=str(Path(row['right_path']).parent/'matched-comparison.json'),
                             **{'fidelity_'+k:f[k] for k in ['max_abs_logits_error','argmax_agreement','dtype','dtype_missing_reason','source']},
                             fidelity_stage='original PEFT to dense conversion, before subsequent rank/energy changes',
                             fidelity_reference=f['reference'],fidelity_calibration_prompts=1,
                             fidelity_calibration_tokens=intervention['calibration_tokens'],
                             fidelity_calibration_source=intervention['calibration_source'],
                             answer_exact_identity_claim='not established',ci_scope='pointwise paired examples conditional on fixed checkpoints; no training-seed uncertainty'))
    check('dense_control_rows',len(controls)==4)
    overview=[]
    for row in baseline:
        lim=next(x for x in limits if x['run_id']==row['run_id'])
        overview.append(dict(row_type='baseline_mean',**row,mean=row['original_score'],aggregation='micro_examples',
                             **{k:lim[k] for k in ['max_input_tokens','max_new_tokens','hit_token_limit','prompt_truncated']},
                             ci_scope='descriptive mean; no new CI/test'))
    means={(x['run_id'],x['metric']):x['original_score'] for x in baseline}
    for row in contrasts:
        task=next(x['task'] for x in baseline if x['run_id']==row['left_run'])
        overview.append(dict(row_type='saved_baseline_contrast',**row,task=task,
                             left_mean=means[row['left_run'],row['metric']],right_mean=means[row['right_run'],row['metric']],
                             ci_scope='historical pointwise paired examples conditional on fixed checkpoints; not training seeds',
                             p_method='historical paired_sign_permutation_p; copied, no new baseline tests'))
    for row in subjects:
        overview.append(dict(row_type='mmlu_descriptive',task='mmlu',**row,source_path=str(bundle/'01-corpus-quality/tables/mmlu_subject_metrics.csv'),ci_scope='descriptive; subjects are not independent trained models'))
    for row in strata:
        overview.append(dict(row_type='squad_answerability_descriptive',task='squadv2',**row,aggregation='answerability_stratum',ci_scope='descriptive; no subgroup CI/test'))
    write_csv(out/'quality-overview.csv',overview)
    write_csv(out/'numerical-controls.csv',controls)
    draw_svg(out/'quality-and-controls.svg',contrasts,controls)
    findings=make_findings(contrasts,baseline,subjects,strata,controls,limits)
    (out/'quality-findings.md').write_text(findings)
    report=dict(passed=True,created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                method='read-only hash/alignment and saved-score reproduction; no new baseline tests',
                plan_sha256=sha(repo/'docs/analysis/2026-10-11/PLAN.md'),
                spec_sha256=sha(repo/'docs/analysis/2026-10-11/EXECUTION_SPEC.md'),
                code_sha256=sha(__file__),input_hashes=input_hashes,checks=checks,
                accepted_runs=29,baseline_runs=9,baseline_metric_contrasts=15,dense_scorer_rows=4,
                quality_overview_rows=len(overview),token_limits_all_baselines=limits,
                compression_gate='pass conditional on dense references; PEFT/dense functional identity not established',
                immutable_sources_modified=False,
                outputs={p.name:dict(sha256=sha(p),bytes=p.stat().st_size) for p in out.glob('*') if p.name in ['quality-overview.csv','numerical-controls.csv','quality-and-controls.svg','quality-findings.md']})
    (out/'quality-validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['passed','accepted_runs','baseline_metric_contrasts','dense_scorer_rows','quality_overview_rows','compression_gate']}))


def draw_svg(path, contrasts, controls):
    # Dependency-free scientific SVG because matplotlib is absent in the frozen
    # venv and the execution spec prohibits installing dependencies.
    rows=[(r['job'].replace('shadow_4b_','').replace('-quality-greedy','')+' '+r['metric'],r['difference'],r['ci95_low'],r['ci95_high']) for r in contrasts if r['contrast']=='dora_minus_lora']
    rows += [(r['job_id']+' '+r['metric'],r['difference'],r['existing_ci95_low'],r['existing_ci95_high']) for r in controls]
    parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="620" viewBox="0 0 1200 620">',
           '<rect width="1200" height="620" fill="white"/>','<g font-family="sans-serif" font-size="14" fill="#15202b">',
           '<text x="30" y="30" font-size="20">Fixed-checkpoint quality contrasts and dense conversion controls</text>',
           '<text x="30" y="55">Historical pointwise paired-example CI95; no training-seed uncertainty</text>']
    def x(value):return 650+float(value)*100*75
    for tick in [-2,-1,0,1,2,3]:
        xx=x(tick/100);parts.append(f'<line x1="{xx}" x2="{xx}" y1="85" y2="490" stroke="#dddddd"/><text x="{xx-8}" y="515">{tick}</text>')
    parts.append(f'<line x1="650" x2="650" y1="85" y2="490" stroke="#333"/>')
    for i,(label,value,lo,hi) in enumerate(rows):
        yy=105+i*42;color='#2364aa' if i<5 else '#a45a16'
        parts.extend([f'<text x="30" y="{yy+5}">{html.escape(label)}</text>',
                      f'<line x1="{x(lo)}" x2="{x(hi)}" y1="{yy}" y2="{yy}" stroke="{color}" stroke-width="2"/>',
                      f'<circle cx="{x(value)}" cy="{yy}" r="4" fill="{color}"/>',
                      f'<text x="885" y="{yy+5}" font-size="12">{float(value)*100:+.3f} [{float(lo)*100:+.3f}, {float(hi)*100:+.3f}]</text>'])
    parts.extend(['<text x="465" y="550">Difference in percentage points (right minus left)</text>',
                  '<text x="30" y="580">Blue: DoRA − LoRA. Brown: dense − original corresponding adapter. Means and all 15 contrasts in quality-overview.csv.</text>',
                  '<text x="30" y="604">Historical Holm families: baseline 3/6/6 metric hypotheses; dense 16 metric hypotheses. CI are unadjusted.</text>','</g></svg>'])
    path.write_text('\n'.join(parts)+'\n')


def make_findings(contrasts, baseline, subjects, strata, controls, limits):
    lines=['# Качество и численные контроли — пакет Q','',
           'Анализ exploratory: план составлен после сбора результатов. Все оценки относятся к сохранённым task-specific checkpoints Qwen3-4B, одной паре обучения на задачу. Все 29 принятых runs, 15 baseline metric contrasts и четыре dense/scorer comparisons проверены. Исходные hashes, accepted paths, полнота, provenance и парность проверены read-only; старый bundle не изменён. Новые baseline tests/CI не вычислялись.','',
           '## Базовое качество','',
           '| Задача/метрика | Base, % | LoRA, % | DoRA, % | DoRA−LoRA, п.п. | Исторический CI95, п.п. | Holm p |',
           '|---|---:|---:|---:|---:|---:|---:|']
    for r in contrasts:
        if r['contrast']!='dora_minus_lora':continue
        job=r['job'];m=r['metric']; vals={x['role']:float(x['original_score'])*100 for x in baseline if x['run_id'].split('/')[0]==job and x['metric']==m}
        lines.append(f"| {job}/{m} | {vals['base']:.4f} | {vals['lora']:.4f} | {vals['dora']:.4f} | {float(r['difference'])*100:+.4f} | [{float(r['ci95_low'])*100:+.4f}, {float(r['ci95_high'])*100:+.4f}] | {r['holm_p']} |")
    lines += ['', 'Ни один сохранённый CI DoRA−LoRA не исключает ноль. Это не доказательство равенства и не установление отсутствия эффекта. По GSM8K точечная разница положительна, по MMLU почти нулевая, по SQuADv2 отрицательна; уверенного общего преимущества DoRA этими данными не установлено. Обе адаптации лучше base по всем сохранённым baseline contrasts, но величина GSM8K адаптация−base резко зависит от scorer и лимита генерации.', '',
              'CI — исторические percentile paired-example bootstrap, B=10000, seed=42, без одновременной поправки. p сохранены из paired_sign_permutation_p, Holm точно внутри исходных файлов: MMLU 3 metric hypotheses, GSM8K 6, SQuADv2 6. Это не общая семья всех задач/исследовательского поиска. Интервалы не охватывают независимые обучения, seed, выбор гиперпараметров или выбор checkpoint.', '',
              '## Scorer, лимиты и описательные разбиения', '',
              'GSM8K author scorer использует особый fallback первого числа; final scorer — альтернативное извлечение последнего числа. У base они расходятся на 846/1319 ответах (836 final-only correct и 10 author-only correct); у каждой адаптации на 3/1319. Поэтому 1.213% base author EM нельзя интерпретировать как чистое отсутствие арифметической способности. Результат final EM 63.836% тоже относится к тому же ограниченному greedy протоколу, а не к произвольной настройке генерации.', '',
              '| Run | Input cap | New-token cap | Hit cap / n | Truncated prompts / n |','|---|---:|---:|---:|---:|']
    for r in limits:lines.append(f"| {r['run_id']} | {r['max_input_tokens']} | {r['max_new_tokens']} | {r['hit_token_limit']}/{r['n']} | {r['prompt_truncated']}/{r['n']} |")
    lines += ['', 'Лимит не является рандомизированным фактором: из различий частот нельзя вывести причинный эффект truncation. Нельзя переносить эти оценки на увеличенный контекст/генерацию. Никаких условных тестов по hitting-cap группам не выполнялось.', '', '| MMLU role | micro, % | unweighted macro по 57 subjects, % |','|---|---:|---:|']
    for role in ['base','lora','dora']:
        d={r['aggregation']:float(r['mean'])*100 for r in subjects if r['role']==role and r['aggregation']!='subject'}
        lines.append(f"| {role} | {d['micro']:.4f} | {d['macro_unweighted_subjects']:.4f} |")
    lines += ['', 'Все 171 subject means представлены в quality-overview.csv, без новых p/CI и выбора «успешных» subjects. Subject macro равновесит subjects; micro взвешивает примеры. Subjects не являются независимыми обученными моделями.', '',
              '| SQuADv2 stratum / metric | n | Base, % | LoRA, % | DoRA, % | DoRA−LoRA, п.п. |','|---|---:|---:|---:|---:|---:|']
    for group in ['answerable','unanswerable']:
        for metric in ['exact','f1']:
            rs=[r for r in strata if r['answerability']==group and r['metric']==metric];v={r['role']:float(r['mean'])*100 for r in rs}
            lines.append(f"| {group}/{metric} | {rs[0]['n']} | {v['base']:.4f} | {v['lora']:.4f} | {v['dora']:.4f} | {v['dora']-v['lora']:+.4f} |")
    lines += ['', 'Answerability задана исходным answers.text, не результатом модели. Разбиения описательные, без subgroup tests или причинных объяснений. DoRA−LoRA exact положительна на answerable (+0.3711 п.п.), отрицательна на unanswerable (−0.6392 п.п.); итог зависит от состава evaluation set. Три task-specific пары не устанавливают универсализацию на архитектуры и задачи.', '',
              '## Численные контроли и переход к компрессии','',
              '| Dense control / scorer | Δ, п.п. | CI95, п.п. | Исправлено | Сломано | Changed text /1319 |','|---|---:|---:|---:|---:|---:|']
    for r in controls:
        lines.append(f"| {r['job_id']}/{r['metric']} | {float(r['difference'])*100:+.4f} | [{float(r['existing_ci95_low'])*100:+.4f}, {float(r['existing_ci95_high'])*100:+.4f}] | {r['wrong_to_correct']} | {r['correct_to_wrong']} | {r['generated_text_changes']} |")
    lines += ['', 'Исторические dense p/CI скопированы только для точной пары dense−соответствующий исходный PEFT. Семья intervention-family-holm.json: 8 contrasts ×2 scorers =16 гипотез. Все четыре CI включают ноль; это не equivalence. Различия ответов и ненулевые logits errors исключают утверждение подтверждённой функциональной идентичности.', '',
              'Dense DoRA: max abs logits error 1.34375; dense LoRA: 1.578125; argmax agreement каждого 0.9814814925. Эти числа относятся к original-adapter→dense проверке на одном calibration prompt/54 input positions, не к полному test set, не к autoregressive sequence agreement, не к изменённому rank32/E95/E99 решению. dtype в fidelity summary явно не записан; BF16 provenance полного evaluator не подменяет эту отсутствующую запись. Source paths и этапы имеются в numerical-controls.csv.', '',
              '**Gate к компрессии: условно пройден.** Integrity/provenance совместимы, dense references известны. Downstream rank/energy comparisons следует оценивать относительно сохранённой dense DoRA; matched-LoRA — относительно dense LoRA. Автоматический перенос результата на исходный PEFT checkpoint и использование pre-intervention fidelity как fidelity сжатого решения запрещены. CI dense DoRA допускает ухудшение около 1.59–1.74 п.п.; это существенная неопределённость для утверждения о сохранении исходного качества. Номинальный нулевой тест не устанавливает noninferiority.', '',
              '## Пределы происхождения и воспроизведение','',
              'Проверены точные pinned evaluation revisions и hashes сохранённых inputs. Они не восстанавливают неизвестные training revisions/seeds, оптимизаторные траектории, обучение и выбор гиперпараметров. Quantization отсутствует как явное поле summaries; неизвестное не превращено в подтверждённый факт. Независимых training repeats нет. Финальные checkpoints и posthoc вмешательства не идентифицируют причину различий во время обучения.', '',
              '`quality-overview.csv` содержит исходные fraction values, все 15 contrasts с точными историческими references/families и описательные means. `numerical-controls.csv` содержит 4 dense rows с transitions и fidelity source. `quality-validation.json` связывает read-only input hashes, код, PLAN/SPEC и outputs. SVG показывает только DoRA−LoRA и dense controls; полный набор таблицы не отобран по значимости.', '',
              'CPU на compute-host, максимум два потока; только stdlib, без новых зависимостей, GPU/forward/SVD. Frozen venv не имеет matplotlib; SVG построен непосредственно средствами stdlib, с явными осями, единицами и pointwise CI.', '',
              '```bash','OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 ./artifacts ./artifacts','```','']
    return '\n'.join(lines)

if __name__=='__main__':main()
