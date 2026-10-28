import copy
import json
import unittest
from pathlib import Path
from src.analyze_incident import summarize, validate

FIXTURE = json.loads((Path(__file__).resolve().parents[1] / "data/events.json").read_text(encoding="utf-8"))


class TestIncidentAnalysis(unittest.TestCase):
    def changed(self, index, key, value):
        data = copy.deepcopy(FIXTURE)
        data["events"][index][key] = value
        return data

    def test_counts(self):
        report = summarize(FIXTURE)
        self.assertEqual((report["total_records"], report["independent_observations"], report["excluded_duplicate_records"]), (5, 4, 1))

    def test_order(self):
        self.assertEqual(summarize(FIXTURE)["timeline"][0]["id"], "E05")

    def test_kind_counts(self):
        self.assertEqual(summarize(FIXTURE)["event_kinds"]["timeout"], 1)

    def test_duplicate_id(self):
        with self.assertRaises(ValueError): validate(self.changed(1, "id", "E01"))

    def test_unknown_reference(self):
        with self.assertRaises(ValueError): validate(self.changed(2, "duplicate_of", "UNKNOWN"))

    def test_wrong_reference_type(self):
        with self.assertRaises(ValueError): validate(self.changed(2, "duplicate_of", ["E02"]))

    def test_self_reference(self):
        with self.assertRaises(ValueError): validate(self.changed(2, "duplicate_of", "E03"))

    def test_invalid_timestamp(self):
        with self.assertRaises(ValueError): validate(self.changed(0, "event_time", "invalid"))

    def test_non_strict_timestamp(self):
        with self.assertRaises(ValueError): validate(self.changed(0, "event_time", "2026-01-15 10:00:00Z"))

    def test_recorded_before_event(self):
        with self.assertRaises(ValueError): validate(self.changed(0, "recorded_time", "2026-01-15T09:00:00Z"))

    def test_missing_field(self):
        data = copy.deepcopy(FIXTURE)
        del data["events"][0]["kind"]
        with self.assertRaises(ValueError): validate(data)

    def test_missing_copy_reference(self):
        data = copy.deepcopy(FIXTURE)
        del data["events"][2]["duplicate_of"]
        with self.assertRaises(ValueError): validate(data)

    def test_copy_time_mismatch(self):
        with self.assertRaises(ValueError): validate(self.changed(2, "event_time", "2026-01-15T10:05:00Z"))

    def test_wrong_kind(self):
        with self.assertRaises(ValueError): validate(self.changed(2, "kind", "timeout"))

    def test_nonstring_field(self):
        with self.assertRaises(ValueError): validate(self.changed(0, "detail", 42))

    def test_timezone(self):
        data = copy.deepcopy(FIXTURE)
        data["timezone"] = "Europe/Istanbul"
        with self.assertRaises(ValueError): validate(data)

    def test_classification(self):
        data = copy.deepcopy(FIXTURE)
        data["data_classification"] = "internal"
        with self.assertRaises(ValueError): validate(data)

    def test_missing_case_id(self):
        data = copy.deepcopy(FIXTURE)
        del data["case_id"]
        with self.assertRaises(ValueError): validate(data)

    def test_empty_events(self):
        data = copy.deepcopy(FIXTURE)
        data["events"] = []
        self.assertEqual(summarize(data)["independent_observations"], 0)


if __name__ == "__main__":
    unittest.main()
