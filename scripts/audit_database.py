"""Genera una auditoría local reproducible de cobertura e integridad SQLite."""

from __future__ import annotations

import argparse
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from db.database import connect_database, integrity_report  # noqa: E402

DEFAULT_EXPECTED_TABLES = {
    "TUNJA": 424,
    "PAIPA": 95,
    "SOGAMOSO": 301,
    "DUITAMA": 287,
}
FACT_TABLES = (
    "municipios",
    "puestos",
    "mesas",
    "partidos",
    "candidatos",
    "resumen_mesa",
    "resultados_partido",
    "resultados_candidato",
    "carga_log",
)


def _one(connection: Any, sql: str, parameters: Sequence[object] = ()) -> Any:
    return connection.execute(sql, parameters).fetchone()[0]


def audit_database(
    database_path: str | Path,
    *,
    expected_tables: Mapping[str, int] = DEFAULT_EXPECTED_TABLES,
) -> dict[str, Any]:
    connection = connect_database(database_path)
    try:
        integrity = integrity_report(connection)
        coverage_rows = connection.execute(
            "SELECT mu.nombre, "
            "(SELECT COUNT(1) FROM puestos p WHERE p.municipio_id = mu.id), "
            "(SELECT COALESCE(SUM(p.mesas_esperadas), 0) FROM puestos p "
            " WHERE p.municipio_id = mu.id), "
            "(SELECT COUNT(1) FROM mesas me JOIN puestos p ON p.id = me.puesto_id "
            " WHERE p.municipio_id = mu.id), "
            "(SELECT COUNT(1) FROM resumen_mesa rm JOIN mesas me ON me.id = rm.mesa_id "
            " JOIN puestos p ON p.id = me.puesto_id "
            " WHERE p.municipio_id = mu.id AND rm.corporacion = 'CA'), "
            "(SELECT COUNT(1) FROM resumen_mesa rm JOIN mesas me ON me.id = rm.mesa_id "
            " JOIN puestos p ON p.id = me.puesto_id "
            " WHERE p.municipio_id = mu.id AND rm.corporacion = 'SE') "
            "FROM municipios mu ORDER BY mu.nombre"
        ).fetchall()
        coverage = {
            row[0]: {
                "puestos": row[1],
                "mesas_nomenclator": row[2],
                "mesas_cargadas": row[3],
                "resultados_CA": row[4],
                "resultados_SE": row[5],
                "mesas_esperadas": expected_tables.get(row[0]),
            }
            for row in coverage_rows
        }
        status_rows = connection.execute(
            "SELECT estado, COUNT(1) FROM carga_log GROUP BY estado ORDER BY estado"
        ).fetchall()
        load_status = {row[0]: row[1] for row in status_rows}
        table_counts = {
            table: _one(connection, f"SELECT COUNT(1) FROM {table}")
            for table in FACT_TABLES
        }

        missing_corporations = _one(
            connection,
            "SELECT COUNT(1) FROM mesas me WHERE "
            "(SELECT COUNT(1) FROM resumen_mesa rm WHERE rm.mesa_id = me.id) <> 2",
        )
        invalid_vote_balances = _one(
            connection,
            "SELECT COUNT(1) FROM resumen_mesa "
            "WHERE votos_validos + votos_nulos + votos_no_marcados <> votantes",
        )
        invalid_party_balances = _one(
            connection,
            "SELECT COUNT(1) FROM resumen_mesa rm WHERE "
            "COALESCE((SELECT SUM(rp.votos) FROM resultados_partido rp "
            "JOIN partidos pa ON pa.id = rp.partido_id "
            "WHERE rp.mesa_id = rm.mesa_id AND pa.corporacion = rm.corporacion), 0) "
            "+ rm.votos_blancos <> rm.votos_validos",
        )
        invalid_candidate_balances = _one(
            connection,
            "SELECT COUNT(1) FROM resultados_partido rp WHERE "
            "COALESCE((SELECT SUM(rc.votos) FROM candidatos ca "
            "JOIN resultados_candidato rc ON rc.candidato_id = ca.id "
            "WHERE ca.partido_id = rp.partido_id AND rc.mesa_id = rp.mesa_id), 0) "
            "<> rp.votos",
        )
        census_anomaly_rows = connection.execute(
            "SELECT me.codigo, rm.corporacion, rm.censo, rm.votantes "
            "FROM resumen_mesa rm JOIN mesas me ON me.id = rm.mesa_id "
            "WHERE rm.votantes > rm.censo ORDER BY me.codigo, rm.corporacion"
        ).fetchall()
        top_senate_party = connection.execute(
            "SELECT pa.codpar, pa.nombre, SUM(rp.votos) AS total "
            "FROM resultados_partido rp JOIN partidos pa ON pa.id = rp.partido_id "
            "WHERE pa.corporacion = 'SE' GROUP BY pa.id "
            "ORDER BY total DESC, pa.codpar LIMIT 1"
        ).fetchone()
        top_senate_candidate = connection.execute(
            "SELECT pa.codpar, ca.codcan, ca.nombre_fuente, SUM(rc.votos) AS total "
            "FROM resultados_candidato rc JOIN candidatos ca ON ca.id = rc.candidato_id "
            "JOIN partidos pa ON pa.id = ca.partido_id "
            "WHERE pa.corporacion = 'SE' AND ca.es_lista = 0 GROUP BY ca.id "
            "ORDER BY total DESC, pa.codpar, ca.codcan LIMIT 1"
        ).fetchone()

        expected_names = set(expected_tables)
        coverage_ok = set(coverage) == expected_names and all(
            coverage[name]["mesas_cargadas"] == expected
            and coverage[name]["resultados_CA"] == expected
            and coverage[name]["resultados_SE"] == expected
            for name, expected in expected_tables.items()
        )
        blocking_checks = {
            "integrity_check": integrity.integrity_messages == ("ok",),
            "foreign_key_check": not integrity.foreign_key_violations,
            "coverage": coverage_ok,
            "two_corporations_per_table": missing_corporations == 0,
            "vote_balances": invalid_vote_balances == 0,
            "party_balances": invalid_party_balances == 0,
            "candidate_balances": invalid_candidate_balances == 0,
            "no_failed_or_incomplete_loads": set(load_status).issubset({"COMPLETADA"}),
        }
        return {
            "audit_type": "local_non_official",
            "ok": all(blocking_checks.values()),
            "blocking_checks": blocking_checks,
            "coverage": coverage,
            "totals": table_counts,
            "load_status": load_status,
            "quality": {
                "missing_corporations": missing_corporations,
                "invalid_vote_balances": invalid_vote_balances,
                "invalid_party_balances": invalid_party_balances,
                "invalid_candidate_balances": invalid_candidate_balances,
                "voters_over_census_count": len(census_anomaly_rows),
                "voters_over_census_sample": [
                    {
                        "mesa": row[0],
                        "corporacion": row[1],
                        "censo": row[2],
                        "votantes": row[3],
                    }
                    for row in census_anomaly_rows[:10]
                ],
            },
            "leaders_SE": {
                "party": (
                    {
                        "codpar": top_senate_party[0],
                        "nombre": top_senate_party[1],
                        "votos": top_senate_party[2],
                    }
                    if top_senate_party
                    else None
                ),
                "candidate": (
                    {
                        "codpar": top_senate_candidate[0],
                        "codcan": top_senate_candidate[1],
                        "nombre": top_senate_candidate[2],
                        "votos": top_senate_candidate[3],
                    }
                    if top_senate_candidate
                    else None
                ),
            },
        }
    finally:
        connection.close()


def write_audit(report: Mapping[str, Any], output_path: str | Path) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=Path("db/puestos_2026.db"))
    parser.add_argument("--output", type=Path, default=Path("outputs/auditoria_local.json"))
    args = parser.parse_args(argv)
    report = audit_database(args.db)
    write_audit(report, args.output)
    print(
        f"AUDITORIA ok={report['ok']} municipios={len(report['coverage'])}/4 "
        f"mesas={report['totals']['mesas']}/1107 "
        f"resultados={report['totals']['resumen_mesa']}/2214 "
        f"anomalias_censo={report['quality']['voters_over_census_count']}"
    )
    print(f"INFO salida={args.output} tipo={report['audit_type']}")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
