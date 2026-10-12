#!/usr/bin/env python3
"""Streaming, CPU-only endpoint diagnostics. No model loading/forward or SVD."""
import os
os.environ['CUDA_VISIBLE_DEVICES'] = ''
for _k in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[_k] = '2'
import argparse
import csv
import gzip
import hashlib
import inspect
import json
import math
from pathlib import Path
import resource
import sys
import time
import platform
import numpy as np
import torch
import peft
from safetensors import safe_open
from peft.tuners.lora.dora import DoraLinearLayer

torch.set_num_threads(2)
torch.set_num_interop_threads(2)
START = time.perf_counter()
CHECKS = []
QUANTILES = [('min', 0), ('median', .5), ('p90', .9), ('p99', .99), ('max', 1)]


def check(name, condition, detail=None):
    CHECKS.append(dict(name=name, pass_=bool(condition), detail=detail))
    if not condition:
        raise ValueError(f'Validation failed: {name}: {detail}')


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while block := f.read(8 * 1024 * 1024):
            h.update(block)
    return h.hexdigest()


def dump(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def ss(x):
    return float(torch.sum(x.double().square()).item())


def dot(x, y):
    return float(torch.sum(x.double() * y.double()).item())


def ratio(a, b):
    return math.sqrt(a / b) if b > 0 else None


def valid_norm(n):
    if not bool(torch.all(torch.isfinite(n) & (n > 0))):
        raise ValueError('Zero or nonfinite denominator norm; no clamp allowed')


def describe(x, prefix):
    x = np.asarray(x, dtype=np.float64)
    return {prefix + '_' + k: float(np.quantile(x, q)) for k, q in QUANTILES}


def surrogate(W, A, B, m):
    # Exactly the weight-normalization operation order in installed PEFT;
    # CPU BF16 kernels differ from historical CUDA kernels.
    with torch.autocast('cpu', dtype=torch.bfloat16):
        eye = torch.eye(A.shape[1], dtype=torch.float32)
        a = torch.nn.functional.linear(eye, A)
        lid = torch.nn.functional.linear(a, B).T
        us = W.float() + lid
        ns = torch.linalg.norm(us, dim=1).to(us.dtype)
        gs = m / ns
    valid_norm(ns)
    return us, ns, gs, dict(eye=str(eye.dtype), identity_A=str(a.dtype),
                           identity_B=str(lid.dtype), base=str(W.dtype),
                           addition=str(us.dtype), norm=str(ns.dtype),
                           magnitude=str(m.dtype), quotient=str(gs.dtype))


def toy_tests():
    w = torch.tensor([[3., 4.], [0., 2.]], dtype=torch.float32)
    l = torch.tensor([[.1, -.2], [.3, .4]])
    u = w + l
    n = torch.linalg.norm(u, dim=1)
    m = n.clone()
    check('toy g=1 makes R zero', ss((m / n - 1)[:, None] * u) == 0)
    bn = torch.linalg.norm(w, dim=1)
    check('toy L=0 and m=baseNorm makes Delta zero', ss((bn / bn)[:, None] * w - w) == 0)
    g = torch.tensor([2., .5])
    check('toy known g scales row norms', torch.allclose(torch.linalg.norm(g[:, None] * u, dim=1), g * n))
    one = torch.tensor(1., dtype=torch.bfloat16)
    prev = torch.nextafter(one, torch.tensor(0., dtype=torch.bfloat16)).item()
    nex = torch.nextafter(one, torch.tensor(2., dtype=torch.bfloat16)).item()
    points = torch.tensor([1 - (1-prev)*.49, 1 - (1-prev)*.51,
                           1 + (nex-1)*.49, 1 + (nex-1)*.51])
    check('toy asymmetric BF16 rounding below/above midpoints', points.to(torch.bfloat16).tolist() == [1., prev, 1., nex])
    check('toy weighted norm differs from mean of module ratios',
          math.isclose(ratio(1+9, 1+81), math.sqrt(10/82)) and not math.isclose(ratio(10,82), (1+1/3)/2))
    try:
        valid_norm(torch.tensor([0.]))
    except ValueError:
        check('toy zero denominator explicitly errors', True)
    else:
        check('toy zero denominator explicitly errors', False)
    a = torch.tensor([[.1, .2]])
    b = torch.tensor([[.2], [.3]])
    us, ns, gs, trace = surrogate(w, a, b, bn)
    with torch.autocast('cpu', dtype=torch.bfloat16):
        lid = torch.nn.functional.linear(torch.nn.functional.linear(torch.eye(2), a), b).T
        actual = DoraLinearLayer(False).get_weight_norm(w, lid, 1.)
    check('toy installed PEFT norm equals surrogate', torch.equal(ns, actual))
    check('toy PEFT surrogate dtype trace', trace['identity_B'] == 'torch.bfloat16' and trace['quotient'] == 'torch.float32')
    r0 = (gs-1)[:,None]*w
    gl = gs[:,None]*lid.float()
    check('toy decomposition identity', math.isclose(ss(gs[:,None]*us-w), ss(r0)+ss(gl)+2*dot(r0,gl), rel_tol=3e-6, abs_tol=1e-10))
    return dict(bf16_previous_one=prev, bf16_next_one=nex, dtype_trace=trace)


ROW_FIELDS = ['n', 'm', 'base_norm_fp32', 'base_norm_fp32_cast_bf16', 'base_norm_cpu_bf16',
              'g', 'g_minus_one', 'abs_g_minus_one', 'g_cast_bf16_equals_one',
              'surrogate_n', 'surrogate_g', 'surrogate_g_equals_one',
              'surrogate_g_abs_error', 'surrogate_g_relative_error',
              'm_base_fp32_abs_relative_residual', 'm_base_cast_bf16_abs_relative_residual',
              'm_base_cpu_bf16_abs_relative_residual',
              'm_base_fp32_exact', 'm_base_cast_bf16_exact', 'm_base_cpu_bf16_exact',
              'remove_dense_equal_row', 'reset_dense_equal_row']


def analyze(module, Wdisk, A, B, m):
    check(module+' base BF16', Wdisk.dtype == torch.bfloat16)
    check(module+' adapter F32', A.dtype == B.dtype == m.dtype == torch.float32)
    out, inp = Wdisk.shape
    check(module+' shapes', A.shape == (32, inp) and B.shape == (out, 32) and m.shape == (out,))
    check(module+' finite input', all(bool(torch.all(torch.isfinite(x))) for x in (Wdisk,A,B,m)))
    w = Wdisk.float()
    l = B @ A
    u = w + l
    n = torch.linalg.norm(u, dim=1)
    bn = torch.linalg.norm(w, dim=1)
    valid_norm(n)
    valid_norm(bn)
    g = m/n
    bcast = bn.to(torch.bfloat16).float()
    bcpu = torch.linalg.norm(Wdisk, dim=1).float()
    valid_norm(bcast)
    valid_norm(bcpu)
    us, ns, gs, trace = surrogate(w, A, B, m)
    check(module+' surrogate quotient F32', gs.dtype == torch.float32)
    check(module+' finite derived', all(bool(torch.all(torch.isfinite(x))) for x in (l,u,n,g,us,ns,gs)))
    rows = dict(n=n, m=m, base_norm_fp32=bn, base_norm_fp32_cast_bf16=bcast,
                base_norm_cpu_bf16=bcpu, g=g, g_minus_one=g-1, abs_g_minus_one=(g-1).abs(),
                g_cast_bf16_equals_one=g.to(torch.bfloat16)==1,
                surrogate_n=ns, surrogate_g=gs, surrogate_g_equals_one=gs==1,
                surrogate_g_abs_error=(gs-g).abs(), surrogate_g_relative_error=(gs-g).abs()/g.abs().clamp_min(torch.finfo(torch.float32).tiny),
                m_base_fp32_abs_relative_residual=(m-bn).abs()/bn,
                m_base_cast_bf16_abs_relative_residual=(m-bcast).abs()/bcast,
                m_base_cpu_bf16_abs_relative_residual=(m-bcpu).abs()/bcpu,
                m_base_fp32_exact=m==bn, m_base_cast_bf16_exact=m==bcast,
                m_base_cpu_bf16_exact=m==bcpu)
    sums = {k+'_ss': 0. for k in ('W0','L','U','WD','Delta','R','Rm','reset_delta','R0','GL','dense_Delta','dense_L','dense_W0','surrogate_R')}
    sums.update(R_dot_L=0., R0_dot_GL=0., remove_dense_ss=0., reset_dense_ss=0.,
                remove_dense_maxabs=0., reset_dense_maxabs=0., remove_row_identity_maxabs=0., reset_row_identity_maxabs=0.)
    eqremove, eqreset = [], []
    sums.update(elements=out*inp, rows=out, remove_dense_equal_elements=0, reset_dense_equal_elements=0,
                remove_dense_equal_rows=0, reset_dense_equal_rows=0)
    for lo in range(0, out, 128):
        hi = min(out, lo+128)
        wb,lb,ub = w[lo:hi],l[lo:hi],u[lo:hi]
        gb = g[lo:hi,None]
        wd = gb*ub
        reset = (bn[lo:hi]/n[lo:hi])[:,None]*ub
        r = (gb-1)*ub
        rm = ((m[lo:hi]-bn[lo:hi])/n[lo:hi])[:,None]*ub
        r0 = (gb-1)*wb
        gl = gb*lb
        vals = dict(W0=wb,L=lb,U=ub,WD=wd,Delta=wd-wb,R=r,Rm=rm,
                    reset_delta=reset-wb,R0=r0,GL=gl,
                    surrogate_R=(gs[lo:hi,None]-1)*us[lo:hi])
        for key,value in vals.items():
            sums[key+'_ss'] += ss(value)
        sums['R_dot_L'] += dot(r,lb)
        sums['R0_dot_GL'] += dot(r0,gl)
        # R and Rm evaluated with stable radial formulas; validate both algebraic
        # row identities and their agreement with explicit FP32 subtraction.
        for key,value,target in [('remove',r,(m[lo:hi]-n[lo:hi]).abs()), ('reset',rm,(m[lo:hi]-bn[lo:hi]).abs())]:
            err = (torch.linalg.norm(value,dim=1)-target).abs().max().item()
            sums[key+'_row_identity_maxabs'] = max(sums[key+'_row_identity_maxabs'],err)
        check(module+f' block{lo} R explicit subtraction', torch.allclose(r,wd-ub,rtol=2e-3,atol=2e-7))
        check(module+f' block{lo} Rm explicit subtraction', torch.allclose(rm,wd-reset,rtol=2e-3,atol=2e-7))
        dw,du,dr = (v.to(torch.bfloat16).float() for v in (wd,ub,reset))
        sums['dense_Delta_ss'] += ss(dw-wb)
        sums['dense_L_ss'] += ss(du-wb)
        sums['dense_W0_ss'] += ss(wb)
        for key,other,eqs in [('remove',du,eqremove),('reset',dr,eqreset)]:
            equal = dw==other
            er = torch.all(equal,dim=1)
            eqs.append(er)
            sums[key+'_dense_equal_elements'] += int(equal.sum())
            sums[key+'_dense_equal_rows'] += int(er.sum())
            diff = dw-other
            sums[key+'_dense_ss'] += ss(diff)
            sums[key+'_dense_maxabs'] = max(sums[key+'_dense_maxabs'],float(diff.abs().max()))
    rows['remove_dense_equal_row'] = torch.cat(eqremove)
    rows['reset_dense_equal_row'] = torch.cat(eqreset)
    for key in rows:
        rows[key] = rows[key].numpy().copy()
    sums.update(g_equals_one=int((g==1).sum()),g_negative=int((g<0).sum()),m_zero=int((m==0).sum()),
                zero_norms=0, nonfinite_norms=0)
    denom = max(sums['Delta_ss'],1e-30)
    reconstructed = sums['R0_ss']+sums['GL_ss']+2*sums['R0_dot_GL']
    sums['decomposition_relative_error'] = abs(sums['Delta_ss']-reconstructed)/denom
    check(module+' Delta decomposition', sums['decomposition_relative_error'] < 2e-5)
    # Absolute tolerance bounds accumulated FP32 normalization/cancellation.
    tol = 2e-6*float(torch.max(torch.stack([m.abs().max(),n.max(),bn.max()])))+2e-7
    check(module+' R row norm identity', sums['remove_row_identity_maxabs'] <= tol)
    check(module+' Rm row norm identity', sums['reset_row_identity_maxabs'] <= tol)
    return sums,rows,trace


def summarize(sums, rows):
    result = dict(sums)
    for k in ROW_FIELDS:
        if k.endswith('_exact') or k.endswith('_row') or k.endswith('_equals_one'):
            result[k+'_count'] = int(np.count_nonzero(rows[k]))
            result[k+'_fraction'] = float(np.mean(rows[k]))
        else:
            result.update(describe(rows[k], k))
    for k in ('R','Rm','R0','GL','reset_delta'):
        for reference in ('W0','Delta','L'):
            result[f'{k}_norm_over_{reference}'] = ratio(sums[k+'_ss'],sums[reference+'_ss'])
    result['R_energy_over_Delta'] = sums['R_ss']/sums['Delta_ss'] if sums['Delta_ss'] else None
    result['R_dot_L_cosine'] = sums['R_dot_L']/math.sqrt(sums['R_ss']*sums['L_ss']) if sums['R_ss']*sums['L_ss'] else None
    result['radial_additive_cancellation_ratio'] = sums['Delta_ss']/(sums['R_ss']+sums['L_ss']) if sums['R_ss']+sums['L_ss'] else None
    for k in ('remove','reset'):
        result[k+'_dense_changed_elements'] = sums['elements']-sums[k+'_dense_equal_elements']
        result[k+'_dense_changed_fraction'] = result[k+'_dense_changed_elements']/sums['elements']
        result[k+'_dense_equal_row_fraction'] = sums[k+'_dense_equal_rows']/sums['rows']
        for ref in ('W0','Delta','L'):
            result[k+'_dense_norm_over_'+ref] = ratio(sums[k+'_dense_ss'],sums['dense_'+ref+'_ss'])
        cast = rows['g_cast_bf16_equals_one'].astype(bool)
        changed = ~rows[k+'_dense_equal_row'].astype(bool)
        for a in (0,1):
            for b in (0,1):
                result[f'{k}_crosstab_gcast_one_{a}_dense_changed_{b}'] = int(np.sum((cast==a)&(changed==b)))
    return result


def csvwrite(path, records):
    with open(path,'w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--repo',type=Path,default=Path('./artifacts'))
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--raw',type=Path,required=True)
    p.add_argument('--pilot',action='store_true')
    p.add_argument('--compare-pilot',type=Path)
    args=p.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    args.raw.mkdir(parents=True,exist_ok=True)
    io0=Path('/proc/self/io').read_text()
    toy=toy_tests()
    config_path=args.repo/'configs/shadow_qwen3_4b_gsm8k.json'
    downloads_path=args.repo/'results/shadow_4b_gsm8k-downloads.json'
    config=json.loads(config_path.read_text())
    downloads=json.loads(downloads_path.read_text())
    inputs=[]
    hash_start=time.perf_counter()
    paths={}
    for role in ('base','dora'):
        record=downloads['artifacts'][role]
        check(role+' pinned revision agreement',record['revision']==config['artifacts'][role]['revision'])
        root=Path(record['snapshot_path'])
        check(role+' snapshot matches pinned revision',root.name==record['revision'])
        paths[role]=root
        for item in config['artifacts'][role]['files']:
            if not item['path'].endswith('.safetensors'):
                continue
            path=root/item['path']
            digest=sha(path)
            check(role+' weight hash '+item['path'],digest==item['sha256'])
            check(role+' weight byte size '+item['path'],path.stat().st_size==item['size'])
            inputs.append(dict(path=str(path),sha256=digest,bytes=path.stat().st_size,pinned_sha256=item['sha256']))
    hash_seconds=time.perf_counter()-hash_start
    for path in (config_path,downloads_path,paths['base']/'model.safetensors.index.json',paths['base']/'config.json',paths['dora']/'adapter_config.json',args.repo/'docs/diagnostics/radial-activity-2026-10-11/SPEC.md',args.repo/'docs/diagnostics/radial-activity-2026-10-11/INVENTORY.md'):
        inputs.append(dict(path=str(path),sha256=sha(path),bytes=path.stat().st_size))
    adapter_config=json.loads((paths['dora']/'adapter_config.json').read_text())
    for key,value in dict(r=32,lora_alpha=32,bias='none',fan_in_fan_out=False,use_rslora=False,use_dora=True).items():
        check('adapter config '+key,adapter_config.get(key)==value)
    for key in ('rank_pattern','alpha_pattern'):
        check('empty '+key,not adapter_config.get(key))
    index=json.loads((paths['base']/'model.safetensors.index.json').read_text())['weight_map']
    modules=[f'base_model.model.model.layers.{layer}.self_attn.{proj}_proj' for layer in range(36) for proj in ('q','k','v','o')]
    adapter_path=paths['dora']/'adapter_model.safetensors'
    with safe_open(adapter_path,framework='pt',device='cpu') as af:
        expected={module+suffix for module in modules for suffix in ('.lora_A.weight','.lora_B.weight','.lora_magnitude_vector')}
        check('exact 432 adapter key set',set(af.keys())==expected)
        # Verify all headers before measuring any selected module.
        for module in modules:
            basekey=module.removeprefix('base_model.model.')+'.weight'
            check(module+' base key map',basekey in index)
            with safe_open(paths['base']/index[basekey],framework='pt',device='cpu') as bf:
                shape=bf.get_slice(basekey).get_shape()
                check(module+' base header dtype',bf.get_slice(basekey).get_dtype()=='BF16')
            for suffix,shape_expected in (('.lora_A.weight',[32,shape[1]]),('.lora_B.weight',[shape[0],32]),('.lora_magnitude_vector',[shape[0]])):
                sl=af.get_slice(module+suffix)
                check(module+suffix+' header',sl.get_shape()==shape_expected and sl.get_dtype()=='F32')
        selected=modules[:4] if args.pilot else modules
        module_records=[]
        row_records=[]
        rawpath=args.raw/'row-activity.csv.gz'
        measure_start=time.perf_counter()
        with gzip.open(rawpath,'wt',newline='') as gz:
            rw=csv.writer(gz)
            rw.writerow(['module','projection','row']+ROW_FIELDS)
            for ordinal,module in enumerate(selected):
                t=time.perf_counter()
                basekey=module.removeprefix('base_model.model.')+'.weight'
                with safe_open(paths['base']/index[basekey],framework='pt',device='cpu') as bf:
                    w=bf.get_tensor(basekey)
                    a=af.get_tensor(module+'.lora_A.weight')
                    b=af.get_tensor(module+'.lora_B.weight')
                    m=af.get_tensor(module+'.lora_magnitude_vector')
                    sums,rows,trace=analyze(module,w,a,b,m)
                projection=module.split('.')[-1][0].upper()
                record=dict(module=module,projection=projection,**summarize(sums,rows))
                module_records.append(record)
                row_records.append((projection,sums,rows))
                for i in range(len(rows['n'])):
                    rw.writerow([module,projection,i]+[rows[k][i].item() for k in ROW_FIELDS])
                del w,a,b,m
                print(json.dumps(dict(completed=ordinal+1,total=len(selected),module=module,seconds=time.perf_counter()-t,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)),flush=True)
    measure_seconds=time.perf_counter()-measure_start
    group_records=[]
    maxkeys={k for k in row_records[0][1] if 'maxabs' in k or k=='decomposition_relative_error'}
    for group in ('all','Q','K','V','O'):
        subset=[r for r in row_records if group=='all' or r[0]==group]
        sums={k:(max(r[1][k] for r in subset) if k in maxkeys else sum(r[1][k] for r in subset)) for k in subset[0][1]}
        rows={k:np.concatenate([r[2][k] for r in subset]) for k in ROW_FIELDS}
        group_records.append(dict(group=group,modules=len(subset),**summarize(sums,rows)))
    check('output row count',len(module_records)==(4 if args.pilot else 144))
    check('group row count',len(group_records)==5)
    check('global row count',group_records[0]['rows']==(8704 if args.pilot else 313344))
    check('weighted group squares',all(math.isclose(group_records[0][k],sum(r[k] for r in group_records[1:]),rel_tol=1e-12,abs_tol=1e-12) for k in row_records[0][1] if k.endswith('_ss')))
    csvwrite(args.out/'module-activity.csv',module_records)
    csvwrite(args.out/'group-activity.csv',group_records)
    if args.compare_pilot:
        old=list(csv.DictReader(open(args.compare_pilot)))
        now=list(csv.DictReader(open(args.out/'module-activity.csv')))
        check('pilot/full first four rows exact deterministic agreement',old==now[:4])
    source=Path(inspect.getfile(DoraLinearLayer))
    resource_info=dict(cpu_threads=2,cuda_visible_devices='',gpu_used=False,
                       peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                       hash_verification_seconds=hash_seconds,measurement_seconds=measure_seconds,
                       wall_seconds=time.perf_counter()-START,proc_io_start=io0,
                       proc_io_finish=Path('/proc/self/io').read_text(),
                       versions=dict(python=platform.python_version(),torch=torch.__version__,numpy=np.__version__,peft=peft.__version__),
                       dtype_trace=trace,mode='pilot' if args.pilot else 'full',
                       no_training=True,no_model_forward=True,no_svd=True,no_new_dependencies=True)
    dump(args.out/'resource-use.json',resource_info)
    dump(args.out/'validation.json',dict(pass_=True,checks=len(CHECKS),failed=0,modules=len(selected),rows=group_records[0]['rows'],toy=toy,details=CHECKS))
    method='''# Radial activity measurement\n\nThis post-campaign CPU diagnostic measures GSM8K Qwen3-4B endpoint weights, not a training mechanism. Base tensors are native BF16 promoted to FP32; raw A/B/m remain FP32. Scaling is 32/32=1. Ideal quantities are L=BA, U=W0+L, n=rowNorm(U), g=m/n, WD=gU and Wreset=(rowNorm(W0)/n)U. R=(g-1)U and Rm=((m-rowNorm(W0))/n)U use stable equivalent formulas; explicit FP32 subtraction and row norm identities are checked with recorded tolerances.\n\nR0=(g-1)W0 is the conditioning term; GL=gL. FP64 sums over FP32 blocks verify Delta energy=R0 energy+GL energy+2 dot(R0,GL). Norm ratios are square roots of global sums of squares, never means of module ratios. Global quantiles concatenate all row arrays. Delta=WD-W0; R energy/Delta energy can exceed one. Endpoint baseline residuals compare saved m with FP32 base row norms, BF16 casts of those norms, and CPU BF16 row norms. Training initializer/library/base provenance is unknown, so these are not learned movement.\n\nDense proxies cast WD, U and Wreset individually to actual torch BF16. Element differences, exact equal counts, fully equal rows and their cross-tabs with BF16(g)==1 are measured after promoting the rounded matrices to FP32. Dense Delta is BF16(WD)-W0 and dense L is BF16(U)-W0; these are the ratio references. This proxy is not PEFT function fidelity. BF16(g)==1 is a counterfactual quotient cast. Actual current-PEFT-operation CPU surrogate executes identity B(A(I)) under CPU BF16 autocast, adds its BF16 result to FP32 W0, computes FP32 norm and FP32 g. Installed PEFT get_weight_norm is checked on a toy; CPU kernels do not establish historical CUDA bitwise behavior. Surrogate R uses (g_surrogate-1)U_surrogate.\n\nAll used weight files are SHA256-verified before measurements against the pinned config. Downloads manifest supplies revisions/paths and past verified-file names, but contains no literal SHA digests; config supplies expected digests. Both are hashed. Safetensors are opened one module at a time; no full model, training, forward evaluation, SVD, GPU computation, downloads or installations occur. Tiny toy tensor operations are validation only.\n\nCSV empty cells mean undefined zero-denominator ratios. All denominator row norms must be positive/finite; failures raise rather than clamp. Only relative surrogate g error uses minimum-positive protection; if g=0 it should be interpreted with recorded m_zero count. Quantiles use NumPy linear interpolation. No p values or independent-training claims are made. Manifest omits its own hash to avoid cycles. Logs and compressed row data remain server-side.\n'''
    (args.out/'METHOD.md').write_text(method)
    outputs=[]
    for name in ('module-activity.csv','group-activity.csv','validation.json','resource-use.json','METHOD.md'):
        path=args.out/name
        outputs.append(dict(path=str(path),sha256=sha(path),bytes=path.stat().st_size))
    outputs.append(dict(path=str(rawpath),sha256=sha(rawpath),bytes=rawpath.stat().st_size,schema=['module','projection','row']+ROW_FIELDS))
    dump(args.out/'manifest.json',dict(format_version=1,mode='pilot' if args.pilot else 'full',inputs=inputs,outputs=outputs,
                                      code=dict(path=str(Path(__file__).resolve()),sha256=sha(__file__)),
                                      peft_source=dict(path=str(source),sha256=sha(source),forward_sha256=hashlib.sha256(inspect.getsource(DoraLinearLayer.forward).encode()).hexdigest(),get_weight_norm_sha256=hashlib.sha256(inspect.getsource(DoraLinearLayer.get_weight_norm).encode()).hexdigest()),
                                      dtype_trace=trace,complete=True))
    print(json.dumps(dict(done=True,modules=len(selected),checks=len(CHECKS),wall_seconds=time.perf_counter()-START)),flush=True)


if __name__=='__main__':
    main()
