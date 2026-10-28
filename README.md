# Incident Evidence Analysis — Portfolio Demonstration

A read-only Python example of structured incident-evidence validation, chronological reconstruction, and duplicate-aware counting.

**Provenance:** This project is informed by practical AI evaluation and incident-analysis exercises. All published events are independently authored **synthetic demonstration data**, not original client records or proof of personally managing a live payment incident.

## Run

Requires Python 3.10+; no third-party packages.

```bash
python -m src.analyze_incident data/events.json
python -m unittest discover -s tests -v
```

## What it does

- Checks required fields and strict UTC timestamps.
- Rejects duplicate IDs and invalid forwarded-copy references.
- Sorts by event time rather than recording time.
- Excludes explicitly marked forwarded copies from independent observation counts.
- Emits a JSON summary without modifying any system.

**Limitations:** Explicit metadata is required to detect duplicates. Temporal proximity does not establish causation. Valid JSON does not prove evidence authenticity. No production actions or root-cause claims are made.

See [methodology](docs/methodology.md) and [publication review](docs/publication-review.md).
