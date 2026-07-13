from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[2]
HTML_PATH = ROOT / "dashboard" / "index.html"
JSON_PATH = ROOT / "dashboard" / "data.json"
DATA_PATTERN = re.compile(
    r'<script id="dashboard-data" type="application/json">\s*(.*?)\s*</script>',
    re.DOTALL,
)


class DashboardHtmlContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.html = HTML_PATH.read_text(encoding="utf-8")
        match = DATA_PATTERN.search(cls.html)
        if match is None:
            raise AssertionError("Falta el bloque JSON embebido")
        cls.embedded = json.loads(match.group(1).replace("<\\/", "</"))
        cls.exported = json.loads(JSON_PATH.read_text(encoding="utf-8"))

    def test_is_self_contained_and_file_protocol_safe(self) -> None:
        self.assertNotRegex(self.html, r'<script[^>]+src=')
        self.assertNotRegex(self.html, r'<link[^>]+href=["\']https?://')
        self.assertNotIn("fetch(", self.html)
        self.assertNotIn("pendiente de implementación", self.html.lower())

    def test_embedded_data_matches_exported_contract(self) -> None:
        self.assertEqual(self.embedded, self.exported)
        self.assertEqual(self.embedded["meta"]["municipios"], 4)
        self.assertEqual(self.embedded["meta"]["puestos"], 73)
        self.assertEqual(self.embedded["meta"]["mesas"], 1107)
        self.assertEqual(
            [item["nombre"] for item in self.embedded["municipios"]],
            ["TUNJA", "PAIPA", "SOGAMOSO", "DUITAMA"],
        )

    def test_each_municipality_has_required_views(self) -> None:
        for municipality in self.embedded["municipios"]:
            with self.subTest(municipality=municipality["nombre"]):
                self.assertEqual(len(municipality["top_candidatos_ca"]), 10)
                self.assertIsNotNone(municipality["lider_se"])
                self.assertEqual(
                    len(municipality["arrastre_verde"]), municipality["puestos"]
                )

    def test_mandatory_colors_and_reference_are_present(self) -> None:
        for color in ("#007C34", "#7B2D8B", "#1E477D", "#E07B00"):
            self.assertIn(color, self.html)
        self.assertEqual(self.embedded["meta"]["referencia_arrastre"], 1.0)
        self.assertIn("CA 5 → SE 57", self.html)
        self.assertIn("Referencia 1,0", self.html)

    def test_interactive_and_accessible_landmarks_exist(self) -> None:
        self.assertIn('lang="es"', self.html)
        self.assertIn('id="municipality-select"', self.html)
        self.assertIn('for="municipality-select"', self.html)
        self.assertIn('id="comparison-chart"', self.html)
        self.assertIn('id="candidate-chart"', self.html)
        self.assertIn('id="leader-card"', self.html)
        self.assertIn('id="drag-chart"', self.html)
        self.assertGreaterEqual(self.html.count('role="img"'), 3)
        self.assertIn('aria-live="polite"', self.html)
