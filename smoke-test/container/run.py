#!/usr/bin/env python3
"""Smoke test — writes hello.txt to /output and prints env diagnostics."""
import json
import os
import sys
from pathlib import Path

output_dir = Path("/output")
output_dir.mkdir(parents=True, exist_ok=True)

# Collect env keys (values redacted) and write to output
env_keys = sorted(os.environ.keys())
diagnostics = {
    "status": "ok",
    "env_keys": env_keys,
    "python": sys.version,
}

(output_dir / "hello.txt").write_text("hello from smoke-test container\n")
(output_dir / "diagnostics.json").write_text(json.dumps(diagnostics, indent=2))

print("smoke-test container ran successfully")
print(f"wrote {output_dir / 'hello.txt'} and {output_dir / 'diagnostics.json'}")
