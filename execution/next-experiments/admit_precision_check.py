#!/usr/bin/env python3
"""Reuse the existing queue controller with an additional model-memory guard."""
import importlib.util
from pathlib import Path

path=Path(__file__).with_name('admit_queues.py')
spec=importlib.util.spec_from_file_location('existing_admission',path)
admission=importlib.util.module_from_spec(spec)
spec.loader.exec_module(admission)
original_eligible=admission.eligible
admission.eligible=lambda gpu:original_eligible(gpu) and gpu['index']!=1 and gpu['total_mib']-gpu['used_mib']>=14336

if __name__=='__main__':
    admission.controller()
