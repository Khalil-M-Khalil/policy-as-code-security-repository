"""Policy-as-Code validator with human-readable findings."""
from __future__ import annotations

import json
from dataclasses import dataclass

from jsonschema import Draft202012Validator, FormatChecker
from pathlib import Path
from urllib.parse import urlparse


@dataclass(frozen=True)
class Finding:
    policy_id: str
    severity: str
    rule: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {
            "policy_id": self.policy_id,
            "severity": self.severity,
            "rule": self.rule,
            "message": self.message,
        }


def _is_url(value: object) -> bool:
    parsed = urlparse(str(value))
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def validate_policy(policy: dict, checklist: dict) -> list[Finding]:
    findings: list[Finding] = []
    policy_id = str(policy.get("policy_id", "UNKNOWN"))
    required = ["policy_id", "title", "version", "status", "owner", "review_cadence", "effective_date", "scope", "principles", "requirements", "exceptions", "references"]
    for field in required:
        if not policy.get(field):
            findings.append(Finding(policy_id, "ERROR", "POL-001", f"Required policy field is missing: {field}"))
    if policy.get("status") not in {"draft", "approved", "retired"}:
        findings.append(Finding(policy_id, "ERROR", "POL-002", "Status must be draft, approved, or retired."))
    if len(policy.get("principles", [])) < 3:
        findings.append(Finding(policy_id, "ERROR", "POL-003", "Policy must contain at least three principles."))
    requirements = policy.get("requirements", [])
    req_ids = {item.get("id") for item in requirements}
    if len(req_ids) != len(requirements):
        findings.append(Finding(policy_id, "ERROR", "POL-004", "Requirement IDs must be unique."))
    for requirement in requirements:
        for field in ["id", "statement", "control_mappings", "evidence", "accountable_role"]:
            if not requirement.get(field):
                findings.append(Finding(policy_id, "ERROR", "POL-005", f"Requirement {requirement.get('id', '?')} is missing {field}."))
        if len(requirement.get("control_mappings", [])) == 0:
            findings.append(Finding(policy_id, "ERROR", "POL-006", f"Requirement {requirement.get('id', '?')} has no control mapping."))
    for reference in policy.get("references", []):
        if not _is_url(reference.get("url")):
            findings.append(Finding(policy_id, "ERROR", "POL-007", f"Reference {reference.get('identifier', '?')} has an invalid URL."))
    exceptions = policy.get("exceptions", [])
    for exception in exceptions:
        if int(exception.get("expiry_days", 0)) <= 0:
            findings.append(Finding(policy_id, "ERROR", "POL-008", f"Exception {exception.get('id', '?')} must expire in a positive number of days."))
        if not exception.get("compensating_control"):
            findings.append(Finding(policy_id, "ERROR", "POL-009", f"Exception {exception.get('id', '?')} lacks a compensating control."))
    checklist_items = checklist.get("items", [])
    checklist_req_ids = {item.get("requirement_id") for item in checklist_items}
    missing_checks = sorted(req_ids - checklist_req_ids)
    if missing_checks:
        findings.append(Finding(policy_id, "ERROR", "CHK-001", f"Requirements missing checklist coverage: {', '.join(missing_checks)}"))
    for item in checklist_items:
        if not item.get("test") or not item.get("evidence_expected") or not item.get("owner"):
            findings.append(Finding(policy_id, "ERROR", "CHK-002", f"Checklist item {item.get('check_id', '?')} is incomplete."))
    if policy.get("status") == "approved" and not policy.get("approver"):
        findings.append(Finding(policy_id, "ERROR", "POL-010", "Approved policies must identify an approver."))
    if not findings:
        findings.append(Finding(policy_id, "PASS", "POL-000", "Policy and checklist passed all automated checks."))
    return findings


def validate_directory(policy_dir: Path, checklist_dir: Path) -> tuple[list[Finding], dict[str, object]]:
    all_findings: list[Finding] = []
    policy_count = 0
    schema_path = policy_dir.parent / "schemas" / "policy.schema.json"
    schema_validator = None
    if schema_path.exists():
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        schema_validator = Draft202012Validator(schema, format_checker=FormatChecker())
    for policy_path in sorted(policy_dir.glob("*.json")):
        if policy_path.name.endswith(".schema.json"):
            continue
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
        policy_count += 1
        if schema_validator is not None:
            for error in sorted(schema_validator.iter_errors(policy), key=lambda item: list(item.path)):
                all_findings.append(Finding(policy.get("policy_id", "UNKNOWN"), "ERROR", "SCHEMA-001", error.message))
        checklist_path = checklist_dir / policy_path.name
        if not checklist_path.exists():
            all_findings.append(Finding(policy.get("policy_id", "UNKNOWN"), "ERROR", "CHK-000", f"No checklist found for {policy_path.name}."))
            continue
        checklist = json.loads(checklist_path.read_text(encoding="utf-8"))
        all_findings.extend(validate_policy(policy, checklist))
    errors = [item for item in all_findings if item.severity == "ERROR"]
    return all_findings, {"policies": policy_count, "findings": len(all_findings), "errors": len(errors), "passed": len(errors) == 0}
