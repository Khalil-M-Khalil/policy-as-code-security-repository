"""Run the policy-as-code validation suite."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from src.validator import validate_directory


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate policy documents and their audit checklists.")
    parser.add_argument("--policy-dir", default="policies")
    parser.add_argument("--checklist-dir", default="checklists")
    parser.add_argument("--out-dir", default="reports")
    args = parser.parse_args()
    findings, metrics = validate_directory(Path(args.policy_dir), Path(args.checklist_dir))
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = {"metrics": metrics, "findings": [finding.as_dict() for finding in findings]}
    (out_dir / "policy_validation_report.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    pd.DataFrame(payload["findings"]).to_csv(out_dir / "policy_validation_findings.csv", index=False)
    print(json.dumps(metrics, indent=2))
    if not metrics["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
