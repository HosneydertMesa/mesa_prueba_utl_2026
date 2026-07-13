from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from dashboard.export_data import (
    DashboardExportError,
    build_dashboard_data,
    validate_dashboard_contract,
    write_dashboard_data,
)
from db.database import initialize_database
from db.etl import load_act_payload
from scraper.nomenclator import load_nomenclator, resolve_municipality

FIXTURES = Path(__file__).parents[1] / "fixtures"


def fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


class DashboardExportIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.connection = initialize_database(Path(self.temporary.name) / "dashboard.db")
        nomenclator = load_nomenclator(FIXTURES / "nomenclator_boyaca_min.json")
        for corporation, payload in (
            ("CA", fixture("act_ca_mesa_min.json")),
            ("SE", fixture("act_se_mesa_min.json")),
        ):
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

    def test_exports_dashboard_contract_from_sqlite(self) -> None:
        data = build_dashboard_data(self.connection, municipality_order=("TUNJA",))
        validate_dashboard_contract(data, require_top_ten=False)
        tunja = data["municipios"][0]

        self.assertEqual(data["meta"]["schema_version"], 1)
        self.assertEqual(data["meta"]["referencia_arrastre"], 1.0)
        self.assertEqual(data["colores_partido"]["5"], "#007C34")
        self.assertEqual(data["colores_partido"]["92"], "#7B2D8B")
        self.assertEqual(data["colores_partido"]["10"], "#1E477D")
        self.assertEqual(data["colores_partido"]["2"], "#E07B00")
        self.assertEqual((tunja["puestos"], tunja["mesas"]), (1, 1))
        self.assertEqual(tunja["votos_ca_total"], 70)
        self.assertEqual(tunja["top_candidatos_ca"][0]["codcan"], "101")
        self.assertEqual(tunja["top_candidatos_ca"][0]["votos"], 20)
        self.assertEqual(tunja["lider_se"]["codpar"], 57)
        self.assertEqual(tunja["lider_se"]["votos"], 45)
        self.assertAlmostEqual(tunja["arrastre_verde"][0]["ratio_arrastre"], 1.125)

    def test_requires_all_requested_municipalities(self) -> None:
        with self.assertRaisesRegex(DashboardExportError, "PAIPA"):
            build_dashboard_data(self.connection)

    def test_serialization_is_byte_deterministic(self) -> None:
        data = build_dashboard_data(self.connection, municipality_order=("TUNJA",))
        first = Path(self.temporary.name) / "first.json"
        second = Path(self.temporary.name) / "second.json"

        write_dashboard_data(data, first)
        write_dashboard_data(data, second)

        self.assertEqual(first.read_bytes(), second.read_bytes())
