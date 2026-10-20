from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import build_data  # noqa: E402


class DashboardDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = build_data.load_inputs()
        build_data.validate(cls.payload)

    def test_three_periods_and_store_counts(self):
        self.assertEqual(len(self.payload["periods"]), 3)
        for period in self.payload["periods"].values():
            self.assertEqual(period["meta"]["storeTotal"], 60)
            self.assertEqual(len(period["stores"]), 60)

    def test_metric_contract_and_bounds(self):
        for period in self.payload["periods"].values():
            for store in period["stores"]:
                self.assertEqual(set(store["metrics"]), set(build_data.ALL_METRICS))
                self.assertTrue(1 <= store["metrics"]["channel_a_score"]["cur"] <= 5)
                self.assertTrue(1 <= store["metrics"]["channel_b_score"]["cur"] <= 5)
                self.assertGreaterEqual(store["metrics"]["channel_a_repeat"]["cur"], 0)
                self.assertLessEqual(store["metrics"]["channel_b_cancel"]["cur"], 0.02)

    def test_synthetic_identifiers_only(self):
        for period in self.payload["periods"].values():
            ids = [store["id"] for store in period["stores"]]
            self.assertTrue(all(value.startswith(("Store_A", "Store_B")) for value in ids))
            self.assertEqual(len(ids), len(set(ids)))

    def test_aggregate_is_reproducible_from_store_rows(self):
        period = self.payload["periods"][self.payload["defaultPeriod"]]
        region = next(item for item in period["region_summary"] if item["name"] == "Region_A")
        stores = [store for store in period["stores"] if store["region"] == "Region_A"]
        expected = sum(store["metrics"]["channel_a_score"]["cur"] for store in stores) / len(stores)
        self.assertAlmostEqual(region["metrics"]["channel_a_score"]["cur"], expected, places=3)

    def test_payload_uses_only_public_demo_labels(self):
        text = json.dumps(self.payload, ensure_ascii=False)
        self.assertIn("Store_A001", text)
        self.assertIn("Synthetic demo data", text)
        self.assertNotRegex(text, r"C:[\\/]Users[\\/]")


if __name__ == "__main__":
    unittest.main()
