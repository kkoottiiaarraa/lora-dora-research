"""Exact diagonal witnesses, not measurements on trained checkpoints."""
from fractions import Fraction as F
import argparse
import hashlib
import json
import math
from pathlib import Path


def compress(value, base, rank=1):
    delta = [a-b for a, b in zip(value, base)]
    # For diagonal matrices this is a best Frobenius rank-k approximation.
    order = sorted(range(len(delta)), key=lambda i: (-abs(delta[i]), i))
    keep = set(order[:rank])
    return [b+(d if i in keep else 0) for i, (b, d) in enumerate(zip(base, delta))]


def product(v, o):
    return [a*b for a, b in zip(v, o)]


def sqnorm(values):
    return sum(x*x for x in values)


def distance(a, b):
    return sqnorm([x-y for x, y in zip(a, b)])


def canonical(v, o, base_v):
    # Deliberately simple pivot gauge; positive pivot required in these fixtures.
    c = base_v[0]/v[0]
    assert c > 0
    return [c*x for x in v], [x/c for x in o]


def run():
    fixtures = {
        'smooth_rank1': ([F(1)]*8, [F(1)]*8,
                         [F(2)]+[F(1)]*7, [F(1), F(3, 2)]+[F(1)]*6),
        'near_spectral_crossing_rank2': ([F(1), F(2)]+[F(1)]*6,
            [F(10+i, 10) for i in range(8)], [F(2001, 1000)]+[F(1)]*7,
            [F(10+i, 10) for i in range(8)]),
    }
    result = dict(scope='exact rational diagonal examples, not trained-model evidence',
        compression='rank1 SVD of each full delta against fixed base; deterministic ties',
        canonicalization='positive first V entry anchored to the corresponding base entry', fixtures={})
    for name, (bv, bo, v, o) in fixtures.items():
        original = product(v, o)
        base_compressed = product(compress(v, bv), compress(o, bo))
        canonical_pair = canonical(v, o, bv)
        canonical_compressed = product(compress(canonical_pair[0], bv), compress(canonical_pair[1], bo))
        rows, compressed = [], {}
        for c in [F(199, 200), F(1), F(201, 200)]:
            gv, go = [c*x for x in v], [x/c for x in o]
            assert product(gv, go) == original
            assert canonical(gv, go, bv) == canonical_pair
            cp = product(compress(gv, bv), compress(go, bo))
            compressed[c] = cp
            err, drift = distance(cp, original), distance(cp, base_compressed)
            rows.append(dict(c=str(c), source_function_exactly_preserved=True,
                compressed_relative_frobenius_error=math.sqrt(float(err/sqnorm(original))),
                compressed_drift_from_c1_over_original_norm=math.sqrt(float(drift/sqnorm(original))),
                squared_error_exact=str(err), composition=[str(x) for x in cp]))
        spread = math.sqrt(float(distance(compressed[F(199, 200)], compressed[F(201, 200)])/sqnorm(original)))
        result['fixtures'][name] = dict(rows=rows,
            local_compressed_output_spread_over_original_norm=spread,
            canonical_compressed_relative_error=math.sqrt(float(distance(canonical_compressed, original)/sqnorm(original))),
            canonical_compression_exactly_gauge_invariant=True)
    assert result['fixtures']['smooth_rank1']['rows'][1]['squared_error_exact'] == '0'
    assert result['fixtures']['smooth_rank1']['canonical_compressed_relative_error'] > .28
    assert result['fixtures']['near_spectral_crossing_rank2']['local_compressed_output_spread_over_original_norm'] > .3
    result['script_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = run()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    for name, value in result['fixtures'].items():
        print(name, 'local compression spread=', value['local_compressed_output_spread_over_original_norm'],
              'canonical error=', value['canonical_compressed_relative_error'])
