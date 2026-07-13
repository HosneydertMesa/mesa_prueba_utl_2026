from __future__ import annotations

import io
import json
import tempfile
import unittest
from pathlib import Path

from db.database import initialize_database
from scraper.http_client import FetchResult
from scraper.act_parser import ActParseError
from scraper.nomenclator import load_nomenclator
from scraper.scraper import run_pipeline

FIXTURES = Path(__file__).parents[1] / "fixtures"


class FixtureFetcher:
    def __init__(self) -> None:
        self.camera = json.loads((FIXTURES / "act_ca_mesa_min.json").read_text(encoding="utf-8"))
        self.senate = json.loads((FIXTURES / "act_se_mesa_min.json").read_text(encoding="utf-8"))
        self.calls: list[str] = []

    def get_json(self, url: str, *, use_cache: bool = True) -> FetchResult:
        self.calls.append(url)
        payload = self.camera if "/CA/" in url else self.senate
        return FetchResult(url=url, payload=payload, status=200, from_cache=False, etag='"test"')


class ScraperPipelineIntegrationTests(unittest.TestCase):
    def test_one_table_smoke_and_second_execution(self) -> None:
        nomenclator = load_nomenclator(FIXTURES / "nomenclator_boyaca_min.json")
        fetcher = FixtureFetcher()
        output = io.StringIO()
        with tempfile.TemporaryDirectory() as directory:
            connection = initialize_database(Path(directory) / "pipeline.db")
            try:
                first = run_pipeline(
                    nomenclator,
                    ("TUNJA",),
                    fetcher,
                    connection,
                    table_limit=1,
                    output=output,
                )
                second = run_pipeline(
                    nomenclator,
                    ("TUNJA",),
                    fetcher,
                    connection,
                    table_limit=1,
                    output=output,
                )
            finally:
                connection.close()

        self.assertEqual((first.tables_processed, first.loads), (1, 2))
        self.assertEqual((first.rows_read, first.rows_inserted, first.rows_skipped), (12, 12, 0))
        self.assertEqual((second.rows_read, second.rows_inserted, second.rows_skipped), (12, 0, 12))
        self.assertEqual(len(fetcher.calls), 4)
        self.assertIn("SCRAPER mesas=1 cargas=2", output.getvalue())

    def test_rejects_payload_from_a_different_table(self) -> None:
        nomenclator = load_nomenclator(FIXTURES / "nomenclator_boyaca_min.json")
        fetcher = FixtureFetcher()
        fetcher.camera["amb"] = "0700001010001000002"
        with tempfile.TemporaryDirectory() as directory:
            connection = initialize_database(Path(directory) / "wrong-scope.db")
            try:
                with self.assertRaisesRegex(ActParseError, "ámbito inesperado"):
                    run_pipeline(
                        nomenclator,
                        ("TUNJA",),
                        fetcher,
                        connection,
                        table_limit=1,
                        output=io.StringIO(),
                    )
            finally:
                connection.close()
