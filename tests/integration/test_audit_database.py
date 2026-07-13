from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from db.database import initialize_database
from db.etl import load_act_payload
from scraper.nomenclator import load_nomenclator, resolve_municipality
from scripts.audit_database import audit_database

FIXTURES = Path(__file__).parents[1] / "fixtures"


class DatabaseAuditIntegrationTests(unittest.TestCase):
    def test_complete_fixture_database_passes_local_audit(self) -> None:
        nomenclator = load_nomenclator(FIXTURES / "nomenclator_boyaca_min.json")
        ca_payload = json.loads(
            (FIXTURES / "act_ca_mesa_min.json").read_text(encoding="utf-8")
        )
        se_payload = json.loads(
            (FIXTURES / "act_se_mesa_min.json").read_text(encoding="utf-8")
        )
        with tempfile.TemporaryDirectory() as directory:
            database_path = Path(directory) / "audit.db"
            connection = initialize_database(database_path)
            try:
                for corporation, payload in (("CA", ca_payload), ("SE", se_payload)):
                    municipality = resolve_municipality(nomenclator, "TUNJA", corporation)
                    load_act_payload(
                        connection,
                        payload,
                        nomenclator,
                        municipality,
                        municipality.positions[0],
                        corporation,
                        expected_scope_code=payload["amb"],
                        source_url=f"fixture://{corporation}",
                    )
            finally:
                connection.close()

            report = audit_database(database_path, expected_tables={"TUNJA": 1})

        self.assertTrue(report["ok"])
        self.assertEqual(report["totals"]["resumen_mesa"], 2)
        self.assertEqual(report["quality"]["missing_corporations"], 0)
        self.assertEqual(report["leaders_SE"]["party"]["codpar"], 57)
        self.assertTrue(all(task["ok"] for task in report["sql_tasks"].values()))
        self.assertEqual(report["sql_tasks"]["3.1"]["row_count"], 1)
        self.assertEqual(report["sql_tasks"]["3.3"]["row_count"], 2)
