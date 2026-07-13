"""CLI del pipeline electoral: incremento 1.2a (preflight verificable)."""

from __future__ import annotations

import argparse
import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scraper.http_client import HttpClientError, JsonHttpClient  # noqa: E402
from scraper.nomenclator import (  # noqa: E402
    DEFAULT_BASE_URL,
    NomenclatorError,
    normalize_name,
    resolve_municipality,
)

DEFAULT_MUNICIPALITIES = ("TUNJA", "PAIPA", "SOGAMOSO", "DUITAMA")
NOMENCLATOR_PATH = "/json/nomenclator.json"


@dataclass(frozen=True)
class MunicipalityPreflight:
    name: str
    code: str
    positions: int
    tables: int


@dataclass(frozen=True)
class PreflightSummary:
    municipalities: tuple[MunicipalityPreflight, ...]

    @property
    def position_count(self) -> int:
        return sum(item.positions for item in self.municipalities)

    @property
    def table_count(self) -> int:
        return sum(item.tables for item in self.municipalities)

    @property
    def act_request_count(self) -> int:
        return self.table_count * 2


def parse_municipalities(values: Sequence[str]) -> tuple[str, ...]:
    normalized: list[str] = []
    for value in values:
        name = normalize_name(value)
        if name not in DEFAULT_MUNICIPALITIES:
            allowed = ", ".join(DEFAULT_MUNICIPALITIES)
            raise ValueError(f"municipio no soportado: {value}. Permitidos: {allowed}")
        if name not in normalized:
            normalized.append(name)
    if not normalized:
        raise ValueError("debe indicar al menos un municipio")
    return tuple(normalized)


def run_preflight(
    nomenclator: Mapping[str, Any],
    municipalities: Sequence[str],
    *,
    output: TextIO = sys.stdout,
) -> PreflightSummary:
    results: list[MunicipalityPreflight] = []
    for name in municipalities:
        camera = resolve_municipality(nomenclator, name, "CA")
        senate = resolve_municipality(nomenclator, name, "SE")
        camera_shape = (camera.code, len(camera.positions), camera.table_count)
        senate_shape = (senate.code, len(senate.positions), senate.table_count)
        if camera_shape != senate_shape:
            raise NomenclatorError(
                f"cobertura CA/SE inconsistente para {name}: CA={camera_shape} SE={senate_shape}"
            )
        item = MunicipalityPreflight(
            name=name,
            code=camera.code,
            positions=len(camera.positions),
            tables=camera.table_count,
        )
        results.append(item)
        print(
            f"[OK] municipio={item.name} codigo={item.code} "
            f"puestos={item.positions} mesas={item.tables}",
            file=output,
        )
    summary = PreflightSummary(tuple(results))
    print(
        f"PREFLIGHT {len(results)}/{len(municipalities)} municipios | "
        f"puestos={summary.position_count} | mesas={summary.table_count} | "
        f"solicitudes_ACT={summary.act_request_count}",
        file=output,
    )
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--municipios",
        nargs="+",
        default=list(DEFAULT_MUNICIPALITIES),
        metavar="NOMBRE",
        help="municipios a procesar; por defecto los cuatro obligatorios",
    )
    parser.add_argument(
        "--preflight",
        action="store_true",
        help="muestra cobertura y solicitudes estimadas sin descargar resultados ni escribir BD",
    )
    parser.add_argument(
        "--nomenclator",
        type=Path,
        help="archivo local alternativo; útil para sample_data o pruebas offline",
    )
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--cache-dir", type=Path, default=Path(".cache/http"))
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--max-attempts", type=int, default=4)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    try:
        municipalities = parse_municipalities(args.municipios)
        if not args.preflight:
            parser.error("la descarga/persistencia se habilitará en el incremento 1.2b; use --preflight")
        if args.nomenclator:
            import json

            with args.nomenclator.open(encoding="utf-8") as source:
                nomenclator = json.load(source)
            source_label = str(args.nomenclator)
        else:
            client = JsonHttpClient(
                cache_dir=args.cache_dir,
                timeout=args.timeout,
                max_attempts=args.max_attempts,
            )
            url = f"{args.base_url.rstrip('/')}{NOMENCLATOR_PATH}"
            fetched = client.get_json(url)
            nomenclator = fetched.payload
            source_label = f"{url} cache={fetched.from_cache} etag={fetched.etag or '-'}"
        logging.info("nomenclator=%s", source_label)
        run_preflight(nomenclator, municipalities)
        return 0
    except (OSError, ValueError, HttpClientError, NomenclatorError) as error:
        logging.error("preflight falló: %s", error)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

