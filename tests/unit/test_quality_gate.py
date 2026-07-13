from __future__ import annotations

import unittest

from scripts.quality_gate import (
    REQUIRED_H2,
    find_secrets,
    markdown_headings,
    validate_release_manifest,
)


class QualityGateTests(unittest.TestCase):
    def test_secret_detector_flags_token_shape_without_real_secret(self) -> None:
        synthetic = "gh" + "p_" + ("A" * 36)
        self.assertEqual(find_secrets(synthetic), ["GitHub token"])

    def test_markdown_headings_ignore_code_fences(self) -> None:
        content = "# A — Prueba Técnica UTL Senado 2026\n\n```bash\n# comentario\n```\n"
        content += "\n".join(REQUIRED_H2)
        self.assertEqual(
            markdown_headings(content),
            ["# A — Prueba Técnica UTL Senado 2026", *REQUIRED_H2],
        )

    def test_release_manifest_validator_rejects_incomplete_contract(self) -> None:
        failures = validate_release_manifest(
            {
                "overall_status": "ERROR",
                "scope": {"municipalities_loaded": 3, "municipalities_expected": 4},
                "sql_tasks": {},
            }
        )
        self.assertIn("overall_status no es OK", failures)
        self.assertIn("cobertura del manifest distinta de 4/4", failures)
        self.assertIn("tareas SQL incompletas", failures)


if __name__ == "__main__":
    unittest.main()
