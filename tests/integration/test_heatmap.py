from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from viz.heatmap import HeatmapError, load_heatmap_data, render_heatmap


def heatmap_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.executescript(
        """
        CREATE TABLE municipios (id INTEGER PRIMARY KEY, nombre TEXT NOT NULL);
        CREATE TABLE puestos (
            id INTEGER PRIMARY KEY,
            municipio_id INTEGER NOT NULL
        );
        CREATE TABLE mesas (id INTEGER PRIMARY KEY, puesto_id INTEGER NOT NULL);
        CREATE TABLE partidos (
            id INTEGER PRIMARY KEY,
            corporacion TEXT NOT NULL,
            codpar INTEGER NOT NULL
        );
        CREATE TABLE candidatos (
            id INTEGER PRIMARY KEY,
            partido_id INTEGER NOT NULL,
            codcan TEXT NOT NULL,
            nombre_fuente TEXT NOT NULL,
            es_lista INTEGER NOT NULL
        );
        CREATE TABLE resultados_partido (
            mesa_id INTEGER NOT NULL,
            partido_id INTEGER NOT NULL,
            votos INTEGER NOT NULL
        );
        CREATE TABLE resultados_candidato (
            mesa_id INTEGER NOT NULL,
            candidato_id INTEGER NOT NULL,
            votos INTEGER NOT NULL
        );
        """
    )
    connection.execute(
        "INSERT INTO partidos(id, corporacion, codpar) VALUES (1, 'CA', 5)"
    )
    for candidate_id in range(1, 10):
        connection.execute(
            "INSERT INTO candidatos "
            "(id, partido_id, codcan, nombre_fuente, es_lista) "
            "VALUES (?, 1, ?, ?, 0)",
            (candidate_id, str(100 + candidate_id), f"CANDIDATO {candidate_id}"),
        )
    for index, municipality in enumerate(
        ("TUNJA", "PAIPA", "SOGAMOSO", "DUITAMA"), start=1
    ):
        connection.execute(
            "INSERT INTO municipios(id, nombre) VALUES (?, ?)",
            (index, municipality),
        )
        connection.execute(
            "INSERT INTO puestos(id, municipio_id) VALUES (?, ?)", (index, index)
        )
        connection.execute(
            "INSERT INTO mesas(id, puesto_id) VALUES (?, ?)", (index, index)
        )
        connection.execute(
            "INSERT INTO resultados_partido(mesa_id, partido_id, votos) "
            "VALUES (?, 1, ?)",
            (index, 1000 * index),
        )
        for candidate_id in range(1, 10):
            connection.execute(
                "INSERT INTO resultados_candidato(mesa_id, candidato_id, votos) "
                "VALUES (?, ?, ?)",
                (index, candidate_id, (10 - candidate_id) * 10 * index),
            )
    connection.commit()
    return connection


class HeatmapIntegrationTests(unittest.TestCase):
    def test_builds_ranked_eight_by_four_percentage_matrix(self) -> None:
        connection = heatmap_connection()
        try:
            data = load_heatmap_data(connection)
        finally:
            connection.close()

        self.assertEqual(data.percentages.shape, (8, 4))
        self.assertEqual(data.municipalities, ("TUNJA", "PAIPA", "SOGAMOSO", "DUITAMA"))
        self.assertEqual(data.candidate_keys[0], (5, "101"))
        self.assertNotIn((5, "109"), data.candidate_keys)
        self.assertTrue((data.percentages[0] == 9.0).all())
        self.assertEqual(data.consolidated_votes[0], 900)

    def test_rejects_missing_required_municipality(self) -> None:
        connection = heatmap_connection()
        connection.execute("DELETE FROM municipios WHERE nombre = 'DUITAMA'")
        try:
            with self.assertRaisesRegex(HeatmapError, "DUITAMA"):
                load_heatmap_data(connection)
        finally:
            connection.close()

    def test_renders_legible_png_over_required_size(self) -> None:
        connection = heatmap_connection()
        try:
            data = load_heatmap_data(connection)
        finally:
            connection.close()
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "heatmap.png"
            size = render_heatmap(data, output)
            header = output.read_bytes()[:24]
            self.assertEqual(header[:8], b"\x89PNG\r\n\x1a\n")
            width = int.from_bytes(header[16:20], "big")
            height = int.from_bytes(header[20:24], "big")

        self.assertGreater(size, 10_000)
        self.assertGreaterEqual(width, 1600)
        self.assertGreaterEqual(height, 1000)


if __name__ == "__main__":
    unittest.main()
