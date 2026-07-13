"""Exporta un contrato JSON determinista para el dashboard estático."""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from db.database import connect_database  # noqa: E402

REQUIRED_MUNICIPALITIES = ("TUNJA", "PAIPA", "SOGAMOSO", "DUITAMA")
PARTY_COLORS = {
    5: "#007C34",
    57: "#007C34",
    87: "#7B2D8B",
    92: "#7B2D8B",
    10: "#1E477D",
    2: "#E07B00",
}
DEFAULT_PARTY_COLOR = "#64748B"
SQL_3_1_PATH = Path(__file__).resolve().parents[1] / "sql" / "tarea_3_1.sql"


class DashboardExportError(RuntimeError):
    """La base no satisface el contrato mínimo del dashboard."""


def party_color(codpar: int) -> str:
    return PARTY_COLORS.get(codpar, DEFAULT_PARTY_COLOR)


def _municipality_catalog(connection: sqlite3.Connection) -> dict[str, sqlite3.Row]:
    rows = connection.execute(
        "SELECT mu.id, mu.codigo, mu.nombre, "
        "COUNT(DISTINCT pu.id) AS puestos, COUNT(DISTINCT me.id) AS mesas "
        "FROM municipios mu "
        "JOIN puestos pu ON pu.municipio_id = mu.id "
        "JOIN mesas me ON me.puesto_id = pu.id "
        "GROUP BY mu.id, mu.codigo, mu.nombre"
    ).fetchall()
    return {str(row["nombre"]): row for row in rows}


def _party_votes_total(
    connection: sqlite3.Connection,
    municipality_id: int,
    corporation: str,
) -> int:
    return int(
        connection.execute(
            "SELECT COALESCE(SUM(rp.votos), 0) "
            "FROM resultados_partido rp "
            "JOIN partidos pa ON pa.id = rp.partido_id "
            "JOIN mesas me ON me.id = rp.mesa_id "
            "JOIN puestos pu ON pu.id = me.puesto_id "
            "WHERE pu.municipio_id = ? AND pa.corporacion = ?",
            (municipality_id, corporation),
        ).fetchone()[0]
    )


def _top_camera_candidates(
    connection: sqlite3.Connection,
    municipality_id: int,
    camera_total: int,
) -> list[dict[str, Any]]:
    rows = connection.execute(
        "SELECT pa.codpar, pa.nombre AS partido, ca.codcan, "
        "ca.nombre_fuente AS candidato, SUM(rc.votos) AS votos "
        "FROM resultados_candidato rc "
        "JOIN candidatos ca ON ca.id = rc.candidato_id "
        "JOIN partidos pa ON pa.id = ca.partido_id "
        "JOIN mesas me ON me.id = rc.mesa_id "
        "JOIN puestos pu ON pu.id = me.puesto_id "
        "WHERE pu.municipio_id = ? AND pa.corporacion = 'CA' "
        "AND ca.es_lista = 0 "
        "GROUP BY ca.id, pa.codpar, pa.nombre, ca.codcan, ca.nombre_fuente "
        "ORDER BY votos DESC, pa.codpar, ca.codcan LIMIT 10",
        (municipality_id,),
    ).fetchall()
    return [
        {
            "posicion": position,
            "codpar": int(row["codpar"]),
            "codcan": str(row["codcan"]),
            "candidato": str(row["candidato"]),
            "partido": str(row["partido"]),
            "votos": int(row["votos"]),
            "porcentaje_ca_municipal": round(
                int(row["votos"]) * 100.0 / camera_total, 4
            )
            if camera_total
            else None,
            "color": party_color(int(row["codpar"])),
        }
        for position, row in enumerate(rows, start=1)
    ]


def _senate_leader(
    connection: sqlite3.Connection,
    municipality_id: int,
    senate_total: int,
) -> dict[str, Any] | None:
    row = connection.execute(
        "SELECT pa.codpar, pa.nombre AS partido, SUM(rp.votos) AS votos "
        "FROM resultados_partido rp "
        "JOIN partidos pa ON pa.id = rp.partido_id "
        "JOIN mesas me ON me.id = rp.mesa_id "
        "JOIN puestos pu ON pu.id = me.puesto_id "
        "WHERE pu.municipio_id = ? AND pa.corporacion = 'SE' "
        "GROUP BY pa.id, pa.codpar, pa.nombre "
        "ORDER BY votos DESC, pa.codpar LIMIT 1",
        (municipality_id,),
    ).fetchone()
    if row is None:
        return None
    codpar = int(row["codpar"])
    votes = int(row["votos"])
    return {
        "codpar": codpar,
        "partido": str(row["partido"]),
        "votos": votes,
        "porcentaje_se_municipal": round(votes * 100.0 / senate_total, 4)
        if senate_total
        else None,
        "color": party_color(codpar),
    }


def _green_drag_by_municipality(
    connection: sqlite3.Connection,
) -> dict[str, list[dict[str, Any]]]:
    rows = connection.execute(SQL_3_1_PATH.read_text(encoding="utf-8")).fetchall()
    result: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        result.setdefault(str(row["municipio"]), []).append(
            {
                "puesto_codigo": str(row["puesto_codigo"]),
                "puesto": str(row["puesto"]),
                "votos_ca_verde": int(row["votos_ca_verde"]),
                "votos_se_verde": int(row["votos_se_verde"]),
                "ratio_arrastre": (
                    float(row["ratio_arrastre"])
                    if row["ratio_arrastre"] is not None
                    else None
                ),
            }
        )
    return result


def build_dashboard_data(
    connection: sqlite3.Connection,
    *,
    municipality_order: Sequence[str] = REQUIRED_MUNICIPALITIES,
) -> dict[str, Any]:
    catalog = _municipality_catalog(connection)
    missing = [name for name in municipality_order if name not in catalog]
    if missing:
        raise DashboardExportError(
            "faltan municipios requeridos en la base: " + ", ".join(missing)
        )
    drag = _green_drag_by_municipality(connection)
    municipalities: list[dict[str, Any]] = []
    comparison: list[dict[str, Any]] = []
    for name in municipality_order:
        scope = catalog[name]
        municipality_id = int(scope["id"])
        camera_total = _party_votes_total(connection, municipality_id, "CA")
        senate_total = _party_votes_total(connection, municipality_id, "SE")
        leader = _senate_leader(connection, municipality_id, senate_total)
        if leader is None:
            raise DashboardExportError(f"{name} no tiene líder SE")
        item = {
            "codigo": str(scope["codigo"]),
            "nombre": name,
            "puestos": int(scope["puestos"]),
            "mesas": int(scope["mesas"]),
            "votos_ca_total": camera_total,
            "votos_se_total": senate_total,
            "top_candidatos_ca": _top_camera_candidates(
                connection, municipality_id, camera_total
            ),
            "lider_se": leader,
            "arrastre_verde": drag.get(name, []),
        }
        municipalities.append(item)
        comparison.append({"municipio": name, "votos_ca_total": camera_total})

    return {
        "meta": {
            "schema_version": 1,
            "dataset": "Congreso 2026 - Cámara y Senado - Boyacá",
            "corporaciones": ["CA", "SE"],
            "municipios": len(municipalities),
            "puestos": sum(item["puestos"] for item in municipalities),
            "mesas": sum(item["mesas"] for item in municipalities),
            "referencia_arrastre": 1.0,
        },
        "colores_partido": {str(code): color for code, color in PARTY_COLORS.items()},
        "comparativo_ca": comparison,
        "municipios": municipalities,
    }


def validate_dashboard_contract(
    data: Mapping[str, Any],
    *,
    require_top_ten: bool = True,
) -> None:
    municipalities = list(data["municipios"])
    meta = data["meta"]
    if int(meta["municipios"]) != len(municipalities):
        raise DashboardExportError("meta.municipios no coincide con el detalle")
    if int(meta["puestos"]) != sum(int(item["puestos"]) for item in municipalities):
        raise DashboardExportError("meta.puestos no coincide con el detalle")
    if int(meta["mesas"]) != sum(int(item["mesas"]) for item in municipalities):
        raise DashboardExportError("meta.mesas no coincide con el detalle")
    names = [str(item["nombre"]) for item in municipalities]
    comparison_names = [str(item["municipio"]) for item in data["comparativo_ca"]]
    if names != comparison_names or len(names) != len(set(names)):
        raise DashboardExportError("orden o unicidad municipal inconsistente")
    expected_colors = {str(code): color for code, color in PARTY_COLORS.items()}
    if data["colores_partido"] != expected_colors:
        raise DashboardExportError("colores obligatorios incompletos o alterados")
    for item in municipalities:
        if len(item["arrastre_verde"]) != int(item["puestos"]):
            raise DashboardExportError(
                f"{item['nombre']} no tiene un resultado de arrastre por puesto"
            )
        if require_top_ten and len(item["top_candidatos_ca"]) != 10:
            raise DashboardExportError(f"{item['nombre']} no tiene top 10 CA")
        if item["lider_se"] is None:
            raise DashboardExportError(f"{item['nombre']} no tiene líder SE")


def write_dashboard_data(data: Mapping[str, Any], output_path: str | Path) -> int:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(
        data,
        ensure_ascii=False,
        indent=2,
        sort_keys=False,
    ) + "\n"
    encoded = serialized.encode("utf-8")
    temporary = path.with_suffix(".tmp")
    temporary.write_bytes(encoded)
    temporary.replace(path)
    return len(encoded)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=Path("db/puestos_2026.db"))
    parser.add_argument("--output", type=Path, default=Path("dashboard/data.json"))
    args = parser.parse_args(argv)
    connection = connect_database(args.db)
    try:
        data = build_dashboard_data(connection)
        validate_dashboard_contract(data)
    finally:
        connection.close()
    size = write_dashboard_data(data, args.output)
    print(
        f"DASHBOARD_EXPORT municipios={data['meta']['municipios']} "
        f"puestos={data['meta']['puestos']} mesas={data['meta']['mesas']} bytes={size}"
    )
    print(f"INFO salida={args.output} schema_version={data['meta']['schema_version']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
