from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from db.database import assert_integrity, initialize_database
from db.etl import load_act_payload
from scraper.nomenclator import load_nomenclator, resolve_municipality

ROOT = Path(__file__).resolve().parents[2]
SAMPLES = ROOT / "sample_data" / "candidate_captured"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


class CandidateSampleDataIntegrationTests(unittest.TestCase):
    def test_real_captured_samples_are_traceable_and_loadable(self) -> None:
        provenance = json.loads(
            (SAMPLES / "provenance.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            provenance["provenance"], "candidate_captured_from_public_api_cache"
        )
        self.assertFalse(provenance["official_utl_sample"])
        for name, expected in provenance["files"].items():
            path = SAMPLES / name
            self.assertTrue(path.is_file())
            self.assertNotIn(b"\r\n", path.read_bytes())
            self.assertEqual(path.stat().st_size, expected["bytes"])
            self.assertEqual(sha256(path), expected["sha256"])

        nomenclator = load_nomenclator(SAMPLES / "nomenclator_boyaca_sample.json")
        payloads = {
            corporation: json.loads(
                (SAMPLES / f"act_{corporation.lower()}_tunja_mesa_001.json").read_text(
                    encoding="utf-8"
                )
            )
            for corporation in ("CA", "SE")
        }
        with tempfile.TemporaryDirectory() as directory:
            connection = initialize_database(Path(directory) / "sample.db")
            try:
                for corporation, payload in payloads.items():
                    municipality = resolve_municipality(
                        nomenclator, "TUNJA", corporation
                    )
                    position = next(
                        item
                        for item in municipality.positions
                        if payload["amb"].startswith(item.code)
                    )
                    stats = load_act_payload(
                        connection,
                        payload,
                        nomenclator,
                        municipality,
                        position,
                        corporation,
                        expected_scope_code=payload["amb"],
                        source_url=provenance["files"][
                            f"act_{corporation.lower()}_tunja_mesa_001.json"
                        ]["url"],
                    )
                    self.assertGreater(stats.rows_read, 0)
                    self.assertGreater(stats.rows_inserted, 0)
                assert_integrity(connection)
                self.assertEqual(
                    connection.execute("SELECT COUNT(*) FROM mesas").fetchone()[0], 1
                )
                self.assertEqual(
                    connection.execute("SELECT COUNT(*) FROM resumen_mesa").fetchone()[0],
                    2,
                )
            finally:
                connection.close()


if __name__ == "__main__":
    unittest.main()
