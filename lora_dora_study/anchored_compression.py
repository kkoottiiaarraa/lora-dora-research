"""Base-norm anchoring for the positive scalar V/O symmetry, not general GL gauges."""


def anchors(matrices):
    result={}
    for name,r in matrices.items():
        if name.endswith('v_proj'):
            ratio=float(r['base'].double().norm()/r['value'].double().norm())
            result[name.rsplit('.',1)[0]]=ratio
    return result


def canonical_values(matrices,multipliers=None):
    a=anchors(matrices);result={}
    for name,r in matrices.items():
        layer=name.rsplit('.',1)[0];c=a[layer]*(multipliers or {}).get(layer,1.)
        result[name]=r['value'].double()*(c if name.endswith('v_proj') else 1/c)
    return result
