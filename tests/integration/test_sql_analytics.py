from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from db.database import initialize_database
from db.etl import load_act_payload
from scraper.nomenclator import load_nomenclator, resolve_municipality

FIXTURES = Path(__file__).parents[1] / "fixtures"
SQL_DIR = Path(__file__).parents[2] / "sql"


def fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


class SqlAnalyticsIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.connection = initialize_database(Path(self.temporary.name) / "analytics.db")
        nomenclator = load_nomenclator(FIXTURES / "nomenclator_boyaca_min.json")
        ca_payload = copy.deepcopy(fixture("act_ca_mesa_min.json"))
        green = ca_payload["camaras"][0]["partotabla"][0]["act"]
        green["cantotabla"][0]["vot"] = "10"
        green["cantotabla"][1]["vot"] = "30"
        green["cantotabla"][2]["vot"] = "0"

        for corporation, payload in (("CA", ca_payload), ("SE", fixture("act_se_mesa_min.json"))):
            municipality = resolve_municipality(nomenclator, "TUNJA", corporation)
            load_act_payload(
                self.connection,
                payload,
                nomenclator,
                municipality,
                municipality.positions[0],
                corporation,
                expected_scope_code=payload["amb"],
                source_url=f"fixture://{corporation}",
            )

    def tearDown(self) -> None:
        self.connection.close()
        self.temporary.cleanup()

    def _query(self, filename: str):
        sql = (SQL_DIR / filename).read_text(encoding="utf-8")
        return self.connection.execute(sql).fetchall()

    def test_3_1_calculates_green_ratio_by_position(self) -> None:
        rows = self._query("tarea_3_1.sql")

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][0:5], ("TUNJA", "0700001010001", "PUESTO TUNJA", 40, 45))
        self.assertAlmostEqual(rows[0][5], 1.125)

    def test_3_2_uses_strict_sixty_percent_threshold(self) -> None:
        rows = self._query("tarea_3_2.sql")

        self.assertEqual(len(rows), 1)
        self.assertEqual((rows[0][5], rows[0][6], rows[0][8]), ("CA", 5, "101"))
        self.assertAlmostEqual(rows[0][12], 0.75)

        self.connection.execute(
            "UPDATE resultados_candidato SET votos = 24 WHERE candidato_id = "
            "(SELECT ca.id FROM candidatos ca JOIN partidos pa ON pa.id = ca.partido_id "
            "WHERE pa.corporacion = 'CA' AND pa.codpar = 5 AND ca.codcan = '101')"
        )
        self.connection.execute(
            "UPDATE resultados_candidato SET votos = 16 WHERE candidato_id = "
            "(SELECT ca.id FROM candidatos ca JOIN partidos pa ON pa.id = ca.partido_id "
            "WHERE pa.corporacion = 'CA' AND pa.codpar = 5 AND ca.codcan = '0')"
        )
        self.assertEqual(self._query("tarea_3_2.sql"), [])

    def test_3_3_applies_candidate_share_to_homologated_senate_votes(self) -> None:
        rows = self._query("tarea_3_3.sql")

        self.assertEqual((rows[0][0], rows[0][2]), (5, "101"))
        self.assertEqual(rows[0][4:6], (30, 1))
        self.assertAlmostEqual(rows[0][6], 33.75)
