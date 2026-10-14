"""Pure scheduling decisions shared by two persistent sequential queues."""
from lora_dora_study.server import idle_gpu


def balance(jobs):
    queues = [[], []]
    loads = [0., 0.]
    for job in sorted(jobs, key=lambda j: (-j["estimated_gpu_seconds"],j["id"])):
        index = min(range(2),key=lambda i: (loads[i],len(queues[i])))
        queues[index].append(job)
        loads[index] += job["estimated_gpu_seconds"]
    return queues, loads


def idle_candidates(snapshot, primary):
    # Give the unchanged primary runner priority between its workers. During a
    # running worker, exclude its last assigned GPU even if temporarily empty.
    if primary.get("status") in {"waiting_for_evaluation_gpu", "waiting_for_pilot"}:
        return set()
    excluded = {primary.get('retained_gpu_uuid')}
    if primary.get('status')=='running':excluded.add(primary.get('gpu_uuid'))
    return {g["uuid"] for g in snapshot["gpus"]
            if g["uuid"] not in excluded and idle_gpu(g,snapshot["compute_processes"])}
