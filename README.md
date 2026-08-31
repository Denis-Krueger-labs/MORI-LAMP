# MORI // LAMP

**Listing Analysis and Matching Pipeline**

MORI // LAMP is a local-first pipeline for analysing job listings against evidence-backed candidate information.

Its purpose is to support truthful applications—not manufacture qualifications.

> The system may identify uncertainty, but it must never invent experience, skills, or evidence.

## Current status

LAMP currently provides:

- Strict Pydantic schemas for jobs and candidate profiles
- Requirements, responsibilities, and application rules
- Evidence-backed and self-reported candidate claims
- Category-aware requirement matching
- CEFR language-level comparison
- Grounding checks against source listing text
- Structured JSON output
- Automation-friendly exit codes
- A passing 13-test regression suite

The local listing extractor is the next major component.

## Principles

### Local first

The planned extractor must run entirely on the user’s computer:

- No candidate or listing data leaves the laptop
- No paid API or usage fees
- No dependency on an external AI service
- Extraction quality should be maximised within the available hardware

### Evidence first

A claim marked as `verified` must contain evidence.

Self-reported claims are never silently promoted to verified matches.

### Preserve meaning

LAMP distinguishes between:

- Requirements
- Responsibilities
- Learning opportunities
- Application instructions

For example, a technology mentioned as something the employee may learn is not automatically treated as an entry requirement.

### Fail visibly

Invalid, contradictory, or ungrounded data should produce a clear failure instead of a confident-looking result.

## Installation

MORI // LAMP requires Python 3.14 or newer.

```powershell
py -V:3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --editable .
```

## Usage

Match a normalized job listing against a candidate profile:

```powershell
mori-lamp match examples\job.normalized.json examples\profile.sample.json
```

A successful run prints structured JSON and exits with code `0`.

Invalid input prints a concise error to stderr and exits with code `2`.

## Matching outcomes

| Outcome | Meaning |
|---|---|
| `verified_matches` | A verified claim satisfies the requirement |
| `needs_evidence` | A relevant claim exists but is only self-reported |
| `unmet_requirements` | A claim exists but does not meet the requirement |
| `unknown_requirements` | No corresponding candidate claim exists |

Claims match requirements using both their normalized name and category. Identical names in unrelated categories do not match.

Language requirements also compare CEFR levels:

```text
A1 < A2 < B1 < B2 < C1 < C2
```

A verified B1 claim therefore cannot satisfy a C1 requirement.

## Data contracts

### Job

A normalized job may contain:

- Source metadata
- Title, company, location, and employment type
- Responsibilities
- Requirements
- Application rules

Requirements preserve information such as:

- Category
- Priority
- Description
- Original source text
- Evidence hints
- Minimum language level

### Profile

A profile contains categorized claims.

Each claim may contain:

- Name
- Category
- Status
- Evidence
- Language level, when applicable

Private candidate material should be stored under:

```text
data/private/
```

That directory is excluded through `.gitignore`.

## Grounding

Normalized listing facts can be checked against the raw source text.

Grounding validation rejects responsibilities, requirements, or application rules whose recorded `source_text` cannot be found in the supplied listing.

This protects later extraction stages from quietly inventing details.

## Tests

Run the complete test suite:

```powershell
python -m unittest discover -s tests -v
```

The current suite covers:

- Strict schema validation
- Unexpected-field rejection
- Evidence requirements
- Multiple claim categories
- Category-aware matching
- Self-reported claim handling
- CEFR language comparison
- Realistic job-fixture semantics
- Source-text grounding
- Fabricated-source rejection

## Project structure

```text
MORI-LAMP/
├── docs/
│   ├── architecture.md
│   └── decisions/
│       └── 0001-local-first-extraction.md
├── examples/
│   ├── job.normalized.json
│   └── profile.sample.json
├── src/
│   └── mori_lamp/
│       ├── cli.py
│       ├── grounding.py
│       ├── matching.py
│       └── models.py
└── tests/
    ├── fixtures/
    ├── test_grounding.py
    ├── test_job_fixture.py
    ├── test_language_levels.py
    ├── test_matching.py
    ├── test_models.py
    └── test_profile_claims.py
```

## Documentation

- [Architecture](docs/architecture.md)
- [ADR 0001: Local-first extraction](docs/decisions/0001-local-first-extraction.md)

## Roadmap

1. Define a provider-independent extractor interface
2. Build a repeatable extraction-quality evaluation
3. Evaluate suitable local runtimes and models
4. Connect extraction to schema and grounding validation
5. Add controlled normalization and aliases
6. Develop explainable fit assessment
7. Generate evidence-linked application support
8. Keep final application decisions under human control
