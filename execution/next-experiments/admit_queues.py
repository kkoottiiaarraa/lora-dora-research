"""Adapted from night_localization_admission: ordered admission, existing evaluator."""
import argparse
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys
import time

S = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(S))
from lora_dora_study.server import gpu_snapshot, write_json

ORDER = json.loads(os.environ.get('RESEARCH_QUEUE_LANES', '["permuted","directional","bundle"]'))
P = Path(os.environ.get('RESEARCH_QUEUE_ROOT', str(S.parent / 'lora-dora-profiling' / 'next-experiments-queues-20261012')))
EXCLUDED_INDICES = {int(x) for x in os.environ.get('RESEARCH_EXCLUDED_GPU_INDICES', '').split(',') if x}
EXCLUDED_UUIDS = {x for x in os.environ.get('RESEARCH_EXCLUDED_GPU_UUIDS', '').split(',') if x}
LOCKS = Path('/tmp') / ('lora-dora-gpu-locks-' + str(os.getuid()))


MAX_USED_MIB = int(os.environ.get('RESEARCH_MAX_USED_MIB', '2048'))
SPEC_PATH = os.environ.get('RESEARCH_QUEUE_SPEC')
SPEC = json.loads(Path(SPEC_PATH).read_text()) if SPEC_PATH else None


def eligible(gpu):
    return (gpu['index'] not in EXCLUDED_INDICES and gpu['uuid'] not in EXCLUDED_UUIDS
            and gpu['utilization_percent'] < 20 and gpu['used_mib'] < MAX_USED_MIB)


def jobs(lane):
    if lane in {'permuted', 'directional'}:
        return [(lane, 'gsm8k', 'controls', lane, 96 * 3600)]
    return [('mmlu-remove-d', 'mmlu', 'remove_d', 'remove_d', 6 * 3600),
            ('squadv2-remove-d', 'squadv2', 'remove_d', 'remove_d', 12 * 3600)] + [
                ('text-' + role, 'gsm8k', 'nll', role, 6 * 3600)
                for role in ['base', 'lora', 'dora', 'remove_d']]


def worker(lane, uuid, lock_fd):
    # This inherited cooperative lock lasts across jobs; no internal idle waits.
    lock = os.fdopen(lock_fd, 'a')
    directory = P / lane
    directory.mkdir(exist_ok=True)
    state = dict(lane=lane, pid=os.getpid(), gpu_uuid=uuid, status='running', jobs=[])
    if SPEC is not None:
        try:
            for phase in ['gpu', 'cpu']:
                if phase == 'cpu':
                    lock.close()
                    state.update(gpu_released=True, status='cpu_running_gpu_released')
                    write_json(directory / 'state.json', state)
                for job in SPEC[lane].get(phase, []):
                    output = directory / job['name']
                    if output.exists():
                        raise RuntimeError('Refusing to overwrite: ' + str(output))
                    command = [sys.executable, str(S / job['script']), '--phase', phase,
                               '--output-dir', str(output), '--queue-dir', str(directory),
                               '--budget-seconds', str(job['budget_seconds'])] + job.get('arguments', [])
                    if phase == 'gpu':
                        command += ['--gpu-uuid', uuid]
                    state.update(current_job=job['name'], phase=phase)
                    write_json(directory / 'state.json', state)
                    env = dict(os.environ)
                    env['CUDA_VISIBLE_DEVICES'] = uuid if phase == 'gpu' else ''
                    with (directory / (job['name'] + '.log')).open('x') as log:
                        result = subprocess.run(command, cwd=S, env=env, stdout=log,
                                                stderr=subprocess.STDOUT,
                                                timeout=job['budget_seconds'] + 120)
                    state['jobs'].append(dict(name=job['name'], exit_code=result.returncode))
                    if result.returncode:
                        state.update(status='failed', exit_code=result.returncode)
                        write_json(directory / 'state.json', state)
                        return result.returncode
            state.update(status='complete', current_job=None, gpu_released=True)
            write_json(directory / 'state.json', state)
            return 0
        except Exception as error:
            state.update(status='failed', error=str(error))
            write_json(directory / 'state.json', state)
            raise
        finally:
            lock.close()
    for name, task, mode, condition, budget in jobs(lane):
        output = directory / name
        if output.exists():
            raise RuntimeError('Refusing to overwrite existing job: ' + str(output))
        command = [sys.executable, str(S / 'execution/next-experiments/pilot.py'),
                   '--stage', 'evaluate', '--evaluation-authorized',
                   '--budget-seconds', str(budget), '--gpu-uuid', uuid,
                   '--task', task, '--mode', mode, '--condition', condition,
                   '--output-dir', str(output)]
        if mode == 'nll':
            command += ['--nll-segments', str(P.parent / 'next-experiments-20261011/wikitext-segments.json')]
        state.update(current_job=name)
        write_json(directory / 'state.json', state)
        with (directory / (name + '.log')).open('x') as log:
            result = subprocess.run(command, cwd=S, stdout=log, stderr=subprocess.STDOUT)
        state['jobs'].append(dict(name=name, exit_code=result.returncode))
        if result.returncode:
            state.update(status='failed', current_job=name)
            write_json(directory / 'state.json', state)
            return result.returncode
    state.update(status='complete', current_job=None)
    write_json(directory / 'state.json', state)
    lock.close()
    return 0


def controller():
    P.mkdir(parents=True, exist_ok=True)
    LOCKS.mkdir(exist_ok=True)
    with (P / 'controller.lock').open('a') as unique:
        fcntl.flock(unique, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if (P / 'admission.json').exists():
            raise RuntimeError('Existing admission state; inspect before restarting')
        state = dict(pid=os.getpid(), status='waiting', interval_seconds=10,
                     consecutive_checks=2, policy=f'utilization<20 and used_mib<{MAX_USED_MIB}',
                     order=ORDER, queues={lane: dict(status='pending') for lane in ORDER})
        previous, children, position = set(), {}, 0
        while position < len(ORDER) or children:
            cycle_start = time.monotonic()
            for lane, child in list(children.items()):
                result = child.poll()
                if result is not None:
                    state['queues'][lane].update(status='complete' if result == 0 else 'failed', exit_code=result)
                    del children[lane]
                elif SPEC is not None and (P / lane / 'state.json').exists():
                    child_state = json.loads((P / lane / 'state.json').read_text())
                    state['queues'][lane].update(phase=child_state.get('phase'),
                        current_job=child_state.get('current_job'),
                        gpu_released=child_state.get('gpu_released', False))
            try:
                snapshot = gpu_snapshot()
                available = {g['uuid'] for g in snapshot['gpus'] if eligible(g)}
                stable = previous & available
                previous = available
                state.update(last_check_unix=time.time(), stable_gpu_uuids=sorted(stable),
                             gpus=snapshot['gpus'])
                for gpu in sorted(snapshot['gpus'], key=lambda g: (g['utilization_percent'], g['used_mib'], g['index'])):
                    if position == len(ORDER):
                        break
                    if gpu['uuid'] not in stable:
                        continue
                    handle = (LOCKS / (gpu['uuid'] + '.lock')).open('a')
                    try:
                        fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
                        fresh = next(g for g in gpu_snapshot()['gpus'] if g['uuid'] == gpu['uuid'])
                        if not eligible(fresh):
                            continue
                        lane = ORDER[position]
                        with (P / (lane + '-worker.log')).open('x') as log:
                            child = subprocess.Popen([sys.executable, __file__, '--lane', lane,
                                '--gpu-uuid', gpu['uuid'], '--lock-fd', str(handle.fileno())],
                                pass_fds=(handle.fileno(),), cwd=S, stdout=log, stderr=subprocess.STDOUT)
                        children[lane] = child
                        state['queues'][lane].update(status='running', pid=child.pid,
                            gpu_uuid=gpu['uuid'], gpu_index=gpu['index'], admitted_unix=time.time())
                        position += 1
                    except BlockingIOError:
                        pass
                    finally:
                        handle.close()
            except Exception as error:
                previous = set()
                state.update(last_probe_error=str(error))
            state['status'] = 'complete' if position == len(ORDER) and not children else 'running_or_waiting'
            write_json(P / 'admission.json', state)
            if state['status'] != 'complete':
                time.sleep(max(0, 10 - (time.monotonic() - cycle_start)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--lane', choices=ORDER)
    parser.add_argument('--gpu-uuid')
    parser.add_argument('--lock-fd', type=int)
    args = parser.parse_args()
    if args.lane:
        sys.exit(worker(args.lane, args.gpu_uuid, args.lock_fd))
    controller()
