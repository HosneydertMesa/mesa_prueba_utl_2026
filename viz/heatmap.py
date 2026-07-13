"""Genera el heatmap 8x4 de candidaturas CA exigido por el Reto 5.1."""

from __future__ import annotations

import argparse
import os
import sqlite3
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Final

os.environ.setdefault(
    "MPLCONFIGDIR", str(Path(__file__).resolve().parents[1] / ".cache" / "matplotlib")
)

import matplotlib
import numpy as np

matplotlib.use("Agg")
from matplotlib import pyplot as plt  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from db.database import connect_database  # noqa: E402

MUNICIPALITIES: Final = ("TUNJA", "PAIPA", "SOGAMOSO", "DUITAMA")
TOP_CANDIDATES: Final = 8
DEFAULT_DATABASE: Final = Path("db/puestos_2026.db")
DEFAULT_OUTPUT: Final = Path("viz/heatmap_municipios.png")


class HeatmapError(RuntimeError):
    """La base no satisface el contrato mínimo del heatmap."""


@dataclass(frozen=True)
class HeatmapData:
    """Matriz y metadatos auditables usados para renderizar el heatmap."""

    municipalities: tuple[str, ...]
    candidate_labels: tuple[str, ...]
    candidate_keys: tuple[tuple[int, str], ...]
    percentages: np.ndarray
    votes: np.ndarray
    municipality_totals: tuple[int, ...]
    consolidated_votes: tuple[int, ...]


def _placeholders(size: int) -> str:
    return ", ".join("?" for _ in range(size))


def load_heatmap_data(
    connection: sqlite3.Connection,
    *,
    municipality_order: tuple[str, ...] = MUNICIPALITIES,
) -> HeatmapData:
    """Selecciona el top 8 consolidado y calcula su peso en cada municipio."""

    if not municipality_order or len(set(municipality_order)) != len(
        municipality_order
    ):
        raise HeatmapError("el heatmap requiere municipios únicos y no vacíos")

    placeholders = _placeholders(len(municipality_order))
    catalog_rows = connection.execute(
        f"SELECT id, nombre FROM municipios WHERE nombre IN ({placeholders})",
        municipality_order,
    ).fetchall()
    municipality_ids = {str(row["nombre"]): int(row["id"]) for row in catalog_rows}
    missing = [name for name in municipality_order if name not in municipality_ids]
    if missing:
        raise HeatmapError("faltan municipios requeridos: " + ", ".join(missing))

    candidate_rows = connection.execute(
        "SELECT ca.id, pa.codpar, ca.codcan, ca.nombre_fuente, "
        "SUM(rc.votos) AS votos_consolidados "
        "FROM resultados_candidato rc "
        "JOIN candidatos ca ON ca.id = rc.candidato_id "
        "JOIN partidos pa ON pa.id = ca.partido_id "
        "JOIN mesas me ON me.id = rc.mesa_id "
        "JOIN puestos pu ON pu.id = me.puesto_id "
        "JOIN municipios mu ON mu.id = pu.municipio_id "
        f"WHERE pa.corporacion = 'CA' AND ca.es_lista = 0 "
        f"AND mu.nombre IN ({placeholders}) "
        "GROUP BY ca.id, pa.codpar, ca.codcan, ca.nombre_fuente "
        "ORDER BY votos_consolidados DESC, pa.codpar, ca.codcan "
        f"LIMIT {TOP_CANDIDATES}",
        municipality_order,
    ).fetchall()
    if len(candidate_rows) != TOP_CANDIDATES:
        raise HeatmapError(
            f"se esperaban {TOP_CANDIDATES} candidatos CA y se obtuvieron "
            f"{len(candidate_rows)}"
        )

    totals_by_municipality: dict[str, int] = {}
    for name in municipality_order:
        total = connection.execute(
            "SELECT COALESCE(SUM(rp.votos), 0) "
            "FROM resultados_partido rp "
            "JOIN partidos pa ON pa.id = rp.partido_id "
            "JOIN mesas me ON me.id = rp.mesa_id "
            "JOIN puestos pu ON pu.id = me.puesto_id "
            "WHERE pa.corporacion = 'CA' AND pu.municipio_id = ?",
            (municipality_ids[name],),
        ).fetchone()[0]
        total = int(total)
        if total <= 0:
            raise HeatmapError(f"el total CA de {name} debe ser positivo")
        totals_by_municipality[name] = total

    candidate_ids = tuple(int(row["id"]) for row in candidate_rows)
    candidate_placeholders = _placeholders(len(candidate_ids))
    vote_rows = connection.execute(
        "SELECT rc.candidato_id, mu.nombre AS municipio, SUM(rc.votos) AS votos "
        "FROM resultados_candidato rc "
        "JOIN mesas me ON me.id = rc.mesa_id "
        "JOIN puestos pu ON pu.id = me.puesto_id "
        "JOIN municipios mu ON mu.id = pu.municipio_id "
        f"WHERE rc.candidato_id IN ({candidate_placeholders}) "
        f"AND mu.nombre IN ({placeholders}) "
        "GROUP BY rc.candidato_id, mu.id, mu.nombre",
        (*candidate_ids, *municipality_order),
    ).fetchall()
    vote_lookup = {
        (int(row["candidato_id"]), str(row["municipio"])): int(row["votos"])
        for row in vote_rows
    }

    votes = np.array(
        [
            [vote_lookup.get((candidate_id, name), 0) for name in municipality_order]
            for candidate_id in candidate_ids
        ],
        dtype=np.int64,
    )
    totals = np.array(
        [totals_by_municipality[name] for name in municipality_order],
        dtype=np.float64,
    )
    percentages = votes.astype(np.float64) * 100.0 / totals[np.newaxis, :]
    labels = tuple(
        f"{str(row['nombre_fuente']).title()}\nCA {int(row['codpar'])}/{row['codcan']}"
        for row in candidate_rows
    )

    return HeatmapData(
        municipalities=municipality_order,
        candidate_labels=labels,
        candidate_keys=tuple(
            (int(row["codpar"]), str(row["codcan"])) for row in candidate_rows
        ),
        percentages=percentages,
        votes=votes,
        municipality_totals=tuple(int(value) for value in totals),
        consolidated_votes=tuple(
            int(row["votos_consolidados"]) for row in candidate_rows
        ),
    )


def render_heatmap(data: HeatmapData, output_path: str | Path) -> int:
    """Renderiza una matriz anotada y devuelve el tamaño final en bytes."""

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    color_map = LinearSegmentedColormap.from_list(
        "utl_blue", ("#F4F8FC", "#B8D1EB", "#4E86BD", "#173E70")
    )
    figure, axis = plt.subplots(figsize=(12.8, 8.4), dpi=180)
    image = axis.imshow(data.percentages, cmap=color_map, aspect="auto", vmin=0)

    maximum = float(data.percentages.max())
    contrast_threshold = maximum * 0.58
    for row in range(data.percentages.shape[0]):
        for column in range(data.percentages.shape[1]):
            value = float(data.percentages[row, column])
            axis.text(
                column,
                row,
                f"{value:.1f}%",
                ha="center",
                va="center",
                color="white" if value >= contrast_threshold else "#15243A",
                fontsize=10.5,
                fontweight="bold",
            )

    axis.set_xticks(range(len(data.municipalities)), labels=data.municipalities)
    axis.set_yticks(range(len(data.candidate_labels)), labels=data.candidate_labels)
    axis.tick_params(axis="x", labelsize=11, pad=9, length=0)
    axis.tick_params(axis="y", labelsize=9.5, pad=8, length=0)
    axis.set_xlabel("Municipio", fontsize=11, labelpad=12)
    axis.set_ylabel("Top 8 candidaturas CA por votación consolidada", fontsize=11)
    axis.set_title(
        "Participación de las principales candidaturas a la Cámara",
        loc="left",
        fontsize=16,
        fontweight="bold",
        color="#173E70",
        pad=20,
    )
    axis.set_xticks(np.arange(-0.5, len(data.municipalities), 1), minor=True)
    axis.set_yticks(np.arange(-0.5, len(data.candidate_labels), 1), minor=True)
    axis.grid(which="minor", color="white", linewidth=2)
    axis.tick_params(which="minor", bottom=False, left=False)
    for spine in axis.spines.values():
        spine.set_visible(False)

    color_bar = figure.colorbar(image, ax=axis, fraction=0.035, pad=0.025)
    color_bar.set_label("% del total de votos CA del municipio", fontsize=10)
    color_bar.ax.tick_params(labelsize=9)
    color_bar.outline.set_visible(False)
    figure.text(
        0.125,
        0.025,
        "Fuente: resultados preliminares Boyacá 2026. "
        "Porcentaje = votos del candidato / votos CA totales del municipio.",
        ha="left",
        fontsize=8.8,
        color="#526173",
    )
    figure.tight_layout(rect=(0.02, 0.055, 0.98, 0.96))
    figure.savefig(
        output,
        format="png",
        bbox_inches="tight",
        facecolor="white",
        metadata={"Software": "mesa_prueba_utl_2026"},
    )
    plt.close(figure)
    size = output.stat().st_size
    if size <= 10_000:
        raise HeatmapError(f"el PNG debe pesar más de 10 KB; bytes={size}")
    return size


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=DEFAULT_DATABASE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)

    connection = connect_database(args.db)
    try:
        data = load_heatmap_data(connection)
    finally:
        connection.close()
    size = render_heatmap(data, args.output)
    print(
        f"HEATMAP candidatos={len(data.candidate_labels)} "
        f"municipios={len(data.municipalities)} bytes={size}"
    )
    print(
        f"INFO salida={args.output} criterio=top_8_votos_ca_consolidados "
        "metrica=porcentaje_total_ca_municipal"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
