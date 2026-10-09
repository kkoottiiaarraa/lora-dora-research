"""Cooperative same-user limits for every worker using this module."""
import contextlib
import fcntl
import os
from pathlib import Path


@contextlib.contextmanager
def gpu_lease(uuid, directory=None):
    directory = Path(directory) if directory is not None else (
        Path('/tmp') / ('lora-dora-gpu-locks-' + str(os.getuid())))
    directory.mkdir(mode=0o700, exist_ok=True)
    with contextlib.ExitStack() as stack:
        gpu = stack.enter_context((directory / (uuid + '.lock')).open('a'))
        fcntl.flock(gpu, fcntl.LOCK_EX | fcntl.LOCK_NB)
        permit = None
        for number in range(3):
            candidate = (directory / ('slot-' + str(number) + '.lock')).open('a')
            try:
                fcntl.flock(candidate, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                candidate.close()
                continue
            permit = stack.enter_context(candidate)
            break
        if permit is None:
            raise RuntimeError('Three research GPU workers already active')
        yield
