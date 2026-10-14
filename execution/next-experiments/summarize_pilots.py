#!/usr/bin/env python3
"""CPU-only pilot accounting and sensitivity forecasts; never launches work."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import statistics


def rows(path):
    return [json.loads(x) for x in path.read_text().split('\n') if x] if path.exists() else []


def extent(values):
    values = list(values)
    return [min(values), max(values)] if values else None


def quantiles(values):
    values = sorted(values)
    if not values:
        return None
    return {str(q): values[round((len(values)-1)*q)] for q in (0, .25, .5, .75, 1)}


def fit_forced(cases, reference):
    import numpy as np
    cases = [c for c in cases if c.get('forced_tokens') and not c.get('warmup')]
    if not cases or not reference:
        return {'available': False, 'reason': 'Forced timing or full reference missing'}
    # Enumerate active subsets: exact NNLS in two dimensions without SciPy.
    x = np.array([[c['generated_tokens'], c['generated_tokens']*c['input_tokens'] + c['generated_tokens']*(c['generated_tokens']-1)/2] for c in cases])
    y = np.array([c['seconds'] for c in cases])
    candidates = [np.zeros(2)]
    for count in (1, 2):
        for active in itertools.combinations(range(2), count):
            beta = np.linalg.lstsq(x[:, active], y, rcond=None)[0]
            if np.all(beta >= 0):
                full = np.zeros(2); full[list(active)] = beta; candidates.append(full)
    beta = min(candidates, key=lambda v: float(np.sum((x@v-y)**2)))
    fitted = x@beta
    ratios = y/fitted
    def total(cap=None):
        result = 0
        for c in reference:
            g = min(c['generated_tokens'], cap) if cap else c['generated_tokens']
            length = c['input_tokens']
            result += beta[0]*g+beta[1]*(g*length+g*(g-1)/2)
        return float(result)
    predicted = total()
    return dict(available=True, formula='t=a*G+b*(G*L+G*(G-1)/2)', nonnegative_coefficients=beta.tolist(),
        forced_observations=len(cases), forced_tokens=sorted({c['generated_tokens'] for c in cases}),
        prompt_tokens=sorted({c['input_tokens'] for c in cases}), residual_seconds_range=extent((y-fitted).tolist()),
        residual_rmse_seconds=float(np.sqrt(np.mean((y-fitted)**2))), observed_over_fitted_range=extent(ratios.tolist()),
        full_reference_cases=len(reference), full_inference_seconds=predicted,
        residual_scaled_seconds=[predicted*float(min(ratios)), predicted*float(max(ratios))],
        reference_generated_tokens=quantiles(c['generated_tokens'] for c in reference),
        all_cases_cap256_seconds=total(256),
        caveat='Uses original-condition lengths, which may change under intervention. 256-token cap extrapolates beyond the 128-token pilot. Residual range is descriptive, not a confidence interval; contention and calibration transfer add uncertainty.')


def summarize(directory, references):
    path = directory/'summary.json'
    s = json.loads(path.read_text())
    resources = rows(directory/'resources.jsonl')
    preload = s.get('preload_resources', {}).get('monotonic')
    def resource_range(group):
        return dict(samples=len(group), gpu_utilization_percent=extent(r['gpu'].get('utilization_percent', r['gpu'].get('utilization_gpu_percent', 0)) for r in group),
            gpu_used_mib=extent(r['gpu']['used_mib'] for r in group),
            other_pid_count=extent(len(r.get('other_processes', [])) for r in group),
            other_memory_mib=extent(sum(float(p.get('memory_mib', 0)) if str(p.get('memory_mib', 0)).replace('.', '', 1).isdigit() else 0 for p in r.get('other_processes', [])) for r in group))
    good = [r for r in resources if 'gpu' in r]
    cases = rows(directory/'predictions.jsonl')
    forced = rows(directory/'length-timing.jsonl')
    timing_keys = ['wall_seconds', 'tokenizer_load_seconds', 'base_load_seconds', 'adapter_load_seconds', 'intervention_seconds', 'control_setup_seconds', 'reference_forward_seconds', 'calibration_train_seconds', 'calibration_validation_seconds', 'inference_seconds']
    result = dict(path=str(directory), task=s['task'], mode=s['mode'], condition=s['condition'], status=s['status'],
        errors={k: s[k] for k in ('error_type', 'error', 'resource_sampler_error') if s.get(k)},
        timing_seconds={k: s[k] for k in timing_keys if k in s}, memory=s.get('memory', s.get('load_memory')),
        baseline=resource_range([r for r in good if preload is not None and r['monotonic'] <= preload]),
        while_running=resource_range([r for r in good if preload is not None and r['monotonic'] > preload]),
        predictions=len(cases), forced_timing_cases=len(forced), selected_indices=s.get('selected_indices'),
        pilot_prompt_tokens=quantiles(c['input_tokens'] for c in cases), pilot_generated_tokens=quantiles(c['generated_tokens'] for c in cases),
        full_reference_prompt_tokens=quantiles(c['input_tokens'] for c in references.get(s['task'], {}).get('rows', [])),
        full_reference_generated_tokens=quantiles(c['generated_tokens'] for c in references.get(s['task'], {}).get('rows', [])),
        full_reference=references.get(s['task'], {}).get('path'),
        reference_sha256=references.get(s['task'], {}).get('sha256'),
        builtin_forecast=s.get('forecast'))
    if s['mode'] == 'controls':
        result['forced_fit'] = fit_forced(forced, references.get(s['task'], {}).get('rows', []))
    if s['mode'] == 'nll' and 'nll' in s:
        nll = s['nll']; per_segment = [r['elapsed_seconds'] for r in nll['per_segment']]
        count = s['nll_full_corpus_segment_count']
        result['nll'] = dict(pilot_segments=nll['segment_count'], full_segments=count, elapsed_seconds=nll['elapsed_seconds'],
            warmup_seconds=nll['warmup_elapsed_seconds'], per_segment_seconds=per_segment,
            forecast_inference_seconds=count*statistics.mean(per_segment),
            segment_range_scaled_seconds=[count*min(per_segment), count*max(per_segment)])
    return result


def markdown(report):
    lines = ['# A/B/C short pilot timing', '', 'Technical pilots only. No full run or queued continuation. Timings are measured shared-GPU wall time; forecasts are sensitivity scenarios, not confidence intervals. Native original response lengths may change after intervention.', '',
        'GPU utilization belongs to the whole device and cannot isolate foreign compute. Other PID counts and memory describe memory occupancy only. The running interval includes load/setup, not solely inference.', '',
        f"Attempts: {len(report['attempts'])}; completed: {report['completed_count']}; failed/refused/exhausted: {report['failure_count']}; incomplete: {report['incomplete_count']}.", '',
        '| Attempt | Status | Wall s | Load s | Calibration s | Inference s | Peak allocated/reserved GiB | RSS GiB |', '|---|---|---:|---:|---:|---:|---:|---:|']
    for a in report['attempts']:
        t=a['timing_seconds']; m=a.get('memory') or {}
        load=sum(t.get(k, 0) for k in ('tokenizer_load_seconds','base_load_seconds','adapter_load_seconds'))
        cal=sum(t.get(k, 0) for k in ('calibration_train_seconds','calibration_validation_seconds'))
        inf=t.get('inference_seconds', a.get('nll',{}).get('elapsed_seconds',0))
        lines.append(f"| {Path(a['path']).name} | {a['status']} | {t.get('wall_seconds', 0):.2f} | {load:.2f} | {cal:.2f} | {inf:.2f} | {m.get('peak_allocated_bytes',0)/2**30:.2f}/{m.get('peak_reserved_bytes',0)/2**30:.2f} | {m.get('max_process_rss_bytes',0)/2**30:.2f} |")
    lines += ['', 'All attempt paths, errors, phase timings, sample length quantiles, baseline/running occupancy ranges and reference provenance are recorded in the companion JSON. Incomplete attempts have no forecast claim.', '']
    for a in report['attempts']:
        lines += [f"## {Path(a['path']).name}", '', f"Output: `{a['path']}`.", '']
        if a['errors']: lines += [f"Errors: `{json.dumps(a['errors'], ensure_ascii=False)}`", '']
        lines += [f"Baseline: `{json.dumps(a['baseline'])}`; while running: `{json.dumps(a['while_running'])}`.", '']
        if a['status'] != 'complete': continue
        fit=a.get('forced_fit', {})
        if fit.get('available'):
            low, high=fit['residual_scaled_seconds']
            lines += [f"A forced-only nonnegative fit: {fit['full_inference_seconds']/3600:.2f} h inference over {fit['full_reference_cases']} original reference cases; residual-scaled {low/3600:.2f}–{high/3600:.2f} h. Coefficients a,b={fit['nonnegative_coefficients']}; RMSE {fit['residual_rmse_seconds']:.3f} s. {fit['caveat']}", '']
        if a['mode']=='remove_d' and a.get('builtin_forecast',{}).get('available'):
            for name in ('per_token_constant','sequence_linear','attention_quadratic'):
                f=a['builtin_forecast']['scenarios'][name]
                lines += [f"B {name}: {f['median_seconds']/3600:.2f} h inference; observed-rate range {f['low_seconds']/3600:.2f}–{f['high_seconds']/3600:.2f} h."]
            lines += ['', 'Use sequence-linear/per-token scenarios as the principal timing range. Attention-quadratic is an aggressive sensitivity scenario and is not a credible central forecast when it becomes huge; small prompt samples cannot fit that law reliably.', '']
        if 'nll' in a:
            f=a['nll']; low,high=f['segment_range_scaled_seconds']
            lines += [f"C {a['condition']}: {f['forecast_inference_seconds']:.2f} s inference for the actual {f['full_segments']} fixed segments, from {f['pilot_segments']} measured segments; per-segment range scaled to full corpus {low:.2f}–{high:.2f} s. Load and warmup are additional.", '']
    lines += ['A full calibration uses at least 200/32 train/validation cases versus 16/8 here; pilot calibration timing and quality do not establish full transfer. Load/setup/calibration must be added to inference forecasts. Shared-GPU contention and changed generated lengths can move full costs outside these ranges.', '', 'Fresh final GPU snapshot: ' + (f"`{report['fresh_gpu_snapshot']}`" if report.get('fresh_gpu_snapshot') else 'pending; this report is provisional.'), '']
    return '\n'.join(lines)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--pilot-root', type=Path, required=True)
    p.add_argument('--reference', action='append', default=[], help='task=/absolute/predictions.jsonl')
    p.add_argument('--output-json', type=Path, required=True)
    p.add_argument('--output-md', type=Path, required=True)
    p.add_argument('--fresh-gpu-snapshot')
    a=p.parse_args(); refs={}
    for value in a.reference:
        task,path=value.split('=',1); path=Path(path)
        refs[task]={'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'rows':rows(path)}
    attempts=[summarize(path.parent,refs) for path in sorted(a.pilot_root.glob('*/summary.json'))]
    failures=[r for r in attempts if r['status'] not in ('starting','running','complete')]
    report=dict(pilot_root=str(a.pilot_root), attempts=attempts, completed_count=sum(r['status']=='complete' for r in attempts),
        failure_count=len(failures), incomplete_count=sum(r['status'] in ('starting','running') for r in attempts), fresh_gpu_snapshot=a.fresh_gpu_snapshot)
    a.output_json.write_text(json.dumps(report, indent=2)+'\n'); a.output_md.write_text(markdown(report))
    print(json.dumps({k:v for k,v in report.items() if k!='attempts'}))


if __name__ == '__main__':
    main()
