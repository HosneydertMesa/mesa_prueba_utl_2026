"""Carga transaccional e idempotente de una respuesta ACT de mesa."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from scraper.act_parser import TableResult, parse_table_result
from scraper.nomenclator import MunicipalityScope, PartyInfo, PositionScope, party_catalog


class EtlError(RuntimeError):
    """La carga no puede continuar sin comprometer integridad o trazabilidad."""


@dataclass(frozen=True)
class LoadStats:
    load_id: int
    rows_read: int
    rows_inserted: int
    rows_skipped: int


def canonical_payload_hash(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


def _insert_or_get_id(
    connection: sqlite3.Connection,
    *,
    insert_sql: str,
    insert_params: Sequence[object],
    select_sql: str,
    select_params: Sequence[object],
    expected: Mapping[str, object],
    entity: str,
) -> int:
    connection.execute(insert_sql, insert_params)
    row = connection.execute(select_sql, select_params).fetchone()
    if row is None:
        raise EtlError(f"no se pudo resolver {entity}")
    for field, expected_value in expected.items():
        if row[field] != expected_value:
            raise EtlError(
                f"conflicto en {entity}.{field}: existente={row[field]!r} nuevo={expected_value!r}"
            )
    return int(row["id"])


def _insert_fact_or_validate(
    connection: sqlite3.Connection,
    *,
    insert_sql: str,
    insert_params: Sequence[object],
    select_sql: str,
    select_params: Sequence[object],
    expected: Mapping[str, object],
    entity: str,
) -> bool:
    cursor = connection.execute(insert_sql, insert_params)
    if cursor.rowcount == 1:
        return True
    row = connection.execute(select_sql, select_params).fetchone()
    if row is None:
        raise EtlError(f"{entity} fue omitido sin fila existente")
    for field, expected_value in expected.items():
        if row[field] != expected_value:
            raise EtlError(
                f"resultado cambió para {entity}.{field}: "
                f"existente={row[field]!r} nuevo={expected_value!r}"
            )
    return False


def _resolve_dimensions(
    connection: sqlite3.Connection,
    result: TableResult,
    municipality: MunicipalityScope,
    position: PositionScope,
) -> tuple[int, int, int]:
    if result.scope_code[:7] != municipality.code:
        raise EtlError(f"mesa {result.scope_code} no pertenece a {municipality.code}")
    if not result.scope_code.startswith(position.code):
        raise EtlError(f"mesa {result.scope_code} no pertenece al puesto {position.code}")
    if position not in municipality.positions:
        raise EtlError(f"puesto {position.code} no pertenece al municipio resuelto")
    table_number = int(result.scope_code[-6:])
    if table_number < 1 or table_number > position.table_count:
        raise EtlError(
            f"número de mesa {table_number} fuera de rango para puesto {position.code}"
        )

    municipality_id = _insert_or_get_id(
        connection,
        insert_sql=(
            "INSERT OR IGNORE INTO municipios (codigo, nombre, departamento_codigo) "
            "VALUES (?, ?, ?)"
        ),
        insert_params=(municipality.code, municipality.name, result.department_code),
        select_sql=(
            "SELECT id, nombre, departamento_codigo FROM municipios WHERE codigo = ?"
        ),
        select_params=(municipality.code,),
        expected={"nombre": municipality.name, "departamento_codigo": result.department_code},
        entity=f"municipio[{municipality.code}]",
    )
    position_id = _insert_or_get_id(
        connection,
        insert_sql=(
            "INSERT OR IGNORE INTO puestos "
            "(municipio_id, codigo, nombre, mesas_esperadas) VALUES (?, ?, ?, ?)"
        ),
        insert_params=(municipality_id, position.code, position.name, position.table_count),
        select_sql=(
            "SELECT id, municipio_id, nombre, mesas_esperadas FROM puestos WHERE codigo = ?"
        ),
        select_params=(position.code,),
        expected={
            "municipio_id": municipality_id,
            "nombre": position.name,
            "mesas_esperadas": position.table_count,
        },
        entity=f"puesto[{position.code}]",
    )
    table_id = _insert_or_get_id(
        connection,
        insert_sql=(
            "INSERT OR IGNORE INTO mesas (puesto_id, numero, codigo) VALUES (?, ?, ?)"
        ),
        insert_params=(position_id, table_number, result.scope_code),
        select_sql="SELECT id, puesto_id, numero FROM mesas WHERE codigo = ?",
        select_params=(result.scope_code,),
        expected={"puesto_id": position_id, "numero": table_number},
        entity=f"mesa[{result.scope_code}]",
    )
    return municipality_id, position_id, table_id


def _resolve_party(
    connection: sqlite3.Connection,
    corporation: str,
    info: PartyInfo,
) -> int:
    return _insert_or_get_id(
        connection,
        insert_sql=(
            "INSERT OR IGNORE INTO partidos (corporacion, codpar, nombre) VALUES (?, ?, ?)"
        ),
        insert_params=(corporation, info.runtime_code, info.name),
        select_sql=(
            "SELECT id, nombre FROM partidos WHERE corporacion = ? AND codpar = ?"
        ),
        select_params=(corporation, info.runtime_code),
        expected={"nombre": info.name},
        entity=f"partido[{corporation},{info.runtime_code}]",
    )


def load_table_result(
    connection: sqlite3.Connection,
    result: TableResult,
    municipality: MunicipalityScope,
    position: PositionScope,
    catalog: Mapping[int, PartyInfo],
    *,
    source_url: str,
    source_etag: str | None,
    source_hash: str,
) -> LoadStats:
    rows_read = 1 + result.party_rows + result.candidate_rows
    started_at = _utc_now()
    cursor = connection.execute(
        "INSERT INTO carga_log "
        "(iniciado_en, estado, corporacion, ambito_codigo, fuente_url, fuente_etag, "
        "fuente_sha256, filas_leidas) VALUES (?, 'INICIADA', ?, ?, ?, ?, ?, ?)",
        (
            started_at,
            result.corporation,
            result.scope_code,
            source_url,
            source_etag,
            source_hash,
            rows_read,
        ),
    )
    load_id = int(cursor.lastrowid)
    connection.commit()
    inserted = 0

    try:
        with connection:
            _, _, table_id = _resolve_dimensions(connection, result, municipality, position)
            summary_values = {
                "censo": result.census,
                "votantes": result.voters,
                "votos_nulos": result.null_votes,
                "votos_no_marcados": result.unmarked_votes,
                "votos_blancos": result.blank_votes,
                "votos_validos": result.valid_votes,
            }
            inserted += int(
                _insert_fact_or_validate(
                    connection,
                    insert_sql=(
                        "INSERT OR IGNORE INTO resumen_mesa "
                        "(mesa_id, corporacion, carga_id, censo, votantes, votos_nulos, "
                        "votos_no_marcados, votos_blancos, votos_validos) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
                    ),
                    insert_params=(
                        table_id,
                        result.corporation,
                        load_id,
                        *summary_values.values(),
                    ),
                    select_sql=(
                        "SELECT censo, votantes, votos_nulos, votos_no_marcados, "
                        "votos_blancos, votos_validos FROM resumen_mesa "
                        "WHERE mesa_id = ? AND corporacion = ?"
                    ),
                    select_params=(table_id, result.corporation),
                    expected=summary_values,
                    entity=f"resumen[{result.scope_code},{result.corporation}]",
                )
            )

            for party in result.parties:
                info = catalog.get(party.code)
                if info is None:
                    raise EtlError(f"partido ACT {party.code} no existe en nomenclator")
                party_id = _resolve_party(connection, result.corporation, info)
                inserted += int(
                    _insert_fact_or_validate(
                        connection,
                        insert_sql=(
                            "INSERT OR IGNORE INTO resultados_partido "
                            "(mesa_id, partido_id, carga_id, votos) VALUES (?, ?, ?, ?)"
                        ),
                        insert_params=(table_id, party_id, load_id, party.votes),
                        select_sql=(
                            "SELECT votos FROM resultados_partido "
                            "WHERE mesa_id = ? AND partido_id = ?"
                        ),
                        select_params=(table_id, party_id),
                        expected={"votos": party.votes},
                        entity=f"resultado_partido[{result.scope_code},{party.code}]",
                    )
                )

                for candidate in party.candidates:
                    candidate_id = _insert_or_get_id(
                        connection,
                        insert_sql=(
                            "INSERT OR IGNORE INTO candidatos "
                            "(partido_id, codcan, nombre_fuente, nombre_normalizado, es_lista) "
                            "VALUES (?, ?, ?, ?, ?)"
                        ),
                        insert_params=(
                            party_id,
                            candidate.code,
                            candidate.source_name,
                            candidate.normalized_name,
                            int(candidate.is_list),
                        ),
                        select_sql=(
                            "SELECT id, nombre_normalizado, es_lista FROM candidatos "
                            "WHERE partido_id = ? AND codcan = ?"
                        ),
                        select_params=(party_id, candidate.code),
                        expected={
                            "nombre_normalizado": candidate.normalized_name,
                            "es_lista": int(candidate.is_list),
                        },
                        entity=f"candidato[{party.code},{candidate.code}]",
                    )
                    inserted += int(
                        _insert_fact_or_validate(
                            connection,
                            insert_sql=(
                                "INSERT OR IGNORE INTO resultados_candidato "
                                "(mesa_id, candidato_id, carga_id, votos) VALUES (?, ?, ?, ?)"
                            ),
                            insert_params=(table_id, candidate_id, load_id, candidate.votes),
                            select_sql=(
                                "SELECT votos FROM resultados_candidato "
                                "WHERE mesa_id = ? AND candidato_id = ?"
                            ),
                            select_params=(table_id, candidate_id),
                            expected={"votos": candidate.votes},
                            entity=(
                                f"resultado_candidato[{result.scope_code},"
                                f"{party.code},{candidate.code}]"
                            ),
                        )
                    )

            skipped = rows_read - inserted
            connection.execute(
                "UPDATE carga_log SET finalizado_en = ?, estado = 'COMPLETADA', "
                "filas_insertadas = ?, filas_omitidas = ? WHERE id = ?",
                (_utc_now(), inserted, skipped, load_id),
            )
        return LoadStats(load_id, rows_read, inserted, skipped)
    except Exception as error:
        connection.rollback()
        connection.execute(
            "UPDATE carga_log SET finalizado_en = ?, estado = 'FALLIDA', error = ?, "
            "filas_insertadas = 0, filas_omitidas = 0 WHERE id = ?",
            (_utc_now(), str(error)[:2000], load_id),
        )
        connection.commit()
        raise


def load_act_payload(
    connection: sqlite3.Connection,
    payload: Mapping[str, Any],
    nomenclator: Mapping[str, Any],
    municipality: MunicipalityScope,
    position: PositionScope,
    corporation: str,
    *,
    expected_scope_code: str,
    source_url: str,
    source_etag: str | None = None,
) -> LoadStats:
    result = parse_table_result(
        payload,
        corporation,
        expected_scope_code=expected_scope_code,
    )
    return load_table_result(
        connection,
        result,
        municipality,
        position,
        party_catalog(nomenclator),
        source_url=source_url,
        source_etag=source_etag,
        source_hash=canonical_payload_hash(payload),
    )
