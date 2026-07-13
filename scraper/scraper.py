"""CLI reproducible del pipeline electoral UTL 2026."""

from __future__ import annotations

import argparse
import json
import logging
import sqlite3
import sys
from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol, TextIO

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from db.database import assert_integrity, initialize_database  # noqa: E402
from db.etl import EtlError, LoadStats, load_act_payload  # noqa: E402
from scraper.http_client import FetchResult, HttpClientError, JsonHttpClient  # noqa: E402
from scraper.nomenclator import (  # noqa: E402
    DEFAULT_BASE_URL,
    MunicipalityScope,
    NomenclatorError,
    PositionScope,
    build_act_url,
    iter_table_scope_codes,
    normalize_name,
    resolve_municipality,
)

REQUIRED_MUNICIPALITIES = ("TUNJA", "PAIPA", "SOGAMOSO", "DUITAMA")
BONUS_MUNICIPALITIES = ("CHIQUINQUIRA", "PUERTO BOYACA", "MONIQUIRA")
DEFAULT_MUNICIPALITIES = REQUIRED_MUNICIPALITIES
NOMENCLATOR_PATH = "/json/nomenclator.json"


class JsonFetcher(Protocol):
    def get_json(self, url: str, *, use_cache: bool = True) -> FetchResult: ...


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


@dataclass(frozen=True)
class TableJob:
    municipality_name: str
    camera_scope: MunicipalityScope
    senate_scope: MunicipalityScope
    camera_position: PositionScope
    senate_position: PositionScope
    table_scope_code: str
    table_number: int


@dataclass(frozen=True)
class PipelineSummary:
    tables_processed: int
    loads: int
    rows_read: int
    rows_inserted: int
    rows_skipped: int


def parse_municipalities(values: Sequence[str]) -> tuple[str, ...]:
    normalized: list[str] = []
    for value in values:
        name = normalize_name(value)
        if not name:
            continue
        if name not in normalized:
            normalized.append(name)
    if not normalized:
        raise ValueError("debe indicar al menos un municipio")
    return tuple(normalized)


def select_municipalities(
    values: Sequence[str], *, include_bonus: bool = False
) -> tuple[str, ...]:
    selected = [*values, *(BONUS_MUNICIPALITIES if include_bonus else ())]
    return parse_municipalities(selected)


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


def iter_table_jobs(
    nomenclator: Mapping[str, Any],
    municipalities: Sequence[str],
    *,
    table_limit: int | None = None,
) -> Iterator[TableJob]:
    emitted = 0
    for name in municipalities:
        camera = resolve_municipality(nomenclator, name, "CA")
        senate = resolve_municipality(nomenclator, name, "SE")
        senate_positions = {position.code: position for position in senate.positions}
        if {position.code for position in camera.positions} != set(senate_positions):
            raise NomenclatorError(f"puestos CA/SE inconsistentes para {name}")
        for camera_position in camera.positions:
            senate_position = senate_positions[camera_position.code]
            if camera_position.table_count != senate_position.table_count:
                raise NomenclatorError(
                    f"mesas CA/SE inconsistentes en puesto {camera_position.code}"
                )
            for table_number, scope_code in enumerate(
                iter_table_scope_codes(camera_position), start=1
            ):
                if table_limit is not None and emitted >= table_limit:
                    return
                yield TableJob(
                    municipality_name=name,
                    camera_scope=camera,
                    senate_scope=senate,
                    camera_position=camera_position,
                    senate_position=senate_position,
                    table_scope_code=scope_code,
                    table_number=table_number,
                )
                emitted += 1


def run_pipeline(
    nomenclator: Mapping[str, Any],
    municipalities: Sequence[str],
    fetcher: JsonFetcher,
    connection: sqlite3.Connection,
    *,
    base_url: str = DEFAULT_BASE_URL,
    table_limit: int | None = None,
    output: TextIO = sys.stdout,
) -> PipelineSummary:
    rows_read = rows_inserted = rows_skipped = loads = tables_processed = 0
    for job in iter_table_jobs(nomenclator, municipalities, table_limit=table_limit):
        per_corporation: list[tuple[str, LoadStats]] = []
        for corporation, scope, position in (
            ("CA", job.camera_scope, job.camera_position),
            ("SE", job.senate_scope, job.senate_position),
        ):
            url = build_act_url(corporation, job.table_scope_code, base_url)
            fetched = fetcher.get_json(url)
            stats = load_act_payload(
                connection,
                fetched.payload,
                nomenclator,
                scope,
                position,
                corporation,
                expected_scope_code=job.table_scope_code,
                source_url=url,
                source_etag=fetched.etag,
            )
            loads += 1
            rows_read += stats.rows_read
            rows_inserted += stats.rows_inserted
            rows_skipped += stats.rows_skipped
            per_corporation.append((corporation, stats))
        tables_processed += 1
        result_text = " ".join(
            f"{corporation}(ins={stats.rows_inserted},omit={stats.rows_skipped})"
            for corporation, stats in per_corporation
        )
        print(
            f"[OK] municipio={job.municipality_name} puesto={job.camera_position.code} "
            f"mesa={job.table_number}/{job.camera_position.table_count} {result_text}",
            file=output,
        )
    assert_integrity(connection)
    summary = PipelineSummary(
        tables_processed=tables_processed,
        loads=loads,
        rows_read=rows_read,
        rows_inserted=rows_inserted,
        rows_skipped=rows_skipped,
    )
    print(
        f"SCRAPER mesas={summary.tables_processed} cargas={summary.loads} "
        f"leidas={summary.rows_read} insertadas={summary.rows_inserted} "
        f"omitidas={summary.rows_skipped}",
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
        help="muestra cobertura sin descargar resultados ni escribir BD",
    )
    parser.add_argument(
        "--incluir-bonus",
        action="store_true",
        help=(
            "añade Chiquinquirá, Puerto Boyacá y Moniquirá al alcance solicitado"
        ),
    )
    parser.add_argument(
        "--nomenclator",
        type=Path,
        help="archivo local alternativo para desarrollo offline",
    )
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--cache-dir", type=Path, default=Path(".cache/http"))
    parser.add_argument("--db", type=Path, default=Path("db/puestos_2026.db"))
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--max-attempts", type=int, default=4)
    parser.add_argument(
        "--limit-mesas",
        type=int,
        help="limita mesas totales para smoke tests; omitir en la ejecución final",
    )
    return parser


def _load_nomenclator(
    args: argparse.Namespace, client: JsonHttpClient
) -> tuple[Mapping[str, Any], str]:
    if args.nomenclator:
        with args.nomenclator.open(encoding="utf-8") as source:
            return json.load(source), str(args.nomenclator)
    url = f"{args.base_url.rstrip('/')}{NOMENCLATOR_PATH}"
    fetched = client.get_json(url)
    return fetched.payload, f"{url} cache={fetched.from_cache} etag={fetched.etag or '-'}"


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    connection: sqlite3.Connection | None = None
    try:
        municipalities = select_municipalities(
            args.municipios, include_bonus=args.incluir_bonus
        )
        if args.limit_mesas is not None and args.limit_mesas < 1:
            raise ValueError("--limit-mesas debe ser mayor que cero")
        client = JsonHttpClient(
            cache_dir=args.cache_dir,
            timeout=args.timeout,
            max_attempts=args.max_attempts,
        )
        nomenclator, source_label = _load_nomenclator(args, client)
        logging.info("nomenclator=%s", source_label)
        if args.preflight:
            run_preflight(nomenclator, municipalities)
            return 0
        args.db.parent.mkdir(parents=True, exist_ok=True)
        connection = initialize_database(args.db)
        summary = run_pipeline(
            nomenclator,
            municipalities,
            client,
            connection,
            base_url=args.base_url,
            table_limit=args.limit_mesas,
        )
        logging.info("base=%s cargas=%s", args.db, summary.loads)
        return 0
    except (
        OSError,
        ValueError,
        HttpClientError,
        NomenclatorError,
        EtlError,
        sqlite3.Error,
    ) as error:
        logging.error("scraper falló: %s", error)
        return 1
    finally:
        if connection is not None:
            connection.close()


if __name__ == "__main__":
    raise SystemExit(main())
