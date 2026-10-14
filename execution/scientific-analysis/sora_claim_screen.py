"""Small analytic witnesses and evaluation call-site audit; Python stdlib only."""
import argparse
import ast
import hashlib
import json
import math
from pathlib import Path


def entropy(spectrum):
    energy = sum(x*x for x in spectrum)
    return -sum((x*x/energy)*math.log(x*x/energy) for x in spectrum if x)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--sources', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    source_names = ['run_glue.py', 'finetune_math.py', 'evaluate_gemma_math.py',
                    'lm-evaluation-harness/lm_eval/models/huggingface.py']
    audit = []
    for name in source_names:
        data = (args.sources/name).read_bytes()
        tree = ast.parse(data)
        calls = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                function = ast.unparse(node.func)
                if any(x in function for x in ['register_custom_module', 'from_pretrained',
                                                'get_peft_model', 'evaluate', 'merge_and_unload']):
                    calls.append({'line':node.lineno, 'call':function})
        audit.append({'file':name, 'sha256':hashlib.sha256(data).hexdigest(),
                      'sora_class_import_or_reference':'SoraLinear' in data.decode(),
                      'calls':sorted(calls, key=lambda x:x['line'])})

    # Theorem1: the positive expression divided by E proves the restricted claim.
    theorem1 = []
    for r, s, alpha, gamma in [(2,4,.5,.1), (4,7,.7,.2), (8,10,.8,.1)]:
        beta = math.sqrt(alpha*alpha-(s-r)*gamma*gamma/(r-1))
        energy = 1+(r-1)*alpha*alpha
        direct = entropy([1]+[beta]*(r-1)+[gamma]*(s-r))-entropy([1]+[alpha]*(r-1))
        proof = ((r-1)*beta*beta*math.log(alpha*alpha/(beta*beta))+
                 (s-r)*gamma*gamma*math.log(alpha*alpha/(gamma*gamma)))/energy
        theorem1.append(dict(r=r,s=s,alpha=alpha,beta=beta,gamma=gamma,
                             entropy_difference=direct,proof_expression=proof,error=abs(direct-proof)))

    # Higher algebraic rank with equal Frobenius energy does not imply higher entropy.
    eps = .01
    lora = [1.,1.,0.,0.]
    dora = [math.sqrt(2-3*eps*eps),eps,eps,eps]
    # W0=I4, L=diag(.1,.1,0,0), positive m=1+the desired delta entries.
    u = [1.1,1.1,1.,1.]
    m = [1+x for x in dora]
    scales = [mi/ui for mi,ui in zip(m,u)]
    reconstructed = [di*ui-1 for di,ui in zip(scales,u)]

    # Low-rank update exactly cancels a nontrivial diagonal conditioning term.
    cancellation = [2*(1-.5)-1, 1*(1+0)-1, 1*(1+0)-1]

    # Fixed nonzero adapter, two labels: a corrected loader need not improve accuracy.
    t = 1.
    scale = min(1., 1/(2*t+1e-6))
    k = scale*t*t
    x = [1., .75]
    loaded = x
    native = [x[0]-k*x[1],k*x[0]+x[1]]
    loaded_prediction = max(range(2),key=loaded.__getitem__)
    native_prediction = max(range(2),key=native.__getitem__)
    examples = [dict(label=y,plain_correct=int(loaded_prediction==y),
                     corrected_correct=int(native_prediction==y)) for y in [0,1]]
    result = dict(
        source_revision='24f62bfe84741e5613ae2e9f387f2e1f9bb64ba8',
        source_audit=audit,
        restricted_theorem1=theorem1,
        higher_rank_counterexample=dict(lora_rank=2,dora_rank=4,directional_rank=2,
            lora_energy=sum(x*x for x in lora),dora_energy=sum(x*x for x in dora),
            lora_entropy=entropy(lora),dora_entropy=entropy(dora),
            positive_m=all(x>0 for x in m),reconstruction_max_error=max(abs(a-b)for a,b in zip(dora,reconstructed)),
            violates_theorem1_assumptions=True),
        upper_bound_is_not_nonzero_lower_bound=dict(nontrivial_D=[2,1,1],directional_rank=1,
            effective_delta=cancellation),
        theorem2_literal_zero_generator=dict(P='identity',T1_P='identity',
            exp_P_minus_T1_norm=math.e-1,epsilon=.01,
            interpretation='notation/indexing inconsistency, not a failure of the corrected skew exponential bound'),
        corrected_first_order_bound=dict(generator_norm_leq_epsilon=True,
            exp_minus_I_plus_K_bound='epsilon^2/2',orthogonality_defect_bound='epsilon^2',
            requires_product_normalization='paper rule, not public sum-of-norms code rule'),
        loader_accuracy_sign=dict(input=x,plain_logits=loaded,corrected_logits=native,
            examples=examples,equal_mixture_net_accuracy_difference=0.,
            interpretation='possible improvement, degradation or equality; no direction identified for trained models'),
        gpu_hours=0,model_loads=0,training=False,
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    assert all(x['entropy_difference']>0 and x['error']<1e-12 for x in theorem1)
    assert result['higher_rank_counterexample']['dora_entropy']<result['higher_rank_counterexample']['lora_entropy']
    assert result['higher_rank_counterexample']['reconstruction_max_error']<1e-12
    assert cancellation==[0,0,0] and loaded_prediction!=native_prediction
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(controls_pass=True,restricted_theorem1_confirmed=True,
                         higher_rank_not_sufficient=True,loader_accuracy_sign_unidentified=True,
                         gpu_hours=0,model_loads=0)))


if __name__=='__main__':
    main()
