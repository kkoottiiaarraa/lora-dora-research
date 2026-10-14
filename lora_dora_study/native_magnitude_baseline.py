"""Cheap source-magnitude-preserving DoRA recompression comparators."""


def retain_magnitude(base, source_direction, source_scale, record):
    import torch
    scale=source_scale.double()
    if not bool(scale.isfinite().all()) or float(scale.abs().min())<1e-6:
        raise ValueError('Degenerate source scale')
    # Source magnitude from the same finite-precision source convention.
    magnitude=source_scale*source_direction.norm(dim=1)
    left=record['left'].double()/scale[:,None]
    right=record['right'].double()
    denominator=(base.double()+left@right).norm(dim=1)
    if not bool((denominator>0).all()):raise ValueError('Degenerate direction')
    new_scale=magnitude.double()/denominator
    result=dict(left=(left*new_scale[:,None]).float().contiguous(),
        right=record['right'].clone(),row_scale=new_scale.float().contiguous())
    deployed=result['row_scale'].double()[:,None]*base.double()+result['left'].double()@result['right'].double()
    discrepancy=float(((deployed.norm(dim=1)-magnitude.double().abs()).abs()/magnitude.double().abs().clamp_min(1e-20)).max())
    if discrepancy>1e-6:raise ValueError('Source magnitude not preserved numerically')
    if any(not bool(t.isfinite().all()) for t in result.values()):raise FloatingPointError('Nonfinite native baseline')
    if sum(t.numel() for t in result.values())!=sum(t.numel() for t in record.values()):
        raise ValueError('Storage changed')
    return result,dict(maximum_relative_magnitude_error=discrepancy,
                       maximum_scale_change=float((result['row_scale'].double()-scale).abs().max()))


def augment(root):
    import json
    from pathlib import Path
    import torch
    from lora_dora_study.evaluation import sha256_file
    from lora_dora_study.server import write_json
    manifest=json.loads((root/'eval-manifest-private.json').read_text())
    parent=Path(manifest['full_root'])
    oldprep=json.loads((parent/'prepare/summary.json').read_text())
    if sha256_file(parent/'prepare/factors.pt')!=oldprep['factors_sha256']:
        raise ValueError('Input-only source factors changed')
    primary=torch.load(root/'prepare/factors.pt',map_location='cpu',weights_only=True)
    old=torch.load(parent/'prepare/factors.pt',map_location='cpu',weights_only=True)['structural_8']
    capture=json.loads((parent/'capture/summary.json').read_text())
    supplements=dict(native_m_input={},native_m_kfac={});rows=[]
    for item in capture['modules']:
        name=item['name'];path=parent/'capture'/item['file']
        if sha256_file(path)!=item['sha256']:raise ValueError('Capture changed')
        data=torch.load(path,map_location='cpu',weights_only=True)
        direction=data['base']+(data['b']@data['a'])*data['scaling']
        for label,record in [('native_m_input',old[name]),('native_m_kfac',primary['structural_kfac'][name])]:
            if not torch.equal(record['row_scale'],data['row_scale']):raise ValueError('Source D changed')
            result,info=retain_magnitude(data['base'],direction,data['row_scale'],record)
            supplements[label][name]=result;rows.append(dict(module=name,label=label,**info))
    counts={label:sum(t.numel() for record in records.values() for t in record.values())
        for label,records in supplements.items()}
    if any(count!=5898240 for count in counts.values()):raise ValueError('Supplement budgets unequal')
    destination=root/'native-m-baselines.pt';torch.save(supplements,destination)
    write_json(root/'native-m-baselines.json',dict(status='complete',factor_counts=counts,
        factors_sha256=sha256_file(destination),diagnostics=rows,before_new_outputs=True))
    return supplements
