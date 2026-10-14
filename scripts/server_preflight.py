#!/usr/bin/env python3
"""Run from a fresh research checkout; inspects, never changes GPU processes."""
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lora_dora_study.server import preflight, write_json

parser = argparse.ArgumentParser()
parser.add_argument("--directory", default=".")
parser.add_argument("--output")
args = parser.parse_args()
report = preflight(args.directory)
if args.output:
    write_json(args.output, report)
print(json.dumps(report, indent=2, ensure_ascii=False))
