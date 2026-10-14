"""Run selected unmodified author methods on tiny CPU tensors; no model loads."""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    started = time.monotonic()
    import torch
    from torch import nn
    from peft.tuners.tuners_utils import check_adapters_to_merge
    from peft.utils.other import transpose
    import peft
    import warnings
    from typing import Any, Optional

    torch.set_num_threads(2)
    source = args.source.read_bytes()
    tree = ast.parse(source)
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'SoraLinear')
    names = {'compute_s_p', 'forward', 'get_delta_weight', 'merge', 'unmerge'}
    methods = [n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name in names]
    assert {n.name for n in methods} == names
    namespace = dict(torch=torch, nn=nn, check_adapters_to_merge=check_adapters_to_merge,
                     transpose=transpose, warnings=warnings, Any=Any, Optional=Optional)
    exec(compile(ast.Module(body=methods, type_ignores=[]), '<pinned-author-methods>', 'exec'), namespace)

    class Harness(nn.Module):
        def __init__(self, nontrivial):
            super().__init__()
            self.in_features, self.out_features = 4, 3
            self.base_layer = nn.Linear(4, 3, bias=False, dtype=torch.float64)
            self.base_layer.weight.data.copy_(torch.tensor(
                [[1., .2, -.1, .3], [0., 1., .4, -.2], [.1, -.3, 1., .5]], dtype=torch.float64))
            self.lora_A = nn.ModuleDict({'default': nn.Linear(4, 1, bias=False, dtype=torch.float64)})
            self.lora_B = nn.ModuleDict({'default': nn.Linear(1, 3, bias=False, dtype=torch.float64)})
            self.lora_C = nn.ModuleDict({'default': nn.Linear(1, 3, bias=False, dtype=torch.float64)})
            self.lora_D = nn.ModuleDict({'default': nn.Linear(1, 3, bias=False, dtype=torch.float64)})
            self.lora_Diag = nn.ModuleDict({'default': nn.Linear(1, 3, bias=False, dtype=torch.float64)})
            self.lora_dropout = nn.ModuleDict({'default': nn.Identity()})
            self.lora_A['default'].weight.data.copy_(torch.tensor([[.2, -.1, .3, .4]]))
            if nontrivial:
                self.lora_B['default'].weight.data.copy_(torch.tensor([[.1], [-.2], [.3]]))
            else:
                self.lora_B['default'].weight.data.zero_()
            self.lora_C['default'].weight.data.copy_(torch.tensor([[.1], [.2], [.3]]))
            self.lora_D['default'].weight.data.copy_(torch.tensor([[.3], [-.1], [.2]]) if nontrivial
                                                   else self.lora_C['default'].weight.data)
            if nontrivial:
                self.lora_Diag['default'].weight.data.copy_(torch.tensor([[1.2], [.8], [1.1]]))
            else:
                self.lora_Diag['default'].weight.data.fill_(1.)
            self.scaling = {'default': 2.}
            self.initial_s_p = {'default': 1.}
            self.lora_bias = {'default': False}
            self.fan_in_fan_out = False
            self.disable_adapters = False
            self.active_adapters = ['default']
            self.merged_adapters = []

        @property
        def merged(self):
            return bool(self.merged_adapters)

        def get_base_layer(self):
            return self.base_layer

    for name in names:
        setattr(Harness, name, namespace[name])

    def relative_error(a, b):
        return float(torch.linalg.vector_norm(a-b) / torch.linalg.vector_norm(b).clamp_min(1e-30))

    rows = []
    torch.manual_seed(20261014)
    x = torch.tensor([[1., 2., -.5, .3], [-.4, .1, .7, 1.]], dtype=torch.float64)
    with torch.inference_mode():
        for nontrivial in (False, True):
            h = Harness(nontrivial)
            original = h.base_layer.weight.clone()
            a, b = h.lora_A['default'].weight, h.lora_B['default'].weight
            c, d = h.lora_C['default'].weight, h.lora_D['default'].weight
            diag = h.lora_Diag['default'].weight[:, 0]
            m = diag[:, None]*original + 2*(b@a)
            k = h.compute_s_p('default')*(d@c.T-c@d.T)
            expected_weight = (torch.eye(3, dtype=torch.float64)+k)@m
            expected = x@expected_weight.T
            native = h(x).clone()
            author_weight = original+h.get_delta_weight('default')
            h.merge(safe_merge=False)
            merged_weight = h.base_layer.weight.clone()
            h.unmerge()
            roundtrip = h.base_layer.weight.clone()
            h.base_layer.weight.copy_(expected_weight)
            fixed_output = h.base_layer(x).clone()
            h.base_layer.weight.copy_(original)
            row = dict(case='nontrivial' if nontrivial else 'initialization',
                       native_dense_relative_error=relative_error(native, expected),
                       author_export_relative_error=relative_error(x@author_weight.T, native),
                       author_export_weight_norm=float(torch.linalg.vector_norm(author_weight)),
                       merge_equals_author_export=torch.equal(merged_weight, author_weight),
                       author_roundtrip_relative_error=relative_error(roundtrip, original),
                       corrected_export_relative_error=relative_error(fixed_output, native),
                       explicit_restore_bitwise=torch.equal(h.base_layer.weight, original))
            rows.append(row)

        scales = []
        for t in (.01, .1, 1., 10.):
            h = Harness(False)
            h.lora_C['default'].weight.copy_(torch.tensor([[t], [0.], [0.]], dtype=torch.float64))
            h.lora_D['default'].weight.copy_(torch.tensor([[0.], [t], [0.]], dtype=torch.float64))
            s = float(h.compute_s_p('default'))
            c, d = h.lora_C['default'].weight, h.lora_D['default'].weight
            k = s*(d@c.T-c@d.T)
            p = torch.eye(3, dtype=torch.float64)+k
            defect = p.T@p-torch.eye(3, dtype=torch.float64)
            theoretical = k.T@k
            paper_s = .01/(2*t*t+.01)
            scales.append(dict(t=t, code_scale=s, paper_scale_epsilon_001=paper_s,
                               code_skew_spectral_norm=s*t*t,
                               code_orthogonality_defect=float(torch.linalg.matrix_norm(defect, ord=2)),
                               code_max_stretch=float(torch.linalg.matrix_norm(p, ord=2)),
                               defect_identity_max_abs=float((defect-theoretical).abs().max()),
                               paper_max_stretch=(1+(paper_s*t*t)**2)**.5))

    accepted = (all(r['native_dense_relative_error'] < 1e-12 and
                    r['corrected_export_relative_error'] < 1e-12 and
                    r['explicit_restore_bitwise'] and r['merge_equals_author_export'] for r in rows)
                and all(s['defect_identity_max_abs'] < 1e-12 for s in scales))
    result = dict(schema_version=1, source_sha256=hashlib.sha256(source).hexdigest(),
                  script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  source_revision='24f62bfe84741e5613ae2e9f387f2e1f9bb64ba8',
                  execution='unmodified selected author AST methods; minimal field harness',
                  dtype='float64', device='cpu', torch_version=torch.__version__,
                  peft_helper_version=peft.__version__, threads=torch.get_num_threads(),
                  module_cases=rows, scale_cases=scales,
                  arithmetic_controls_pass=accepted, gpu_hours=0,
                  wall_seconds=time.monotonic()-started,
                  limitations=['No author checkpoints or benchmark outputs tested',
                               'No full author PEFT fork compatibility claim',
                               'Synthetic parameters do not establish trained orthogonality defect',
                               'Bias, dropout, fan_in_fan_out and multi-adapter cases excluded'])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({'arithmetic_controls_pass':accepted, 'module_cases':rows,
                      'wall_seconds':result['wall_seconds'], 'gpu_hours':0}))
    if not accepted:
        raise SystemExit('Arithmetic controls failed')


if __name__ == '__main__':
    main()
