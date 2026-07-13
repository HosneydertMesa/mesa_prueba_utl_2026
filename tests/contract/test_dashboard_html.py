from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[2]
HTML_PATH = ROOT / "dashboard" / "index.html"
JSON_PATH = ROOT / "dashboard" / "data.json"
PAGES_WORKFLOW_PATH = ROOT / ".github" / "workflows" / "pages.yml"
QUALITY_WORKFLOW_PATH = ROOT / ".github" / "workflows" / "quality.yml"
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
        provenance = self.embedded["meta"]["procedencia"]
        self.assertEqual(provenance["tipo_auditoria"], "local_non_official")
        self.assertEqual(provenance["anomalias_censo_preservadas"], 66)
        self.assertRegex(provenance["huella_contenido_sha256"], r"^[0-9a-f]{64}$")
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

    def test_workspace_navigation_replaces_the_long_landing_flow(self) -> None:
        identifiers = re.findall(r'\bid="([^"]+)"', self.html)
        self.assertEqual(len(identifiers), len(set(identifiers)))
        self.assertIn('class="workspace-shell"', self.html)
        self.assertIn('class="workspace-sidebar"', self.html)
        self.assertIn('role="tablist"', self.html)
        for view in ("overview", "municipality", "analytics", "bonus"):
            self.assertIn(f'data-workspace-target="{view}"', self.html)
            self.assertIn(f'data-workspace-view="{view}"', self.html)
            self.assertIn(f'aria-controls="view-{view}"', self.html)
        self.assertIn("function setWorkspaceView(", self.html)
        self.assertIn("function initializeWorkspaceNavigation()", self.html)
        self.assertIn("window.location.hash.slice(1)", self.html)

    def test_mobile_workspace_constrains_wide_visuals(self) -> None:
        self.assertRegex(
            self.html,
            r"\.workspace-view\s*\{[^}]*min-width:\s*0",
        )
        self.assertRegex(
            self.html,
            r"\.workspace-view \.section\s*\{[^}]*min-width:\s*0",
        )

    def test_presentation_provenance_and_shareable_state_are_available(self) -> None:
        for identifier in (
            "presentation-start",
            "presentation-bar",
            "presentation-previous",
            "presentation-next",
            "presentation-exit",
            "provenance-strip",
            "provenance-source",
            "provenance-anomalies",
        ):
            self.assertIn(f'id="{identifier}"', self.html)
        self.assertIn("huella_contenido_sha256", self.html)
        self.assertIn("function initializePresentation()", self.html)
        self.assertIn("function readDashboardState()", self.html)
        self.assertIn("function syncDashboardHash()", self.html)
        self.assertIn("function applyDashboardState(state)", self.html)
        self.assertIn('params.set("municipio", select.value)', self.html)
        self.assertIn('params.set("scope", analyticsScope)', self.html)
        self.assertIn('params.set("scatter", scatterFilter)', self.html)

    def test_github_pages_workflow_publishes_only_dashboard_artifacts(self) -> None:
        workflow = PAGES_WORKFLOW_PATH.read_text(encoding="utf-8")
        self.assertIn("branches: [main]", workflow)
        self.assertIn("pull_request:", workflow)
        self.assertIn("pages: write", workflow)
        self.assertIn("id-token: write", workflow)
        self.assertIn("actions/checkout@v7", workflow)
        self.assertIn("actions/configure-pages@v6", workflow)
        self.assertIn("actions/upload-pages-artifact@v5", workflow)
        self.assertIn("actions/deploy-pages@v5", workflow)
        self.assertIn("if: github.event_name != 'pull_request'", workflow)
        self.assertIn("cp dashboard/index.html dashboard/data.json _site/", workflow)
        self.assertIn("path: _site", workflow)
        self.assertIn("PAGES_SMOKE_OK", workflow)
        self.assertIn('data["meta"]["mesas"] == 1432', workflow)

        quality_workflow = QUALITY_WORKFLOW_PATH.read_text(encoding="utf-8")
        self.assertIn("actions/checkout@v7", quality_workflow)
        self.assertIn("actions/setup-python@v6", quality_workflow)

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
        self.assertEqual(analytics["alcance_predeterminado"], "ampliado")
        expanded = analytics["ampliada"]
        self.assertEqual(expanded["heatmap"]["municipios"], EXPECTED_MUNICIPALITIES)
        self.assertEqual(len(expanded["heatmap"]["candidatos"]), 8)
        self.assertEqual(len(expanded["scatter"]["puntos"]), 1432)
        expanded_statistics = expanded["scatter"]["estadisticas"]
        self.assertEqual(expanded_statistics["n_mesas"], 1432)
        self.assertAlmostEqual(expanded_statistics["pearson_r"], 0.957, places=3)
        self.assertAlmostEqual(expanded_statistics["pendiente"], 0.939, places=3)
        self.assertIn('id="interactive-heatmap"', self.html)
        self.assertIn('id="scatter-canvas"', self.html)
        self.assertIn('id="scatter-filters"', self.html)
        self.assertIn('id="analytics-scope-toggle"', self.html)
        self.assertIn('data-analytics-scope="obligatorio"', self.html)
        self.assertIn('data-analytics-scope="ampliado"', self.html)
        self.assertIn("function renderAnalyticsScope(", self.html)
