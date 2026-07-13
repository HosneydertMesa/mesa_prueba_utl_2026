from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from db.database import assert_integrity, initialize_database
from db.etl import EtlError, load_act_payload
from scraper.nomenclator import load_nomenclator, resolve_municipality

FIXTURES = Path(__file__).parents[1] / "fixtures"


def fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


class ActEtlIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.connection = initialize_database(Path(self.temporary.name) / "etl.db")
        self.nomenclator = load_nomenclator(FIXTURES / "nomenclator_boyaca_min.json")
        self.municipality = resolve_municipality(self.nomenclator, "TUNJA", "CA")
        self.position = self.municipality.positions[0]

    def tearDown(self) -> None:
        self.connection.close()
        self.temporary.cleanup()

    def _load(self, payload: dict, corporation: str):
        return load_act_payload(
            self.connection,
            payload,
            self.nomenclator,
            self.municipality,
            self.position,
            corporation,
            expected_scope_code=payload["amb"],
            source_url=f"fixture://{corporation}",
            source_etag='"fixture-v1"',
        )

    def test_second_execution_inserts_zero_duplicate_facts(self) -> None:
        payload = fixture("act_ca_mesa_min.json")
        first = self._load(payload, "CA")
        second = self._load(payload, "CA")

        self.assertEqual((first.rows_read, first.rows_inserted, first.rows_skipped), (7, 7, 0))
        self.assertEqual((second.rows_read, second.rows_inserted, second.rows_skipped), (7, 0, 7))
        expected_counts = {
            "municipios": 1,
            "puestos": 1,
            "mesas": 1,
            "partidos": 2,
            "candidatos": 4,
            "resumen_mesa": 1,
            "resultados_partido": 2,
            "resultados_candidato": 4,
            "carga_log": 2,
        }
        for table, expected in expected_counts.items():
            with self.subTest(table=table):
                count = self.connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                self.assertEqual(count, expected)
        statuses = [row[0] for row in self.connection.execute("SELECT estado FROM carga_log")]
        self.assertEqual(statuses, ["COMPLETADA", "COMPLETADA"])
        assert_integrity(self.connection)

    def test_camera_and_senate_coexist_for_same_table(self) -> None:
        self._load(fixture("act_ca_mesa_min.json"), "CA")
        senate_municipality = resolve_municipality(self.nomenclator, "TUNJA", "SE")
        load_act_payload(
            self.connection,
            fixture("act_se_mesa_min.json"),
            self.nomenclator,
            senate_municipality,
            senate_municipality.positions[0],
            "SE",
            expected_scope_code=fixture("act_se_mesa_min.json")["amb"],
            source_url="fixture://SE",
        )
        self.assertEqual(
            self.connection.execute("SELECT COUNT(*) FROM resumen_mesa").fetchone()[0], 2
        )
        self.assertEqual(
            self.connection.execute("SELECT COUNT(*) FROM partidos").fetchone()[0], 4
        )
        assert_integrity(self.connection)

    def test_changed_result_fails_and_is_audited(self) -> None:
        payload = fixture("act_ca_mesa_min.json")
        self._load(payload, "CA")
        changed = copy.deepcopy(payload)
        changed["camaras"][0]["totales"]["act"].update(
            {"votant": "81", "votval": "76", "votcan": "71"}
        )
        party = changed["camaras"][0]["partotabla"][0]["act"]
        party["vot"] = "41"
        party["cantotabla"][0]["vot"] = "11"

        with self.assertRaisesRegex(EtlError, "resultado cambió"):
            self._load(changed, "CA")
        log = self.connection.execute(
            "SELECT estado, error FROM carga_log ORDER BY id DESC LIMIT 1"
        ).fetchone()
        self.assertEqual(log["estado"], "FALLIDA")
        self.assertIn("resultado cambió", log["error"])
        self.assertEqual(
            self.connection.execute("SELECT votos FROM resultados_partido WHERE id = 1").fetchone()[0],
            40,
        )
        assert_integrity(self.connection)
