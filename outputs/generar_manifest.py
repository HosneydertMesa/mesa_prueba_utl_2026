"""Genera el manifest contractual de evaluación descrito por el PDF de la prueba.

La UTL no suministró un generador junto al documento recibido. Esta implementación
del candidato valida los puntos observables indicados en las páginas 2, 4, 5 y 6:
cobertura 4/4, integridad/conteos, líderes SE, SQL 3.1-3.3, artefactos y scatter.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from db.database import connect_database  # noqa: E402
from scripts.audit_database import (  # noqa: E402
    DEFAULT_EXPECTED_TABLES,
    audit_database,
)
from viz.scatter import (  # noqa: E402
    fit_regression,
    format_statistics,
    load_scatter_data,
)

# Sección META solicitada literalmente por el checklist del PDF.
META = {
    "nombre": "Hosneydert Mesa",
    "email": "hosneydert92@gmail.com",
    "repositorio": "https://github.com/HosneydertMesa/mesa_prueba_utl_2026",
}

MANIFEST_SCHEMA_VERSION = 1
GENERATOR_PROVENANCE = "candidate_implemented_from_pdf_contract"
REQUIRED_ARTIFACTS = {
    "dashboard": ("dashboard/index.html", 1),
    "heatmap": ("viz/heatmap_municipios.png", 10_001),
    "scatter": ("viz/scatter_ca_se.png", 10_001),
}
SAMPLE_PROVENANCE = "sample_data/candidate_captured/provenance.json"


class ManifestError(RuntimeError):
    """La entrega no satisface el contrato mínimo del manifest."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _artifact(root: Path, relative_path: str, minimum_bytes: int) -> dict[str, Any]:
    path = root / relative_path
    exists = path.is_file()
    size = path.stat().st_size if exists else 0
    ok = exists and size >= minimum_bytes
    return {
        "status": "OK" if ok else "ERROR",
        "path": relative_path,
        "exists": exists,
        "bytes": size,
        "minimum_bytes": minimum_bytes,
        "sha256": _sha256(path) if exists else None,
    }


def _leaders_se_by_municipality(database_path: Path) -> dict[str, Any]:
    connection = connect_database(database_path)
    try:
        rows = connection.execute(
            "WITH totals AS ("
            " SELECT mu.nombre AS municipio, pa.codpar, pa.nombre AS partido,"
            " SUM(rp.votos) AS votos,"
            " ROW_NUMBER() OVER (PARTITION BY mu.id"
            " ORDER BY SUM(rp.votos) DESC, pa.codpar) AS orden"
            " FROM resultados_partido rp"
            " JOIN partidos pa ON pa.id = rp.partido_id AND pa.corporacion = 'SE'"
            " JOIN mesas me ON me.id = rp.mesa_id"
            " JOIN puestos pu ON pu.id = me.puesto_id"
            " JOIN municipios mu ON mu.id = pu.municipio_id"
            " GROUP BY mu.id, mu.nombre, pa.id, pa.codpar, pa.nombre"
            ") SELECT municipio, codpar, partido, votos"
            " FROM totals WHERE orden = 1 ORDER BY municipio"
        ).fetchall()
        return {
            str(row["municipio"]): {
                "codpar": int(row["codpar"]),
                "partido": str(row["partido"]),
                "votos": int(row["votos"]),
            }
            for row in rows
        }
    finally:
        connection.close()


def _source_updated_at(database_path: Path) -> str | None:
    connection = connect_database(database_path)
    try:
        row = connection.execute(
            "SELECT MAX(finalizado_en) FROM carga_log WHERE estado = 'COMPLETADA'"
        ).fetchone()
        return str(row[0]) if row and row[0] is not None else None
    finally:
        connection.close()


def _sample_data_evidence(root: Path) -> dict[str, Any]:
    provenance_path = root / SAMPLE_PROVENANCE
    if not provenance_path.is_file():
        return {
            "status": "ERROR",
            "path": SAMPLE_PROVENANCE,
            "error": "provenance.json ausente",
        }
    try:
        provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        return {
            "status": "ERROR",
            "path": SAMPLE_PROVENANCE,
            "error": f"JSON inválido: {error}",
        }
    file_results: dict[str, Any] = {}
    for name, expected in provenance.get("files", {}).items():
        path = provenance_path.parent / name
        exists = path.is_file()
        digest = _sha256(path) if exists else None
        size = path.stat().st_size if exists else 0
        ok = (
            exists
            and digest == expected.get("sha256")
            and size == expected.get("bytes")
        )
        file_results[name] = {
            "status": "OK" if ok else "ERROR",
            "bytes": size,
            "sha256": digest,
            "source_url": expected.get("url"),
        }
    ok = (
        provenance.get("provenance") == "candidate_captured_from_public_api_cache"
        and provenance.get("official_utl_sample") is False
        and len(file_results) >= 3
        and all(item["status"] == "OK" for item in file_results.values())
    )
    return {
        "status": "OK" if ok else "ERROR",
        "path": SAMPLE_PROVENANCE,
        "provenance": provenance.get("provenance"),
        "official_utl_sample": provenance.get("official_utl_sample"),
        "files": file_results,
    }


def _scatter_evidence(
    database_path: Path, municipality_order: tuple[str, ...]
) -> dict[str, Any]:
    connection = connect_database(database_path)
    try:
        data = load_scatter_data(connection, municipality_order=municipality_order)
    finally:
        connection.close()
    statistics = fit_regression(data)
    return {
        "status": "OK",
        "pearson_r": round(statistics.pearson_r, 12),
        "slope": round(statistics.slope, 12),
        "intercept": round(statistics.intercept, 12),
        "n_mesas": statistics.table_count,
        "stdout": format_statistics(statistics),
    }


def _sql_evidence(audit: Mapping[str, Any]) -> dict[str, Any]:
    return {
        task: {
            "status": "OK" if result["ok"] else "ERROR",
            "row_count": result["row_count"],
            "columns": result["columns"],
            "sample": result["sample"],
            **({"error": result["error"]} if "error" in result else {}),
        }
        for task, result in audit["sql_tasks"].items()
    }


def build_manifest(
    database_path: str | Path,
    *,
    root: str | Path = ROOT,
    expected_tables: Mapping[str, int] = DEFAULT_EXPECTED_TABLES,
) -> dict[str, Any]:
    root_path = Path(root).resolve()
    db_path = Path(database_path)
    if not db_path.is_absolute():
        db_path = root_path / db_path
    if not db_path.is_file():
        raise ManifestError(f"base SQLite ausente: {db_path}")

    audit = audit_database(db_path, expected_tables=expected_tables)
    municipality_order = tuple(expected_tables)
    loaded = sum(
        name in audit["coverage"]
        and audit["coverage"][name]["mesas_cargadas"] == expected
        for name, expected in expected_tables.items()
    )
    sql = _sql_evidence(audit)
    artifacts = {
        name: _artifact(root_path, path, minimum)
        for name, (path, minimum) in REQUIRED_ARTIFACTS.items()
    }
    samples = _sample_data_evidence(root_path)
    scatter = _scatter_evidence(db_path, municipality_order)
    leaders = _leaders_se_by_municipality(db_path)
    overall_ok = (
        audit["ok"]
        and loaded == len(expected_tables)
        and set(leaders) == set(expected_tables)
        and all(item["status"] == "OK" for item in sql.values())
        and all(item["status"] == "OK" for item in artifacts.values())
        and samples["status"] == "OK"
        and scatter["n_mesas"] == sum(expected_tables.values())
    )
    try:
        database_relative = db_path.relative_to(root_path).as_posix()
    except ValueError:
        database_relative = str(db_path)
    return {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "generator_provenance": GENERATOR_PROVENANCE,
        "overall_status": "OK" if overall_ok else "ERROR",
        "meta": dict(META),
        "source_data_updated_at": _source_updated_at(db_path),
        "scope": {
            "required_municipalities": list(expected_tables),
            "municipalities_loaded": loaded,
            "municipalities_expected": len(expected_tables),
            "tables_expected": sum(expected_tables.values()),
            "corporations": ["CA", "SE"],
        },
        "database": {
            "path": database_relative,
            "bytes": db_path.stat().st_size,
            "sha256": _sha256(db_path),
            "status": "OK" if audit["ok"] else "ERROR",
            "blocking_checks": audit["blocking_checks"],
            "coverage": audit["coverage"],
            "totals": audit["totals"],
            "load_status": audit["load_status"],
            "quality": audit["quality"],
            "leaders_SE_by_municipality": leaders,
        },
        "sql_tasks": sql,
        "artifacts": artifacts,
        "scatter_statistics": scatter,
        "sample_data": samples,
    }


def write_manifest(manifest: Mapping[str, Any], output_path: str | Path) -> None:
    path = Path(output_path)
    if not path.is_absolute():
        path = ROOT / path
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    temporary.replace(path)


def build_example_manifest() -> dict[str, Any]:
    """Devuelve un ejemplo compacto del mismo contrato emitido por el generador."""

    sql_example = {
        task: {
            "status": "OK|ERROR",
            "row_count": 0,
            "columns": [],
            "sample": [],
        }
        for task in ("3.1", "3.2", "3.3")
    }
    artifact_example = {
        name: {
            "status": "OK|ERROR",
            "path": path,
            "exists": True,
            "bytes": 0,
            "minimum_bytes": minimum,
            "sha256": "<SHA256>",
        }
        for name, (path, minimum) in REQUIRED_ARTIFACTS.items()
    }
    return {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "generator_provenance": GENERATOR_PROVENANCE,
        "overall_status": "OK|ERROR",
        "meta": {
            "nombre": "<NOMBRE COMPLETO>",
            "email": "<EMAIL>",
            "repositorio": "https://github.com/<USUARIO>/<REPOSITORIO>",
        },
        "source_data_updated_at": "<TIMESTAMP DE LA CARGA>",
        "scope": {
            "required_municipalities": list(DEFAULT_EXPECTED_TABLES),
            "municipalities_loaded": 4,
            "municipalities_expected": 4,
            "tables_expected": sum(DEFAULT_EXPECTED_TABLES.values()),
            "corporations": ["CA", "SE"],
        },
        "database": {
            "path": "db/puestos_2026.db",
            "bytes": 0,
            "sha256": "<SHA256>",
            "status": "OK|ERROR",
            "blocking_checks": {},
            "coverage": {},
            "totals": {},
            "load_status": {},
            "quality": {},
            "leaders_SE_by_municipality": {},
        },
        "sql_tasks": sql_example,
        "artifacts": artifact_example,
        "scatter_statistics": {
            "status": "OK|ERROR",
            "pearson_r": 0.0,
            "slope": 0.0,
            "intercept": 0.0,
            "n_mesas": 0,
            "stdout": "r=X.XXX | pendiente=X.XXX | n_mesas=NNN",
        },
        "sample_data": {
            "status": "OK|ERROR",
            "path": SAMPLE_PROVENANCE,
            "provenance": "candidate_captured_from_public_api_cache",
            "official_utl_sample": False,
            "files": {},
        },
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=Path("db/puestos_2026.db"))
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("outputs/evaluation_manifest.json"),
    )
    parser.add_argument(
        "--example-output",
        type=Path,
        default=Path("outputs/evaluation_manifest.example.json"),
    )
    args = parser.parse_args(argv)
    try:
        manifest = build_manifest(args.db)
        write_manifest(manifest, args.output)
        write_manifest(build_example_manifest(), args.example_output)
    except (OSError, sqlite3.Error, ValueError, RuntimeError) as error:
        print(f"MANIFEST ERROR | {error}")
        return 1

    scope = manifest["scope"]
    print(
        f"{scope['municipalities_loaded']}/{scope['municipalities_expected']} municipios | "
        f"mesas={manifest['database']['totals']['mesas']}"
    )
    for task, result in manifest["sql_tasks"].items():
        print(f"SQL {result['status']} {task} | filas={result['row_count']}")
    print(manifest["scatter_statistics"]["stdout"])
    print(f"MANIFEST {manifest['overall_status']} | salida={args.output}")
    return 0 if manifest["overall_status"] == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
