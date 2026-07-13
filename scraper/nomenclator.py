"""Resolución determinista de territorios y mesas desde el nomenclator oficial."""

from __future__ import annotations

import json
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator, Mapping
from urllib.parse import quote

DEFAULT_BASE_URL = "https://resultadospreccongreso2026.registraduria.gov.co"
ELECTION_CODES = {"SE": 1, "CA": 2}


class NomenclatorError(ValueError):
    """El nomenclator no cumple el contrato mínimo esperado."""


@dataclass(frozen=True)
class PositionScope:
    name: str
    code: str
    table_count: int


@dataclass(frozen=True)
class MunicipalityScope:
    name: str
    code: str
    election: str
    positions: tuple[PositionScope, ...]

    @property
    def table_count(self) -> int:
        return sum(position.table_count for position in self.positions)


def load_nomenclator(path: str | Path) -> dict[str, Any]:
    with Path(path).open(encoding="utf-8") as source:
        payload = json.load(source)
    if not isinstance(payload, dict):
        raise NomenclatorError("la raíz del nomenclator debe ser un objeto JSON")
    return payload


def normalize_name(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value.strip())
    without_accents = "".join(char for char in decomposed if not unicodedata.combining(char))
    return " ".join(without_accents.upper().split())


def _election_block(payload: Mapping[str, Any], election: str) -> list[Mapping[str, Any]]:
    election = election.upper()
    if election not in ELECTION_CODES:
        raise NomenclatorError(f"corporación no soportada: {election}")
    elections = payload.get("elec")
    scopes = payload.get("amb")
    if not isinstance(elections, list) or not isinstance(scopes, list):
        raise NomenclatorError("faltan las colecciones elec o amb")

    match = next((item for item in elections if item.get("sigla") == election), None)
    if match is None:
        raise NomenclatorError(f"la elección {election} no existe en el nomenclator")
    election_code = match.get("elec")
    block = next((item for item in scopes if item.get("elec") == election_code), None)
    if block is None or not isinstance(block.get("ambitos"), list):
        raise NomenclatorError(f"faltan ámbitos para la elección {election}")
    return block["ambitos"]


def resolve_municipality(
    payload: Mapping[str, Any],
    name: str,
    election: str,
    department_code: str = "07",
) -> MunicipalityScope:
    """Resuelve un municipio y todos sus puestos para CA o SE."""

    records = _election_block(payload, election)
    by_id = {int(record["i"]): record for record in records}
    target = normalize_name(name)
    candidates: list[Mapping[str, Any]] = []

    for record in records:
        if int(record.get("l", 0)) != 3 or normalize_name(str(record.get("n", ""))) != target:
            continue
        parent_ids = [
            int(parent_id)
            for relation in record.get("p", [])
            if int(relation.get("l", 0)) == 2
            for parent_id in relation.get("p", [])
        ]
        parents = [by_id[parent_id] for parent_id in parent_ids if parent_id in by_id]
        if any(str(parent.get("c", "")).startswith(department_code) for parent in parents):
            candidates.append(record)

    if len(candidates) != 1:
        raise NomenclatorError(
            f"se esperaba un municipio {name!r} en departamento {department_code}; "
            f"coincidencias={len(candidates)}"
        )

    municipality = candidates[0]
    positions: list[PositionScope] = []
    pending = [int(child) for relation in municipality.get("h", []) for child in relation.get("p", [])]
    visited: set[int] = set()
    while pending:
        record_id = pending.pop()
        if record_id in visited:
            continue
        visited.add(record_id)
        record = by_id.get(record_id)
        if record is None:
            raise NomenclatorError(f"ámbito hijo inexistente: {record_id}")
        level = int(record.get("l", 0))
        if level == 6:
            positions.append(
                PositionScope(
                    name=str(record["n"]),
                    code=str(record["c"]),
                    table_count=int(record.get("m", 0)),
                )
            )
        pending.extend(
            int(child) for relation in record.get("h", []) for child in relation.get("p", [])
        )

    if not positions:
        raise NomenclatorError(f"el municipio {name!r} no contiene puestos")
    return MunicipalityScope(
        name=str(municipality["n"]),
        code=str(municipality["c"]),
        election=election.upper(),
        positions=tuple(sorted(positions, key=lambda item: item.code)),
    )


def table_scope_code(position_code: str, table_number: int) -> str:
    if len(position_code) != 13:
        raise NomenclatorError("el código de puesto debe tener 13 caracteres")
    if table_number < 1 or table_number > 999_999:
        raise NomenclatorError("el número de mesa debe estar entre 1 y 999999")
    return f"{position_code}{table_number:06d}"


def iter_table_scope_codes(position: PositionScope) -> Iterator[str]:
    for table_number in range(1, position.table_count + 1):
        yield table_scope_code(position.code, table_number)


def build_act_url(election: str, scope_code: str, base_url: str = DEFAULT_BASE_URL) -> str:
    election = election.upper()
    if election not in ELECTION_CODES:
        raise NomenclatorError(f"corporación no soportada: {election}")
    if not scope_code or not scope_code.isalnum():
        raise NomenclatorError("código de ámbito inválido")
    return f"{base_url.rstrip('/')}/json/ACT/{quote(election)}/{quote(scope_code)}.json"

