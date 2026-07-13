"""Genera el scatter CA vs SE por mesa exigido por el Reto 5.2."""

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
from scipy.stats import pearsonr
from statsmodels.api import OLS, add_constant

matplotlib.use("Agg")
from matplotlib import pyplot as plt  # noqa: E402

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from db.database import connect_database  # noqa: E402

MUNICIPALITIES: Final = ("TUNJA", "PAIPA", "SOGAMOSO", "DUITAMA")
MUNICIPALITY_COLORS: Final = {
    "TUNJA": "#1E477D",
    "PAIPA": "#007C34",
    "SOGAMOSO": "#7B2D8B",
    "DUITAMA": "#E07B00",
}
DEFAULT_DATABASE: Final = Path("db/puestos_2026.db")
DEFAULT_OUTPUT: Final = Path("viz/scatter_ca_se.png")


class ScatterError(RuntimeError):
    """La base no satisface el contrato mínimo del scatter."""


@dataclass(frozen=True)
class ScatterData:
    """Observaciones pareadas de votos válidos CA y SE por mesa."""

    camera_votes: np.ndarray
    senate_votes: np.ndarray
    municipalities: tuple[str, ...]
    table_codes: tuple[str, ...]


@dataclass(frozen=True)
class RegressionStatistics:
    """Estadísticos descriptivos exigidos por el contrato."""

    pearson_r: float
    slope: float
    intercept: float
    table_count: int


def _placeholders(size: int) -> str:
    return ", ".join("?" for _ in range(size))


def load_scatter_data(
    connection: sqlite3.Connection,
    *,
    municipality_order: tuple[str, ...] = MUNICIPALITIES,
) -> ScatterData:
    """Carga una observación CA/SE por cada mesa de los cuatro municipios."""

    if len(municipality_order) != 4 or len(set(municipality_order)) != 4:
        raise ScatterError("el scatter requiere exactamente cuatro municipios únicos")
    placeholders = _placeholders(len(municipality_order))
    catalog = {
        str(row["nombre"])
        for row in connection.execute(
            f"SELECT nombre FROM municipios WHERE nombre IN ({placeholders})",
            municipality_order,
        )
    }
    missing = [name for name in municipality_order if name not in catalog]
    if missing:
        raise ScatterError("faltan municipios requeridos: " + ", ".join(missing))

    expected_tables = int(
        connection.execute(
            "SELECT COUNT(*) FROM mesas me "
            "JOIN puestos pu ON pu.id = me.puesto_id "
            "JOIN municipios mu ON mu.id = pu.municipio_id "
            f"WHERE mu.nombre IN ({placeholders})",
            municipality_order,
        ).fetchone()[0]
    )
    rows = connection.execute(
        "SELECT me.codigo AS mesa_codigo, mu.nombre AS municipio, "
        "ca.votos_validos AS votos_ca, se.votos_validos AS votos_se "
        "FROM mesas me "
        "JOIN puestos pu ON pu.id = me.puesto_id "
        "JOIN municipios mu ON mu.id = pu.municipio_id "
        "JOIN resumen_mesa ca ON ca.mesa_id = me.id AND ca.corporacion = 'CA' "
        "JOIN resumen_mesa se ON se.mesa_id = me.id AND se.corporacion = 'SE' "
        f"WHERE mu.nombre IN ({placeholders}) "
        "ORDER BY CASE mu.nombre "
        "WHEN 'TUNJA' THEN 1 WHEN 'PAIPA' THEN 2 "
        "WHEN 'SOGAMOSO' THEN 3 WHEN 'DUITAMA' THEN 4 ELSE 5 END, me.codigo",
        municipality_order,
    ).fetchall()
    if len(rows) != expected_tables:
        raise ScatterError(
            "cada mesa debe tener resumen CA y SE: "
            f"pareadas={len(rows)} esperadas={expected_tables}"
        )
    if len(rows) < 2:
        raise ScatterError("se requieren al menos dos mesas para la regresión")

    camera_votes = np.array([int(row["votos_ca"]) for row in rows], dtype=np.float64)
    senate_votes = np.array([int(row["votos_se"]) for row in rows], dtype=np.float64)
    if np.ptp(camera_votes) == 0 or np.ptp(senate_votes) == 0:
        raise ScatterError("CA y SE deben tener variación para calcular Pearson y OLS")

    return ScatterData(
        camera_votes=camera_votes,
        senate_votes=senate_votes,
        municipalities=tuple(str(row["municipio"]) for row in rows),
        table_codes=tuple(str(row["mesa_codigo"]) for row in rows),
    )


def fit_regression(data: ScatterData) -> RegressionStatistics:
    """Ajusta SE = intercepto + pendiente * CA y calcula Pearson."""

    if len(data.camera_votes) != len(data.senate_votes):
        raise ScatterError("los vectores CA y SE deben tener igual longitud")
    design_matrix = add_constant(data.camera_votes, has_constant="add")
    model = OLS(data.senate_votes, design_matrix).fit()
    correlation = pearsonr(data.camera_votes, data.senate_votes).statistic
    if not np.isfinite(correlation) or not np.all(np.isfinite(model.params)):
        raise ScatterError("Pearson u OLS produjo valores no finitos")
    return RegressionStatistics(
        pearson_r=float(correlation),
        intercept=float(model.params[0]),
        slope=float(model.params[1]),
        table_count=len(data.camera_votes),
    )


def format_statistics(statistics: RegressionStatistics) -> str:
    """Devuelve exactamente el stdout capturado por el manifest."""

    return (
        f"r={statistics.pearson_r:.3f} | pendiente={statistics.slope:.3f} | "
        f"n_mesas={statistics.table_count}"
    )


def render_scatter(
    data: ScatterData,
    statistics: RegressionStatistics,
    output_path: str | Path,
) -> int:
    """Renderiza puntos por municipio, OLS global y anotación estadística."""

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    figure, axis = plt.subplots(figsize=(11.8, 8.2), dpi=180)

    municipality_values = np.array(data.municipalities, dtype=object)
    for municipality in MUNICIPALITIES:
        mask = municipality_values == municipality
        axis.scatter(
            data.camera_votes[mask],
            data.senate_votes[mask],
            s=28,
            alpha=0.58,
            color=MUNICIPALITY_COLORS[municipality],
            edgecolors="white",
            linewidths=0.35,
            label=f"{municipality.title()} (n={int(mask.sum())})",
        )

    x_line = np.linspace(float(data.camera_votes.min()), float(data.camera_votes.max()), 200)
    y_line = statistics.intercept + statistics.slope * x_line
    axis.plot(
        x_line,
        y_line,
        color="#15243A",
        linewidth=2.4,
        label="OLS global",
        zorder=5,
    )
    axis.text(
        0.035,
        0.95,
        f"r de Pearson = {statistics.pearson_r:.3f}\n"
        f"Pendiente OLS = {statistics.slope:.3f}\n"
        f"n = {statistics.table_count:,} mesas".replace(",", "."),
        transform=axis.transAxes,
        va="top",
        ha="left",
        fontsize=10.5,
        color="#15243A",
        bbox={
            "boxstyle": "round,pad=0.55",
            "facecolor": "white",
            "edgecolor": "#CAD5E1",
            "alpha": 0.94,
        },
    )
    axis.set_title(
        "Relación entre votos válidos de Cámara y Senado por mesa",
        loc="left",
        fontsize=16,
        fontweight="bold",
        color="#173E70",
        pad=18,
    )
    axis.set_xlabel("Votos válidos Cámara (CA) por mesa", fontsize=11, labelpad=10)
    axis.set_ylabel("Votos válidos Senado (SE) por mesa", fontsize=11, labelpad=10)
    axis.grid(color="#DCE4EC", linewidth=0.75, alpha=0.8)
    axis.set_axisbelow(True)
    axis.tick_params(axis="both", labelsize=9.5, colors="#34465A")
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)
    axis.spines["left"].set_color("#AEBBC8")
    axis.spines["bottom"].set_color("#AEBBC8")
    axis.legend(
        loc="lower right",
        frameon=True,
        facecolor="white",
        edgecolor="#CAD5E1",
        framealpha=0.96,
        fontsize=9,
    )
    figure.text(
        0.11,
        0.025,
        "Asociación descriptiva del mismo evento electoral; no implica causalidad "
        "ni transferencia de votos.",
        ha="left",
        fontsize=8.8,
        color="#526173",
    )
    figure.tight_layout(rect=(0.03, 0.055, 0.98, 0.97))
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
        raise ScatterError(f"el PNG debe pesar más de 10 KB; bytes={size}")
    return size


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=DEFAULT_DATABASE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)

    connection = connect_database(args.db)
    try:
        data = load_scatter_data(connection)
    finally:
        connection.close()
    statistics = fit_regression(data)
    render_scatter(data, statistics, args.output)
    print(format_statistics(statistics))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
