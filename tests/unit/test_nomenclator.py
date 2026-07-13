from __future__ import annotations

import unittest
from pathlib import Path

from scraper.nomenclator import (
    NomenclatorError,
    build_act_url,
    iter_table_scope_codes,
    load_nomenclator,
    party_catalog,
    resolve_municipality,
    table_scope_code,
)

FIXTURE = Path(__file__).parents[1] / "fixtures" / "nomenclator_boyaca_min.json"


class NomenclatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = load_nomenclator(FIXTURE)

    def test_resolves_four_required_municipalities_for_both_elections(self) -> None:
        expected = {
            "TUNJA": "0700001",
            "PAIPA": "0700181",
            "SOGAMOSO": "0700277",
            "DUITAMA": "0700079",
        }
        for election in ("CA", "SE"):
            for name, code in expected.items():
                with self.subTest(election=election, name=name):
                    scope = resolve_municipality(self.payload, name.lower(), election)
                    self.assertEqual(scope.code, code)
                    self.assertGreater(scope.table_count, 0)

    def test_generates_six_digit_table_suffix(self) -> None:
        tunja = resolve_municipality(self.payload, "Tunja", "CA")
        self.assertEqual(
            list(iter_table_scope_codes(tunja.positions[0])),
            ["0700001010001000001", "0700001010001000002"],
        )
        self.assertEqual(table_scope_code("0700001010001", 27), "0700001010001000027")

    def test_builds_verified_act_pattern(self) -> None:
        self.assertEqual(
            build_act_url("ca", "0700001"),
            "https://resultadospreccongreso2026.registraduria.gov.co/json/ACT/CA/0700001.json",
        )

    def test_rejects_unknown_election(self) -> None:
        with self.assertRaises(NomenclatorError):
            resolve_municipality(self.payload, "Tunja", "XX")

    def test_party_catalog_uses_runtime_i_not_source_codpar(self) -> None:
        catalog = party_catalog(self.payload)
        self.assertEqual(catalog[5].name, "PARTIDO ALIANZA VERDE")
        self.assertEqual(catalog[5].source_code, "4")

