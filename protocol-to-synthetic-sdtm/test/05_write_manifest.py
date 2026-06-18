#!/usr/bin/env python3
"""Write run manifest: pinned versions, parameters, and content hashes of every artifact."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

HERE = Path(__file__).parent
NCT_ID = os.environ.get("NCT_ID")
if not NCT_ID:
    raw_files = sorted((HERE / "00_raw").glob("NCT*.json"))
    if not raw_files:
        raise FileNotFoundError("No 00_raw/NCT*.json file found for manifest input.")
    NCT_ID = raw_files[0].stem

SUBJECT_COUNT = int(os.environ.get("SUBJECT_COUNT", "40"))
RANDOM_SEED = int(os.environ.get("RANDOM_SEED", "1234"))
SDTMIG_VERSION = os.environ.get("SDTMIG_VERSION", "3.4")
CT_PACKAGE_DATE = os.environ.get("CT_PACKAGE_DATE", "sdtmct-2026-03-27")
COHORT_1_N = round(SUBJECT_COUNT * 0.6)
remaining_subjects = SUBJECT_COUNT - COHORT_1_N
COHORT_2_N = remaining_subjects // 2
COHORT_3_N = remaining_subjects - COHORT_2_N

RAW = json.loads((HERE / f"00_raw/{NCT_ID}.json").read_text())
VER = json.loads((HERE / "00_raw/ctgov_version.json").read_text())


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


artifacts = {}
for p in sorted(HERE.rglob("*")):
    if p.is_file() and "__pycache__" not in p.parts and p.suffix in (".json", ".csv", ".pdf", ".py"):
        artifacts[str(p.relative_to(HERE))] = {"sha256_16": sha(p), "bytes": p.stat().st_size}

manifest = {
    "pipeline": "protocol-to-synthetic-SDTM (MVP test run)",
    "input": {"nctId": NCT_ID,
              "sponsorStudyId": RAW["protocolSection"]["identificationModule"]["orgStudyIdInfo"]["id"],
              "title": RAW["protocolSection"]["identificationModule"]["briefTitle"]},
    "provenance": {
        "ctgovApiVersion": VER.get("apiVersion"),
        "ctgovDataTimestamp": VER.get("dataTimestamp"),
        "protocolDocument": "Prot_000.pdf (Clinical Study Protocol v3.0, dated 2021-03-03)",
        "protocolSoAPages": "20-24",
    },
    "standards": {
        "usdmVersion": "3.0.0",
        "ctPackage": CT_PACKAGE_DATE,
        "sdtmigVersion": SDTMIG_VERSION,
    },
    "parameters": {"subjectCount": SUBJECT_COUNT, "randomSeed": RANDOM_SEED,
                   "cohorts": {"Cohort 1": COHORT_1_N, "Cohort 2": COHORT_2_N, "Cohort 3": COHORT_3_N},
                   "crossover": "two-way (AB/BA sequences)"},
    "tools": {"ctgov": "ctgov MCP (ClinicalTrials.gov API v2)",
              "cdisclib": "cdisclib client/MCP (CDISC Library API)"},
    "stages": {
        "1_fetch": f"00_raw/{NCT_ID}.json (+ protocol PDF when registered)",
        "2_usdm": "01_usdm/usdm.json (+ soa.json)",
        "3_4_sdtm_spec": "02_sdtm_spec/sdtm_spec.json (+ ct_cache.json, coverage.json)",
        "5_populate": "03_synthetic_sdtm/*.csv (+ lineage.json, datasets_summary.json)",
        "6a_validate": "03_synthetic_sdtm/validation_report.json",
        "6b_export_core": "06_sdtm_xpt/*.xpt + 07_core_report/{core_sdtmig34.json, summary.json}",
    },
    "artifacts": artifacts,
}
(HERE / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
print(f"Wrote manifest.json with {len(artifacts)} artifacts hashed.")
