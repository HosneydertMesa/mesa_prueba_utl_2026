from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[2]
HTML_PATH = ROOT / "dashboard" / "index.html"
JSON_PATH = ROOT / "dashboard" / "data.json"
REQUIRED_MUNICIPALITIES = ["TUNJA", "PAIPA", "SOGAMOSO", "DUITAMA"]
BONUS_MUNICIPALITIES = ["CHIQUINQUIRA", "PUERTO BOYACA", "MONIQUIRA"]
EXPECTED_MUNICIPALITIES = REQUIRED_MUNICIPALITIES + BONUS_MUNICIPALITIES
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
        self.assertEqual(self.embedded["meta"]["municipios"], 7)
        self.assertEqual(self.embedded["meta"]["municipios_obligatorios"], 4)
        self.assertEqual(self.embedded["meta"]["municipios_bonus"], 3)
        self.assertEqual(self.embedded["meta"]["puestos"], 104)
        self.assertEqual(self.embedded["meta"]["mesas"], 1432)
        self.assertEqual(self.embedded["meta"]["mesas_analiticas"], 1107)
        self.assertEqual(
            [item["nombre"] for item in self.embedded["municipios"]],
            EXPECTED_MUNICIPALITIES,
        )
        self.assertEqual(
            [item["alcance"] for item in self.embedded["municipios"]],
            ["obligatorio"] * 4 + ["bonus"] * 3,
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

    def test_bonus_dark_mode_and_csv_export_are_self_contained(self) -> None:
        self.assertIn('html[data-theme="dark"]', self.html)
        self.assertIn('id="theme-toggle"', self.html)
        self.assertIn('id="theme-label"', self.html)
        self.assertIn('aria-pressed="false"', self.html)
        self.assertIn('localStorage.setItem("utl-dashboard-theme"', self.html)
        self.assertIn('id="csv-export"', self.html)
        self.assertIn('new Blob([content], { type: "text/csv;charset=utf-8" })', self.html)
        self.assertIn('link.download = `dashboard-${slug}.csv`', self.html)
        self.assertIn('"\\uFEFF"', self.html)
        self.assertIn('"ratio_arrastre"', self.html)

    def test_all_six_bonus_are_visible_and_total_fifteen_points(self) -> None:
        bonuses = self.embedded["bonificaciones"]
        self.assertEqual(len(bonuses), 6)
        self.assertEqual(sum(item["puntos"] for item in bonuses), 15)
        self.assertIn('id="bonus-grid"', self.html)
        self.assertIn('id="bonus-total"', self.html)
        self.assertIn("renderBonusEvidence()", self.html)

    def test_analytical_v2_reuses_heatmap_and_scatter_contracts(self) -> None:
        self.assertEqual(self.embedded["meta"]["schema_version"], 2)
        analytics = self.embedded["analitica"]
        self.assertEqual(analytics["heatmap"]["municipios"], REQUIRED_MUNICIPALITIES)
        self.assertEqual(len(analytics["heatmap"]["candidatos"]), 8)
        self.assertEqual(len(analytics["scatter"]["puntos"]), 1107)
        statistics = analytics["scatter"]["estadisticas"]
        self.assertEqual(statistics["n_mesas"], 1107)
        self.assertAlmostEqual(statistics["pearson_r"], 0.964, places=3)
        self.assertAlmostEqual(statistics["pendiente"], 0.933, places=3)
        self.assertIn('id="interactive-heatmap"', self.html)
        self.assertIn('id="scatter-canvas"', self.html)
        self.assertIn('id="scatter-filters"', self.html)
