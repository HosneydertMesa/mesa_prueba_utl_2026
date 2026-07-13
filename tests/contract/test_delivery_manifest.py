from __future__ import annotations

import json
import unittest
from pathlib import Path

from outputs.generar_manifest import (
    GENERATOR_PROVENANCE,
    META,
    build_example_manifest,
)

ROOT = Path(__file__).resolve().parents[2]
OUTPUTS = ROOT / "outputs"


class DeliveryManifestContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = json.loads(
            (OUTPUTS / "evaluation_manifest.json").read_text(encoding="utf-8")
        )
        cls.example = json.loads(
            (OUTPUTS / "evaluation_manifest.example.json").read_text(encoding="utf-8")
        )

    def test_manifest_closes_pdf_observable_contract(self) -> None:
        self.assertEqual(self.manifest["generator_provenance"], GENERATOR_PROVENANCE)
        self.assertEqual(self.manifest["overall_status"], "OK")
        self.assertEqual(self.manifest["meta"], META)
        self.assertEqual(self.manifest["scope"]["municipalities_loaded"], 4)
        self.assertEqual(self.manifest["scope"]["municipalities_expected"], 4)
        self.assertEqual(self.manifest["scope"]["tables_expected"], 1107)
        self.assertEqual(set(self.manifest["sql_tasks"]), {"3.1", "3.2", "3.3"})
        self.assertTrue(
            all(task["status"] == "OK" for task in self.manifest["sql_tasks"].values())
        )
        self.assertEqual(
            self.manifest["scatter_statistics"]["stdout"],
            "r=0.964 | pendiente=0.933 | n_mesas=1107",
        )
        self.assertEqual(self.manifest["sample_data"]["status"], "OK")
        self.assertFalse(self.manifest["sample_data"]["official_utl_sample"])

    def test_example_is_generated_from_the_same_top_level_schema(self) -> None:
        generated_example = build_example_manifest()
        self.assertEqual(self.example, generated_example)
        self.assertEqual(set(self.example), set(self.manifest))


if __name__ == "__main__":
    unittest.main()
