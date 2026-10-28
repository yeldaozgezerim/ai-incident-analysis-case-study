"""Read-only validation and summary of synthetic incident evidence."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import re

REQUIRED = {"id", "event_time", "recorded_time", "component", "kind", "detail"}


def parse_utc(value):
    if not isinstance(value, str) or not re.fullmatch(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?Z", value
    ):
        raise ValueError("Timestamp must use strict UTC ISO-8601 format")
    parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    if parsed.tzinfo != timezone.utc:
        raise ValueError("Timestamp must be UTC")
    return parsed


def validate(dataset):
    if not isinstance(dataset, dict) or not isinstance(dataset.get("events"), list):
        raise ValueError("Expected object with events array")
    if dataset.get("timezone") != "UTC":
        raise ValueError("Expected UTC timezone")
    if not isinstance(dataset.get("case_id"), str) or not dataset["case_id"].strip():
        raise ValueError("case_id must be a nonempty string")
    if dataset.get("data_classification") != "synthetic_public_example":
        raise ValueError("Only synthetic public example data is accepted")
    events = dataset["events"]
    by_id = {}
    for item in events:
        if not isinstance(item, dict) or not REQUIRED <= item.keys():
            raise ValueError("Event is missing required fields")
        if any(not isinstance(item[key], str) or not item[key].strip() for key in REQUIRED):
            raise ValueError("Required fields must be nonempty strings")
        if item["id"] in by_id:
            raise ValueError("Duplicate event ID")
        by_id[item["id"]] = item
        if parse_utc(item["recorded_time"]) < parse_utc(item["event_time"]):
            raise ValueError("Recorded time precedes event time")
    for item in events:
        is_copy = item["kind"] == "forwarded_copy"
        if is_copy and "duplicate_of" not in item:
            raise ValueError("Forwarded copy must reference original")
        if "duplicate_of" in item:
            target = item["duplicate_of"]
            if not isinstance(target, str) or target not in by_id or target == item["id"]:
                raise ValueError("Invalid duplicate reference")
            if not is_copy:
                raise ValueError("Only forwarded copies may reference duplicates")
            if "duplicate_of" in by_id[target]:
                raise ValueError("Forwarded copy cannot reference forwarded copy")
            if item["event_time"] != by_id[target]["event_time"]:
                raise ValueError("Forwarded copy must preserve original event time")
    return events


def summarize(dataset):
    events = validate(dataset)
    independent = [event for event in events if "duplicate_of" not in event]
    ordered = sorted(independent, key=lambda e: (parse_utc(e["event_time"]), e["id"]))
    return {
        "case_id": dataset["case_id"],
        "total_records": len(events),
        "independent_observations": len(independent),
        "excluded_duplicate_records": len(events) - len(independent),
        "event_kinds": dict(sorted(Counter(e["kind"] for e in independent).items())),
        "timeline": [
            {"id": e["id"], "event_time": e["event_time"], "kind": e["kind"]}
            for e in ordered
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="Path to synthetic incident JSON")
    args = parser.parse_args()
    dataset = json.loads(args.path.read_text(encoding="utf-8"))
    print(json.dumps(summarize(dataset), indent=2))


if __name__ == "__main__":
    main()
