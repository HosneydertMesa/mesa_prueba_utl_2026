"""Parser estricto de respuestas ACT a resultados tipados por mesa."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from scraper.nomenclator import normalize_name

ELECTION_NUMBER = {"SE": "1", "CA": "2"}
DEFAULT_CHAMBER = {"SE": "0", "CA": "1"}


class ActParseError(ValueError):
    """La respuesta ACT viola el contrato observado."""


@dataclass(frozen=True)
class CandidateResult:
    code: str
    source_name: str
    normalized_name: str
    votes: int
    is_list: bool


@dataclass(frozen=True)
class PartyResult:
    code: int
    votes: int
    candidates: tuple[CandidateResult, ...]


@dataclass(frozen=True)
class TableResult:
    corporation: str
    scope_code: str
    department_code: str
    census: int
    voters: int
    null_votes: int
    unmarked_votes: int
    blank_votes: int
    valid_votes: int
    parties: tuple[PartyResult, ...]

    @property
    def party_rows(self) -> int:
        return len(self.parties)

    @property
    def candidate_rows(self) -> int:
        return sum(len(party.candidates) for party in self.parties)


def _mapping(value: Any, field: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ActParseError(f"{field} debe ser un objeto")
    return value


def _sequence(value: Any, field: str) -> Sequence[Any]:
    if not isinstance(value, list):
        raise ActParseError(f"{field} debe ser una lista")
    return value


def _nonnegative_int(value: Any, field: str) -> int:
    if isinstance(value, bool):
        raise ActParseError(f"{field} no es un entero válido")
    try:
        parsed = int(str(value))
    except (TypeError, ValueError) as error:
        raise ActParseError(f"{field} no es un entero válido: {value!r}") from error
    if parsed < 0:
        raise ActParseError(f"{field} no puede ser negativo")
    return parsed


def _candidate_name(record: Mapping[str, Any]) -> str:
    parts = [record.get(field, "") for field in ("nomcan", "nomcan2", "apecan", "apecan2")]
    return " ".join(str(part).strip() for part in parts if str(part).strip())


def parse_table_result(
    payload: Mapping[str, Any],
    corporation: str,
    *,
    expected_scope_code: str | None = None,
) -> TableResult:
    corporation = corporation.upper()
    if corporation not in ELECTION_NUMBER:
        raise ActParseError(f"corporación no soportada: {corporation}")
    if str(payload.get("elec")) != ELECTION_NUMBER[corporation]:
        raise ActParseError(
            f"elección inesperada: {payload.get('elec')!r}; "
            f"se esperaba {ELECTION_NUMBER[corporation]}"
        )
    scope_code = str(payload.get("amb", ""))
    if len(scope_code) != 19 or not scope_code.isalnum():
        raise ActParseError(f"la respuesta no corresponde a una mesa: amb={scope_code!r}")
    if expected_scope_code is not None and scope_code != expected_scope_code:
        raise ActParseError(f"ámbito inesperado: {scope_code}; se esperaba {expected_scope_code}")

    totals = _mapping(_mapping(payload.get("totales"), "totales").get("act"), "totales.act")
    cameras = _sequence(payload.get("camaras"), "camaras")
    chamber = next(
        (
            _mapping(candidate, "camaras[]")
            for candidate in cameras
            if str(_mapping(candidate, "camaras[]").get("cam")) == DEFAULT_CHAMBER[corporation]
        ),
        None,
    )
    if chamber is None:
        raise ActParseError(f"no existe cámara {DEFAULT_CHAMBER[corporation]} para {corporation}")

    parties: list[PartyResult] = []
    seen_parties: set[int] = set()
    for raw_party in _sequence(chamber.get("partotabla"), "partotabla"):
        party = _mapping(_mapping(raw_party, "partotabla[]").get("act"), "partotabla[].act")
        code = _nonnegative_int(party.get("codpar"), "codpar")
        if code in seen_parties:
            raise ActParseError(f"partido duplicado en mesa: {code}")
        seen_parties.add(code)
        votes = _nonnegative_int(party.get("vot"), f"partido[{code}].vot")
        candidates: list[CandidateResult] = []
        seen_candidates: set[str] = set()
        for raw_candidate in _sequence(party.get("cantotabla"), f"partido[{code}].cantotabla"):
            candidate = _mapping(raw_candidate, "cantotabla[]")
            candidate_code = str(candidate.get("codcan", "")).strip()
            if not candidate_code or candidate_code in seen_candidates:
                raise ActParseError(
                    f"codcan vacío o duplicado en partido {code}: {candidate_code!r}"
                )
            seen_candidates.add(candidate_code)
            source_name = _candidate_name(candidate)
            if not source_name:
                raise ActParseError(f"candidato sin nombre en partido {code}: {candidate_code}")
            normalized_name = normalize_name(source_name)
            candidates.append(
                CandidateResult(
                    code=candidate_code,
                    source_name=source_name,
                    normalized_name=normalized_name,
                    votes=_nonnegative_int(
                        candidate.get("vot"), f"candidato[{candidate_code}].vot"
                    ),
                    is_list=candidate_code == "0" or normalized_name == "SOLO POR LA LISTA",
                )
            )
        candidate_votes = sum(candidate.votes for candidate in candidates)
        if candidate_votes != votes:
            raise ActParseError(
                f"suma de candidatos inconsistente para partido {code}: "
                f"{candidate_votes} != {votes}"
            )
        parties.append(PartyResult(code=code, votes=votes, candidates=tuple(candidates)))

    chamber_totals = _mapping(
        _mapping(chamber.get("totales"), "camara.totales").get("act"),
        "camara.totales.act",
    )
    expected_candidate_votes = _nonnegative_int(chamber_totals.get("votcan"), "camara.votcan")
    party_votes = sum(party.votes for party in parties)
    if party_votes != expected_candidate_votes:
        raise ActParseError(
            f"suma de partidos inconsistente: {party_votes} != {expected_candidate_votes}"
        )

    census = _nonnegative_int(totals.get("centota"), "centota")
    voters = _nonnegative_int(chamber_totals.get("votant"), "camara.votant")
    null_votes = _nonnegative_int(chamber_totals.get("votnul"), "camara.votnul")
    unmarked_votes = _nonnegative_int(chamber_totals.get("votnma"), "camara.votnma")
    blank_votes = _nonnegative_int(chamber_totals.get("votbla"), "camara.votbla")
    valid_votes = _nonnegative_int(chamber_totals.get("votval"), "camara.votval")
    if valid_votes + null_votes + unmarked_votes != voters:
        raise ActParseError(
            "balance de votos inconsistente: "
            f"válidos({valid_votes}) + nulos({null_votes}) + no_marcados({unmarked_votes}) "
            f"!= votantes({voters})"
        )
    if party_votes + blank_votes != valid_votes:
        raise ActParseError(
            "votos de partido + blancos inconsistentes: "
            f"{party_votes} + {blank_votes} != {valid_votes}"
        )

    return TableResult(
        corporation=corporation,
        scope_code=scope_code,
        department_code=str(payload.get("dept", "")),
        census=census,
        voters=voters,
        null_votes=null_votes,
        unmarked_votes=unmarked_votes,
        blank_votes=blank_votes,
        valid_votes=valid_votes,
        parties=tuple(parties),
    )
