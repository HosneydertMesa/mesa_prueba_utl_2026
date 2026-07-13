from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from viz.scatter import (
    ScatterError,
    fit_regression,
    format_statistics,
    load_scatter_data,
    render_scatter,
)

BASE_MUNICIPALITIES = ("TUNJA", "PAIPA", "SOGAMOSO", "DUITAMA")
BONUS_MUNICIPALITIES = ("CHIQUINQUIRA", "PUERTO BOYACA", "MONIQUIRA")


def scatter_connection(
    municipalities: tuple[str, ...] = BASE_MUNICIPALITIES,
) -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.executescript(
        """
        CREATE TABLE municipios (id INTEGER PRIMARY KEY, nombre TEXT NOT NULL);
        CREATE TABLE puestos (
            id INTEGER PRIMARY KEY,
            municipio_id INTEGER NOT NULL
        );
        CREATE TABLE mesas (
            id INTEGER PRIMARY KEY,
            puesto_id INTEGER NOT NULL,
            codigo TEXT NOT NULL
        );
        CREATE TABLE resumen_mesa (
            mesa_id INTEGER NOT NULL,
            corporacion TEXT NOT NULL,
            votos_validos INTEGER NOT NULL
        );
        """
    )
    table_id = 0
    for municipality_id, municipality in enumerate(municipalities, start=1):
        connection.execute(
            "INSERT INTO municipios(id, nombre) VALUES (?, ?)",
            (municipality_id, municipality),
        )
        connection.execute(
            "INSERT INTO puestos(id, municipio_id) VALUES (?, ?)",
            (municipality_id, municipality_id),
        )
        for _ in range(3):
            table_id += 1
            camera_votes = table_id * 10
            senate_votes = 2 * camera_votes + 5
            connection.execute(
                "INSERT INTO mesas(id, puesto_id, codigo) VALUES (?, ?, ?)",
                (table_id, municipality_id, f"MESA-{table_id:03d}"),
            )
            connection.executemany(
                "INSERT INTO resumen_mesa(mesa_id, corporacion, votos_validos) "
                "VALUES (?, ?, ?)",
                (
                    (table_id, "CA", camera_votes),
                    (table_id, "SE", senate_votes),
                ),
            )
    connection.commit()
    return connection


class ScatterIntegrationTests(unittest.TestCase):
    def test_loads_one_paired_observation_per_table(self) -> None:
        connection = scatter_connection()
        try:
            data = load_scatter_data(connection)
        finally:
            connection.close()

        self.assertEqual(len(data.camera_votes), 12)
        self.assertEqual(len(set(data.table_codes)), 12)
        self.assertEqual(data.municipalities.count("TUNJA"), 3)
        self.assertEqual(data.municipalities.count("DUITAMA"), 3)

    def test_calculates_exact_pearson_ols_and_stdout(self) -> None:
        connection = scatter_connection()
        try:
            statistics = fit_regression(load_scatter_data(connection))
        finally:
            connection.close()

        self.assertAlmostEqual(statistics.pearson_r, 1.0)
        self.assertAlmostEqual(statistics.slope, 2.0)
        self.assertAlmostEqual(statistics.intercept, 5.0)
        self.assertEqual(
            format_statistics(statistics),
            "r=1.000 | pendiente=2.000 | n_mesas=12",
        )

    def test_rejects_table_without_both_corporations(self) -> None:
        connection = scatter_connection()
        connection.execute(
            "DELETE FROM resumen_mesa WHERE mesa_id = 12 AND corporacion = 'SE'"
        )
        try:
            with self.assertRaisesRegex(ScatterError, "pareadas=11 esperadas=12"):
                load_scatter_data(connection)
        finally:
            connection.close()

    def test_supports_seven_municipalities_for_bonus_dashboard(self) -> None:
        municipalities = (*BASE_MUNICIPALITIES, *BONUS_MUNICIPALITIES)
        connection = scatter_connection(municipalities)
        try:
            data = load_scatter_data(
                connection, municipality_order=municipalities
            )
            statistics = fit_regression(data)
        finally:
            connection.close()

        self.assertEqual(len(data.camera_votes), 21)
        self.assertEqual(data.municipalities.count("MONIQUIRA"), 3)
        self.assertEqual(statistics.table_count, 21)

    def test_renders_png_over_required_size(self) -> None:
        connection = scatter_connection()
        try:
            data = load_scatter_data(connection)
        finally:
            connection.close()
        statistics = fit_regression(data)
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "scatter.png"
            size = render_scatter(data, statistics, output)
            header = output.read_bytes()[:24]
            self.assertEqual(header[:8], b"\x89PNG\r\n\x1a\n")
            width = int.from_bytes(header[16:20], "big")
            height = int.from_bytes(header[20:24], "big")

        self.assertGreater(size, 10_000)
        self.assertGreaterEqual(width, 1600)
        self.assertGreaterEqual(height, 1000)


if __name__ == "__main__":
    unittest.main()
