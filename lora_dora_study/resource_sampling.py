"""Existing pilot ResourceSampler extracted without changing the frozen evaluator."""
import datetime
import json
import os
import threading
import time
from lora_dora_study.server import gpu_snapshot, available_memory_bytes


class ResourceSampler:
    def __init__(self, path, uuid):
        self.path, self.uuid = path, uuid
        self.stop_event = threading.Event()
        self.error = None
        self.thread = threading.Thread(target=self.run, daemon=True)

    def sample(self):
        snapshot = gpu_snapshot()
        gpu = next(g for g in snapshot['gpus'] if g['uuid'] == self.uuid)
        processes = [p for p in snapshot['compute_processes'] if p['gpu_uuid'] == self.uuid]
        return dict(timestamp_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    monotonic=time.monotonic(), gpu=gpu, processes=processes,
                    other_processes=[p for p in processes if p['pid'] != os.getpid()],
                    available_host_ram_bytes=available_memory_bytes())

    def run(self):
        with self.path.open('x') as output:
            while not self.stop_event.is_set():
                try:
                    row = self.sample()
                except Exception as error:
                    self.error = str(error)
                    row = dict(monotonic=time.monotonic(), error=self.error)
                output.write(json.dumps(row)+'\n')
                output.flush()
                self.stop_event.wait(2)

    def close(self):
        self.stop_event.set()
        if self.thread.ident is not None:
            self.thread.join(timeout=22)
