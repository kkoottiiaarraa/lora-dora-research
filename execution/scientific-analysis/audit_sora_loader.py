"""Check custom SORA serialization on a tiny untrained model, CPU only."""
import argparse
import copy
from functools import partial
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import time
import warnings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--author-fork', action='store_true', help='Declare pinned author PEFT on PYTHONPATH')
    args = parser.parse_args()
    started = time.monotonic()
    import torch
    from torch import nn
    import peft
    from peft import LoraConfig, PeftModel, get_peft_model
    from safetensors.torch import load_file
    torch.set_num_threads(2)
    spec = importlib.util.spec_from_file_location('pinned_sora', args.source)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mapping = {nn.Linear: partial(mod.SoraLinear, r_p=1)}

    class Tiny(nn.Module):
        def __init__(self):
            super().__init__()
            self.config = {'model_type': 'custom'}
            self.linear = nn.Linear(4, 3, bias=False, dtype=torch.float64)
            self.linear.weight.data.copy_(torch.tensor(
                [[1., .2, -.1, .3], [0., 1., .4, -.2], [.1, -.3, 1., .5]], dtype=torch.float64))

        def forward(self, x):
            return self.linear(x)

    def error(a, b):
        return float((a-b).norm()/b.norm().clamp_min(1e-30))

    torch.manual_seed(20261014)
    x = torch.tensor([[1., 2., -.5, .3], [-.4, .1, .7, 1.]], dtype=torch.float64)
    rows = []
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with torch.inference_mode(), tempfile.TemporaryDirectory(prefix='sora-loader-', dir=args.output.parent) as tmp:
        for nontrivial in (False, True):
            base = Tiny()
            options = dict(r=1, lora_alpha=2, lora_dropout=0, target_modules=['linear'], bias='none')
            if 'adapter_name' in LoraConfig.__dataclass_fields__:
                options['adapter_name'] = 'sora'
            config = LoraConfig(**options)
            config._register_custom_module(mapping)
            model = get_peft_model(copy.deepcopy(base), config).double().eval()
            layer = model.base_model.model.linear
            assert isinstance(layer, mod.SoraLinear)
            # Coefficients are exactly representable in FP32, then evaluated in FP64.
            # This avoids confusing dispatcher loss with constructor dtype rounding.
            layer.lora_A['default'].weight.copy_(torch.tensor([[.2, -.1, .3, .4]]))
            layer.lora_B['default'].weight.copy_(torch.tensor([[.1], [-.2], [.3]])
                                                if nontrivial else torch.zeros(3, 1, dtype=torch.float64))
            layer.lora_C['default'].weight.copy_(torch.tensor([[.1], [.2], [.3]]))
            layer.lora_D['default'].weight.copy_(torch.tensor([[.3], [-.1], [.2]])
                                                if nontrivial else layer.lora_C['default'].weight)
            layer.lora_Diag['default'].weight.copy_(torch.tensor([[1.2], [.8], [1.1]])
                                                   if nontrivial else torch.ones(3, 1, dtype=torch.float64))
            native = model(x).clone()
            w = base.linear.weight
            a, b = layer.lora_A['default'].weight, layer.lora_B['default'].weight
            c, d = layer.lora_C['default'].weight, layer.lora_D['default'].weight
            m = layer.lora_Diag['default'].weight * w + 2*b@a
            k = layer.compute_s_p('default')*(d@c.T-c@d.T)
            dense = x@((torch.eye(3, dtype=torch.float64)+k)@m).T
            case = 'nontrivial' if nontrivial else 'initialization'
            dest = Path(tmp)/case
            with warnings.catch_warnings(record=True) as save_messages:
                warnings.simplefilter('always')
                model.save_pretrained(dest)
            saved = load_file(str(dest/'adapter_model.safetensors'), device='cpu')
            saved_cfg = json.loads((dest/'adapter_config.json').read_text())
            with warnings.catch_warnings(record=True) as plain_messages:
                warnings.simplefilter('always')
                plain = PeftModel.from_pretrained(copy.deepcopy(base), dest).double().eval()
            loaded_cfg = LoraConfig.from_pretrained(dest)
            loaded_cfg._register_custom_module(mapping)
            with warnings.catch_warnings(record=True) as proper_messages:
                warnings.simplefilter('always')
                proper = PeftModel.from_pretrained(copy.deepcopy(base), dest, config=loaded_cfg).double().eval()

            def inventory(loaded):
                states = loaded.state_dict()
                checks = []
                for name, tensor in saved.items():
                    target = name.removesuffix('.weight')+'.default.weight'
                    checks.append(dict(key=name, present=target in states,
                                       exact=target in states and torch.equal(states[target], tensor)))
                return checks

            plain_checks, proper_checks = inventory(plain), inventory(proper)
            rows.append(dict(case=case, saved_tensor_count=len(saved), saved_keys=sorted(saved),
                             serialized_custom_mapping_present='_custom_modules' in saved_cfg,
                             plain_layer_class=type(plain.base_model.model.linear).__name__,
                             proper_layer_class=type(proper.base_model.model.linear).__name__,
                             native_dense_relative_error=error(native, dense),
                             plain_output_relative_error=error(plain(x), native),
                             proper_output_relative_error=error(proper(x), native),
                             plain_tensor_checks=plain_checks, proper_tensor_checks=proper_checks,
                             warnings=dict(save=[str(w.message) for w in save_messages],
                                           plain=[str(w.message) for w in plain_messages],
                                           proper=[str(w.message) for w in proper_messages])))

    accepted = all(r['native_dense_relative_error'] < 1e-12 and r['proper_output_relative_error'] < 1e-12
                   and r['saved_tensor_count'] == 5 and all(t['exact'] for t in r['proper_tensor_checks'])
                   for r in rows)
    result = dict(source_revision='24f62bfe84741e5613ae2e9f387f2e1f9bb64ba8',
                  source_sha256=hashlib.sha256(args.source.read_bytes()).hexdigest(),
                  script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  torch_version=torch.__version__, peft_version=peft.__version__,
                  author_peft_fork=args.author_fork,
                  peft_loader_source_sha256=hashlib.sha256(
                      (Path(peft.__file__).parent/'tuners/lora/model.py').read_bytes()).hexdigest(),
                  execution='complete pinned SoraLinear; no source modification',
                  dtype='float64', threads=torch.get_num_threads(), device='cpu', gpu_hours=0,
                  cases=rows, controls_pass=accepted, wall_seconds=time.monotonic()-started,
                  limitations=[('Pinned author PEFT fork, current installed Torch/Transformers dependencies'
                                if args.author_fork else 'Installed PEFT0.17.1, not full author fork'),
                               'Synthetic untrained adapter, no model quality claims',
                               'No inference that author paper scores used these exact public call sites'])
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(dict(controls_pass=accepted, cases=[{k:v for k,v in r.items()
                           if k not in ('warnings', 'plain_tensor_checks', 'proper_tensor_checks')} for r in rows],
                         wall_seconds=result['wall_seconds'])))
    if not accepted:
        raise SystemExit('Loader arithmetic controls failed')


if __name__ == '__main__':
    main()
