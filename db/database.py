"""Inicialización y verificación de SQLite con integridad activa."""

from __future__ import annotations

import sqlite3
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

DEFAULT_SCHEMA_PATH = Path(__file__).with_name("schema.sql")


class DatabaseIntegrityError(RuntimeError):
    """La base contiene una violación estructural o referencial."""


@dataclass(frozen=True)
class IntegrityReport:
    integrity_messages: tuple[str, ...]
    foreign_key_violations: tuple[tuple[object, ...], ...]

    @property
    def ok(self) -> bool:
        return self.integrity_messages == ("ok",) and not self.foreign_key_violations


def connect_database(path: str | Path) -> sqlite3.Connection:
    connection = sqlite3.connect(Path(path), timeout=30.0)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA busy_timeout = 5000")
    enabled = connection.execute("PRAGMA foreign_keys").fetchone()[0]
    if enabled != 1:
        connection.close()
        raise DatabaseIntegrityError("SQLite no habilitó foreign_keys")
    return connection


def initialize_database(
    path: str | Path,
    *,
    schema_path: str | Path = DEFAULT_SCHEMA_PATH,
) -> sqlite3.Connection:
    connection = connect_database(path)
    schema = Path(schema_path).read_text(encoding="utf-8")
    try:
        connection.executescript(schema)
    except Exception:
        connection.close()
        raise
    return connection


def integrity_report(connection: sqlite3.Connection) -> IntegrityReport:
    integrity = tuple(row[0] for row in connection.execute("PRAGMA integrity_check"))
    foreign_keys: Sequence[sqlite3.Row] = connection.execute("PRAGMA foreign_key_check").fetchall()
    return IntegrityReport(
        integrity_messages=integrity,
        foreign_key_violations=tuple(tuple(row) for row in foreign_keys),
    )


def assert_integrity(connection: sqlite3.Connection) -> None:
    report = integrity_report(connection)
    if not report.ok:
        raise DatabaseIntegrityError(
            f"integrity_check={report.integrity_messages}; "
            f"foreign_key_violations={report.foreign_key_violations}"
        )

