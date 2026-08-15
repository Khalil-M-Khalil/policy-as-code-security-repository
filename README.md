# Policy-as-Code Security Policy Repository

A portfolio-grade repository of original security policy documents and machine-checkable audit checklists. The project turns policy governance into a versioned, reviewable, testable artifact instead of leaving policy content as an unmanaged document.

The initial release contains three policies: **Access Control and Identity Governance**, **Cybersecurity Incident Response**, and **Information Classification and Handling**. Each policy is paired with a checklist whose test steps, expected evidence, owner, and review frequency can be validated automatically.

> The policy text in this repository is original demonstration content. Framework identifiers and references are used for alignment and traceability; this repository does not reproduce copyrighted standard text or claim certification.

## What this project demonstrates

Security policies often fail operationally when they contain principles but no accountable owner, evidence expectation, review cadence, exception path, or measurable audit test. This repository addresses that gap by treating each policy as structured data with a human-readable control narrative and a machine-checkable contract.

The validator checks required metadata, approved status requirements, unique requirement IDs, control mappings, evidence expectations, exception expiry and compensating controls, valid reference URLs, and complete checklist coverage. A successful result means the policy package is structurally complete according to this repository’s rules; it does not prove that the organization has implemented the policy.

## Framework alignment

The design uses NIST SP 800-53 Rev. 5 control families as a public control-reference lens. NIST describes SP 800-53 as a flexible and customizable catalog, and specifically warns that mappings and crosswalks are indicative relationships rather than one-to-one equivalencies [1].

The Incident Response policy uses NIST SP 800-61 Rev. 3, published in April 2025, as its primary incident-response reference. NIST describes Rev. 3 as integrating incident-response recommendations with cybersecurity risk management and the NIST CSF 2.0 Community Profile [2].

ISO/IEC 27001:2022 identifiers are used as high-level alignment references for access governance and information handling. COBIT 2019 identifiers are used where governance, service management, and measurement context is useful. ISACA describes COBIT as a governance and management framework for enterprise information and technology that can integrate with other standards and guidance [3].

| Policy | Primary operational lens | Example reference identifiers |
| --- | --- | --- |
| Access Control | Identity lifecycle, least privilege, MFA, privileged access, recertification | NIST AC/IA/AU; ISO A.5.15–A.5.18; COBIT APO13/DSS05 |
| Incident Response | Preparation, triage, evidence, containment, recovery, communications, lessons learned | NIST SP 800-61 Rev. 3; NIST IR/AU; COBIT DSS02/DSS04 |
| Data Classification | Ownership, classification, handling, sharing, retention, secure disposal | NIST AC/MP/RA/SC; ISO A.5.12/A.5.14/A.8.10; COBIT APO14 |

## Repository structure

```text
.
├── checklists/
│   ├── access_control.json
│   ├── data_classification.json
│   └── incident_response.json
├── policies/
│   ├── access_control.json
│   ├── data_classification.json
│   └── incident_response.json
├── schemas/
│   └── policy.schema.json
├── src/
│   └── validator.py
├── tests/
│   └── test_validator.py
├── validate_policies.py
├── requirements.txt
└── README.md
```

## Policy document model

Each policy contains a stable policy identifier, title, version, status, owner, approver, review cadence, effective date, scope, principles, requirements, exception rules, and reference metadata. Every requirement includes an original policy statement, public control mappings, expected evidence, and an accountable role.

The exception model requires an approver, an expiry period, and a compensating control. This makes exceptions temporary risk decisions rather than informal comments. The checklist model links back to each requirement and adds a test, expected evidence, owner, and frequency.

## Run the validator

The project requires Python 3.10 or newer. Install the dependencies in an isolated environment:

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
python validate_policies.py
```

A passing run produces a JSON and CSV report under `reports/`. The command exits with status 1 when a policy package fails validation, which makes it suitable for a CI gate.

Run automated tests with:

```bash
pytest
```

The included tests cover all three policy packages, missing checklist coverage, invalid reference URLs, and missing approvers on approved policies.

## Example validation result

The included policy packages are intentionally complete and pass the automated rules. A representative result is:

```json
{
  "policies": 3,
  "findings": 3,
  "errors": 0,
  "passed": true
}
```

Each policy receives a `PASS` finding when all requirements have checklist coverage and the package satisfies the validator’s metadata, exception, reference, and evidence rules.

## Policy quality and audit value

The repository provides a practical bridge between written governance and assurance activity. A GRC analyst can review the policy narrative, an control owner can use the evidence expectations, an auditor can sample the checklist tests, and an engineering team can run the validator as a pull-request gate. Version control also provides an observable history of policy changes, review ownership, and control-mapping decisions.

The value is not that a JSON file creates compliance automatically. The value is that a policy package becomes **structured, reviewable, testable, and traceable** before it is distributed to the organization.

## Limitations and responsible use

This is a portfolio demonstration and a starting template. It is not legal advice, a certification package, a complete ISO/IEC 27001 ISMS, a complete NIST SP 800-53 implementation, or a COBIT assessment. Organizations must tailor wording, roles, retention periods, notification requirements, data protection obligations, and approval paths to their jurisdiction, risk appetite, contracts, and operating model.

The validator checks structure and completeness, not real-world implementation. A passing policy can still be ineffective if the organization lacks training, technical enforcement, monitoring, evidence retention, or accountable ownership. Standards and framework publications should be obtained and interpreted from their official sources.

## Roadmap

Future releases can add YAML support, JSON Schema validation through `jsonschema`, policy-to-control crosswalk exports, approval workflow metadata, version-diff reports, evidence sampling status, and GitHub Actions. A future release may also add an OSCAL export where the target profile and licensing boundary are clearly defined.

## References

[1]: https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final "NIST SP 800-53 Rev. 5 — Security and Privacy Controls"

[2]: https://csrc.nist.gov/pubs/sp/800/61/r3/final "NIST SP 800-61 Rev. 3 — Incident Response Recommendations"

[3]: https://www.isaca.org/resources/cobit "ISACA — COBIT Resources"

[4]: https://www.iso.org/standard/27001 "ISO/IEC 27001:2022 overview"

## License

MIT. See `LICENSE` for details.
