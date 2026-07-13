from __future__ import annotations

import unittest

from scripts.quality_gate import REQUIRED_H2, find_secrets, markdown_headings


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


if __name__ == "__main__":
    unittest.main()

