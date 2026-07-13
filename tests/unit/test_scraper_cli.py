from __future__ import annotations

import io
import unittest
from pathlib import Path

from scraper.nomenclator import NomenclatorError, load_nomenclator
from scraper.scraper import (
    BONUS_MUNICIPALITIES,
    DEFAULT_MUNICIPALITIES,
    parse_municipalities,
    run_preflight,
    select_municipalities,
)

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

    def test_accepts_and_preflights_bonus_municipalities(self) -> None:
        selected = select_municipalities(
            DEFAULT_MUNICIPALITIES,
            include_bonus=True,
        )
        output = io.StringIO()
        summary = run_preflight(load_nomenclator(FIXTURE), selected, output=output)
        self.assertEqual(len(summary.municipalities), 7)
        self.assertEqual(summary.table_count, 8)
        self.assertIn("PREFLIGHT 7/7 municipios", output.getvalue())

    def test_bonus_selection_is_deterministic_and_deduplicated(self) -> None:
        selected = select_municipalities(
            [*DEFAULT_MUNICIPALITIES, "chiquinquirá"],
            include_bonus=True,
        )
        self.assertEqual(selected, (*DEFAULT_MUNICIPALITIES, *BONUS_MUNICIPALITIES))

    def test_nomenclator_rejects_municipality_outside_boyaca(self) -> None:
        with self.assertRaises(NomenclatorError):
            run_preflight(load_nomenclator(FIXTURE), ("BOGOTA",))

