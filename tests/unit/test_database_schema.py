from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from db.database import assert_integrity, initialize_database, integrity_report

EXPECTED_TABLES = {
    "carga_log",
    "municipios",
    "puestos",
    "mesas",
    "partidos",
    "candidatos",
    "resumen_mesa",
    "resultados_partido",
    "resultados_candidato",
}

EXPECTED_INDEXES = {
    "idx_puestos_municipio",
    "idx_partidos_codpar_corporacion",
    "idx_resultados_partido_partido_mesa",
    "idx_resultados_candidato_candidato_mesa",
    "idx_carga_log_estado_inicio",
}


class DatabaseSchemaTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temporary.name) / "test.db"
        self.connection = initialize_database(self.database_path)

    def tearDown(self) -> None:
        self.connection.close()
        self.temporary.cleanup()

    def _insert_minimum_graph(self) -> None:
        self.connection.execute(
            "INSERT INTO carga_log (iniciado_en, estado, corporacion, ambito_codigo, fuente_url) "
            "VALUES (?, ?, ?, ?, ?)",
            ("2026-07-12T20:00:00-05:00", "INICIADA", "CA", "0700001010001000001", "fixture"),
        )
        self.connection.execute(
            "INSERT INTO municipios (codigo, nombre) VALUES (?, ?)", ("0700001", "TUNJA")
        )
        self.connection.execute(
            "INSERT INTO puestos (municipio_id, codigo, nombre, mesas_esperadas) "
            "VALUES (1, ?, ?, ?)",
            ("0700001010001", "PUESTO PRUEBA", 1),
        )
        self.connection.execute(
            "INSERT INTO mesas (puesto_id, numero, codigo) VALUES (1, 1, ?)",
            ("0700001010001000001",),
        )
        self.connection.execute(
            "INSERT INTO partidos (corporacion, codpar, nombre) VALUES ('CA', 5, 'ALIANZA VERDE')"
        )
        self.connection.execute(
            "INSERT INTO candidatos "
            "(partido_id, codcan, nombre_fuente, nombre_normalizado, es_lista) "
            "VALUES (1, '101', 'ANA PÉREZ', 'ANA PEREZ', 0)"
        )

    def test_schema_is_repeatable_and_contains_required_tables(self) -> None:
        second = initialize_database(self.database_path)
        second.close()
        tables = {
            row[0]
            for row in self.connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%'"
            )
        }
        self.assertEqual(tables, EXPECTED_TABLES)
        self.assertEqual(self.connection.execute("PRAGMA foreign_keys").fetchone()[0], 1)

    def test_foreign_key_and_check_constraints_are_enforced(self) -> None:
        with self.assertRaises(sqlite3.IntegrityError):
            self.connection.execute(
                "INSERT OR IGNORE INTO puestos (municipio_id, codigo, nombre, mesas_esperadas) "
                "VALUES (999, '0700001010001', 'INVALIDO', 1)"
            )
        self._insert_minimum_graph()
        with self.assertRaises(sqlite3.IntegrityError):
            self.connection.execute(
                "INSERT INTO resultados_partido (mesa_id, partido_id, carga_id, votos) "
                "VALUES (1, 1, 1, -1)"
            )

    def test_insert_or_ignore_is_idempotent_on_natural_keys(self) -> None:
        self._insert_minimum_graph()
        statement = (
            "INSERT OR IGNORE INTO resultados_partido "
            "(mesa_id, partido_id, carga_id, votos) VALUES (1, 1, 1, 42)"
        )
        first = self.connection.execute(statement)
        second = self.connection.execute(statement)
        self.assertEqual(first.rowcount, 1)
        self.assertEqual(second.rowcount, 0)
        self.assertEqual(
            self.connection.execute("SELECT COUNT(*) FROM resultados_partido").fetchone()[0], 1
        )

    def test_explicit_indexes_exist_and_support_analytical_access(self) -> None:
        indexes = {
            row[0]
            for row in self.connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'index'"
            )
        }
        self.assertTrue(EXPECTED_INDEXES.issubset(indexes))
        plan = " ".join(
            str(column)
            for row in self.connection.execute(
                "EXPLAIN QUERY PLAN "
                "SELECT mesa_id, votos FROM resultados_partido WHERE partido_id = 1"
            )
            for column in row
        )
        self.assertIn("idx_resultados_partido_partido_mesa", plan)

    def test_integrity_report_is_clean(self) -> None:
        self._insert_minimum_graph()
        report = integrity_report(self.connection)
        self.assertTrue(report.ok)
        assert_integrity(self.connection)
