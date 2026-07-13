from __future__ import annotations

import io
import unittest
from pathlib import Path

from scraper.nomenclator import load_nomenclator
from scraper.scraper import parse_municipalities, run_preflight

FIXTURE = Path(__file__).parents[1] / "fixtures" / "nomenclator_boyaca_min.json"


class ScraperCliTests(unittest.TestCase):
    def test_preflight_counts_without_network_or_database(self) -> None:
        output = io.StringIO()
        summary = run_preflight(
            load_nomenclator(FIXTURE),
            ("TUNJA", "PAIPA", "SOGAMOSO", "DUITAMA"),
            output=output,
        )
        self.assertEqual(summary.table_count, 5)
        self.assertEqual(summary.act_request_count, 10)
        self.assertIn("PREFLIGHT 4/4 municipios", output.getvalue())

    def test_normalizes_and_deduplicates_municipalities(self) -> None:
        self.assertEqual(parse_municipalities(["tunja", " TUNJA ", "paipa"]), ("TUNJA", "PAIPA"))

    def test_rejects_municipality_outside_scope(self) -> None:
        with self.assertRaises(ValueError):
            parse_municipalities(["Bogotá"])

