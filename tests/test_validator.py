import copy
import json
from pathlib import Path

from src.validator import validate_directory, validate_policy

ROOT = Path(__file__).parents[1]


def test_all_policies_pass():
    findings, metrics = validate_directory(ROOT / "policies", ROOT / "checklists")
    assert metrics == {"policies": 3, "findings": 3, "errors": 0, "passed": True}
    assert all(item.severity == "PASS" for item in findings)


def test_missing_checklist_is_error():
    policy = json.loads((ROOT / "policies/access_control.json").read_text())
    checklist = json.loads((ROOT / "checklists/access_control.json").read_text())
    broken = copy.deepcopy(checklist)
    broken["items"] = broken["items"][:-1]
    findings = validate_policy(policy, broken)
    assert any(item.rule == "CHK-001" and item.severity == "ERROR" for item in findings)


def test_invalid_reference_is_error():
    policy = json.loads((ROOT / "policies/data_classification.json").read_text())
    checklist = json.loads((ROOT / "checklists/data_classification.json").read_text())
    policy["references"][0]["url"] = "not-a-url"
    findings = validate_policy(policy, checklist)
    assert any(item.rule == "POL-007" for item in findings)


def test_approved_policy_requires_approver():
    policy = json.loads((ROOT / "policies/incident_response.json").read_text())
    checklist = json.loads((ROOT / "checklists/incident_response.json").read_text())
    policy["approver"] = ""
    findings = validate_policy(policy, checklist)
    assert any(item.rule == "POL-010" for item in findings)
