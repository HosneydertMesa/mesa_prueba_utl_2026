from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from scraper.act_parser import ActParseError, parse_table_result

FIXTURES = Path(__file__).parents[1] / "fixtures"


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


class ActParserTests(unittest.TestCase):
    def test_parses_camera_table_and_normalizes_names(self) -> None:
        result = parse_table_result(load_fixture("act_ca_mesa_min.json"), "CA")
        self.assertEqual(result.scope_code, "0700001010001000001")
        self.assertEqual((result.census, result.voters, result.valid_votes), (100, 80, 75))
        self.assertEqual((result.party_rows, result.candidate_rows), (2, 4))
        candidate = result.parties[0].candidates[1]
        self.assertEqual(candidate.source_name, "ANA MARÍA PÉREZ LÓPEZ")
        self.assertEqual(candidate.normalized_name, "ANA MARIA PEREZ LOPEZ")
        self.assertFalse(candidate.is_list)

    def test_parses_senate_default_chamber(self) -> None:
        result = parse_table_result(load_fixture("act_se_mesa_min.json"), "SE")
        self.assertEqual([party.code for party in result.parties], [57, 92])
        self.assertEqual(sum(party.votes for party in result.parties), 70)

    def test_rejects_candidate_sum_mismatch(self) -> None:
        payload = copy.deepcopy(load_fixture("act_ca_mesa_min.json"))
        payload["camaras"][0]["partotabla"][0]["act"]["cantotabla"][0]["vot"] = "9"
        with self.assertRaisesRegex(ActParseError, "suma de candidatos inconsistente"):
            parse_table_result(payload, "CA")

    def test_preserves_source_census_anomaly_for_later_audit(self) -> None:
        payload = copy.deepcopy(load_fixture("act_ca_mesa_min.json"))
        payload["totales"]["act"]["centota"] = "62"

        result = parse_table_result(payload, "CA")

        self.assertEqual((result.census, result.voters), (62, 80))

    def test_rejects_response_for_other_scope(self) -> None:
        with self.assertRaisesRegex(ActParseError, "ámbito inesperado"):
            parse_table_result(
                load_fixture("act_ca_mesa_min.json"),
                "CA",
                expected_scope_code="0700001010001000002",
            )
