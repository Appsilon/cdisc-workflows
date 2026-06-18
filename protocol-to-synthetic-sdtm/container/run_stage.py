#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


APP_TEST_DIR = Path("/app/protocol-to-synthetic-sdtm/test")
WORKSPACE_TEST_DIR = Path("/workspace")
OUTPUT_DIR = Path("/output")


def find_input_value(value: object, key: str) -> object | None:
    if isinstance(value, dict):
        if key in value:
            return value[key]
        for child in value.values():
            found = find_input_value(child, key)
            if found is not None:
                return found
    if isinstance(value, list):
        for child in value:
            found = find_input_value(child, key)
            if found is not None:
                return found
    return None


def step_env() -> dict[str, str]:
    input_path = OUTPUT_DIR / "input.json"
    if not input_path.exists():
        return {}
    try:
        step_input = json.loads(input_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}

    mapping = {
        "nctId": "NCT_ID",
        "subjectCount": "SUBJECT_COUNT",
        "randomSeed": "RANDOM_SEED",
        "sdtmigVersion": "SDTMIG_VERSION",
        "ctPackageDate": "CT_PACKAGE_DATE",
    }
    env: dict[str, str] = {}
    for input_key, env_key in mapping.items():
        found = find_input_value(step_input, input_key)
        if found is not None:
            env[env_key] = str(found)
    return env


def copy_static_pipeline() -> None:
    if (WORKSPACE_TEST_DIR / "00_fetch_study.py").exists():
        return

    def ignore_generated(_dir: str, names: list[str]) -> set[str]:
        generated = {
            "00_raw",
            "01_usdm",
            "02_sdtm_spec",
            "03_synthetic_sdtm",
            "06_sdtm_xpt",
            "manifest.json",
        }
        return generated.intersection(names)

    WORKSPACE_TEST_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copytree(APP_TEST_DIR, WORKSPACE_TEST_DIR, ignore=ignore_generated, dirs_exist_ok=True)


def write_result(stage: str, returncode: int) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    status = "success" if returncode == 0 else "failed"
    payload = {
        "status": status,
        "stage": stage,
        "workspace": str(WORKSPACE_TEST_DIR),
    }
    (OUTPUT_DIR / "result.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: run_stage.py <stage-script>", file=sys.stderr)
        return 2

    stage = sys.argv[1]
    copy_static_pipeline()
    stage_path = WORKSPACE_TEST_DIR / stage
    if not stage_path.exists():
        print(f"stage script not found: {stage_path}", file=sys.stderr)
        write_result(stage, 1)
        return 1

    if stage_path.suffix == ".sh":
        command = ["bash", str(stage_path)]
    else:
        command = [sys.executable, str(stage_path)]

    completed = subprocess.run(
        command,
        cwd=WORKSPACE_TEST_DIR,
        env={**os.environ, **step_env()},
        check=False,
    )
    write_result(stage, completed.returncode)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
