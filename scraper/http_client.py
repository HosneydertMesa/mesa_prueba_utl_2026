"""Cliente JSON resiliente, cacheable y comprobable sin red."""

from __future__ import annotations

import hashlib
import json
import logging
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

LOGGER = logging.getLogger(__name__)
RETRYABLE_STATUS = {408, 429, 500, 502, 503, 504}


class HttpClientError(RuntimeError):
    """La fuente HTTP no pudo entregar un JSON válido."""


@dataclass(frozen=True)
class HttpResponse:
    status: int
    body: bytes
    headers: Mapping[str, str]


@dataclass(frozen=True)
class FetchResult:
    url: str
    payload: Any
    status: int
    from_cache: bool
    etag: str | None = None


Transport = Callable[[str, Mapping[str, str], float], HttpResponse]
Sleeper = Callable[[float], None]


def urllib_transport(url: str, headers: Mapping[str, str], timeout: float) -> HttpResponse:
    request = Request(url, headers=dict(headers), method="GET")
    try:
        with urlopen(request, timeout=timeout) as response:  # noqa: S310 - URL controlada
            return HttpResponse(
                status=int(response.status),
                body=response.read(),
                headers=dict(response.headers.items()),
            )
    except HTTPError as error:
        return HttpResponse(
            status=int(error.code),
            body=error.read(),
            headers=dict(error.headers.items()) if error.headers else {},
        )


class JsonHttpClient:
    def __init__(
        self,
        *,
        cache_dir: str | Path = ".cache/http",
        timeout: float = 20.0,
        max_attempts: int = 4,
        backoff_initial: float = 0.5,
        backoff_max: float = 8.0,
        user_agent: str = "utl-electoral-pipeline/0.1 (+README)",
        transport: Transport = urllib_transport,
        sleeper: Sleeper = time.sleep,
    ) -> None:
        if timeout <= 0 or max_attempts < 1 or backoff_initial < 0 or backoff_max < 0:
            raise ValueError("configuración HTTP inválida")
        self.cache_dir = Path(cache_dir)
        self.timeout = timeout
        self.max_attempts = max_attempts
        self.backoff_initial = backoff_initial
        self.backoff_max = backoff_max
        self.headers = {"Accept": "application/json", "User-Agent": user_agent}
        self.transport = transport
        self.sleeper = sleeper

    def get_json(self, url: str, *, use_cache: bool = True) -> FetchResult:
        if not url.lower().startswith(("https://", "http://")):
            raise HttpClientError(f"URL no soportada: {url}")
        cache_path = self._cache_path(url)
        if use_cache and cache_path.exists():
            cached = self._read_cache(cache_path, url)
            if cached is not None:
                return cached

        last_error: Exception | None = None
        for attempt in range(1, self.max_attempts + 1):
            try:
                response = self.transport(url, self.headers, self.timeout)
                if response.status == 200:
                    payload = self._decode_json(response.body, url)
                    result = FetchResult(
                        url=url,
                        payload=payload,
                        status=response.status,
                        from_cache=False,
                        etag=self._header(response.headers, "ETag"),
                    )
                    if use_cache:
                        self._write_cache(cache_path, result)
                    return result
                last_error = HttpClientError(f"HTTP {response.status} al consultar {url}")
                if response.status not in RETRYABLE_STATUS:
                    raise last_error
                retry_after = self._retry_after(response.headers)
            except (URLError, TimeoutError, OSError) as error:
                last_error = error
                retry_after = 0.0

            if attempt < self.max_attempts:
                delay = min(self.backoff_initial * (2 ** (attempt - 1)), self.backoff_max)
                delay = min(max(delay, retry_after), self.backoff_max)
                LOGGER.warning(
                    "reintento HTTP intento=%s/%s espera=%.2fs url=%s error=%s",
                    attempt,
                    self.max_attempts,
                    delay,
                    url,
                    last_error,
                )
                self.sleeper(delay)

        raise HttpClientError(
            f"falló la consulta después de {self.max_attempts} intentos: {url}: {last_error}"
        ) from last_error

    def _cache_path(self, url: str) -> Path:
        digest = hashlib.sha256(url.encode("utf-8")).hexdigest()
        return self.cache_dir / f"{digest}.json"

    def _read_cache(self, path: Path, url: str) -> FetchResult | None:
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            LOGGER.warning("caché inválida; se consultará la fuente: %s", path)
            return None
        if record.get("url") != url or "payload" not in record:
            return None
        return FetchResult(
            url=url,
            payload=record["payload"],
            status=200,
            from_cache=True,
            etag=record.get("etag"),
        )

    def _write_cache(self, path: Path, result: FetchResult) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        record = {
            "url": result.url,
            "etag": result.etag,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "payload": result.payload,
        }
        temporary = path.with_suffix(".tmp")
        temporary.write_text(
            json.dumps(record, ensure_ascii=False, separators=(",", ":")),
            encoding="utf-8",
        )
        temporary.replace(path)

    @staticmethod
    def _decode_json(body: bytes, url: str) -> Any:
        try:
            return json.loads(body.decode("utf-8-sig"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise HttpClientError(f"respuesta JSON inválida: {url}") from error

    @staticmethod
    def _header(headers: Mapping[str, str], name: str) -> str | None:
        return next((value for key, value in headers.items() if key.lower() == name.lower()), None)

    @classmethod
    def _retry_after(cls, headers: Mapping[str, str]) -> float:
        raw = cls._header(headers, "Retry-After")
        try:
            return max(0.0, float(raw)) if raw is not None else 0.0
        except ValueError:
            return 0.0

