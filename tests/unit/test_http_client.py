from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scraper.http_client import HttpClientError, HttpResponse, JsonHttpClient


class SequencedTransport:
    def __init__(self, responses: list[HttpResponse]) -> None:
        self.responses = responses
        self.calls = 0

    def __call__(self, url: str, headers: dict[str, str], timeout: float) -> HttpResponse:
        self.calls += 1
        return self.responses.pop(0)


class JsonHttpClientTests(unittest.TestCase):
    def test_retries_with_backoff_then_caches_success(self) -> None:
        transport = SequencedTransport(
            [
                HttpResponse(503, b"unavailable", {"Retry-After": "0.2"}),
                HttpResponse(500, b"error", {}),
                HttpResponse(200, b'{"ok":true}', {"ETag": '"v1"'}),
            ]
        )
        sleeps: list[float] = []
        with tempfile.TemporaryDirectory() as directory:
            client = JsonHttpClient(
                cache_dir=directory,
                max_attempts=3,
                backoff_initial=0.1,
                backoff_max=1.0,
                transport=transport,
                sleeper=sleeps.append,
            )
            first = client.get_json("https://example.test/data.json")
            second = client.get_json("https://example.test/data.json")

        self.assertEqual(first.payload, {"ok": True})
        self.assertFalse(first.from_cache)
        self.assertTrue(second.from_cache)
        self.assertEqual(transport.calls, 3)
        self.assertEqual(sleeps, [0.2, 0.2])

    def test_does_not_retry_non_retryable_status(self) -> None:
        transport = SequencedTransport([HttpResponse(404, b"missing", {})])
        with tempfile.TemporaryDirectory() as directory:
            client = JsonHttpClient(
                cache_dir=directory,
                transport=transport,
                sleeper=lambda _: None,
            )
            with self.assertRaises(HttpClientError):
                client.get_json("https://example.test/missing.json")
        self.assertEqual(transport.calls, 1)

    def test_rejects_invalid_json(self) -> None:
        transport = SequencedTransport([HttpResponse(200, b"not-json", {})])
        with tempfile.TemporaryDirectory() as directory:
            client = JsonHttpClient(
                cache_dir=Path(directory),
                max_attempts=1,
                transport=transport,
            )
            with self.assertRaises(HttpClientError):
                client.get_json("https://example.test/invalid.json")

    def test_retries_invalid_json_then_caches_success(self) -> None:
        transport = SequencedTransport(
            [
                HttpResponse(200, b"not-json", {}),
                HttpResponse(200, b'{"ok":true}', {"ETag": '"v2"'}),
            ]
        )
        sleeps: list[float] = []
        with tempfile.TemporaryDirectory() as directory:
            client = JsonHttpClient(
                cache_dir=Path(directory),
                max_attempts=2,
                backoff_initial=0.1,
                transport=transport,
                sleeper=sleeps.append,
            )
            first = client.get_json("https://example.test/transient-invalid.json")
            second = client.get_json("https://example.test/transient-invalid.json")

        self.assertEqual(first.payload, {"ok": True})
        self.assertTrue(second.from_cache)
        self.assertEqual(transport.calls, 2)
        self.assertEqual(sleeps, [0.1])

