"""Exporta muestras reales y mínimas desde la caché HTTP del scraper.

Los archivos resultantes no se presentan como insumos suministrados por la UTL:
son capturas del candidato obtenidas de la API pública y serializadas de forma
determinista para desarrollar y verificar el parser sin depender de la red.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scraper.nomenclator import DEFAULT_BASE_URL, normalize_name  # noqa: E402

SCOPE_CODE = "0700001010001000001"
REQUIRED_MUNICIPALITIES = ("TUNJA", "PAIPA", "SOGAMOSO", "DUITAMA")
NOMENCLATOR_URL = f"{DEFAULT_BASE_URL}/json/nomenclator.json"
ACT_URLS = {
    "act_ca_tunja_mesa_001.json": f"{DEFAULT_BASE_URL}/json/ACT/CA/{SCOPE_CODE}.json",
    "act_se_tunja_mesa_001.json": f"{DEFAULT_BASE_URL}/json/ACT/SE/{SCOPE_CODE}.json",
}


class SampleExportError(RuntimeError):
    """La caché no contiene una captura válida para construir las muestras."""


def _cache_path(cache_dir: Path, url: str) -> Path:
    return cache_dir / f"{hashlib.sha256(url.encode('utf-8')).hexdigest()}.json"


def _read_capture(cache_dir: Path, url: str) -> dict[str, Any]:
    path = _cache_path(cache_dir, url)
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise SampleExportError(f"captura ausente o inválida: {path}") from error
    if record.get("url") != url or not isinstance(record.get("payload"), dict):
        raise SampleExportError(f"contrato de caché inválido para {url}")
    return record


def _relation_ids(record: Mapping[str, Any], key: str) -> list[int]:
    return [
        int(item)
        for relation in record.get(key, [])
        for item in relation.get("p", [])
    ]


def _filter_relations(record: dict[str, Any], selected_ids: set[int]) -> None:
    for key in ("p", "h"):
        filtered = []
        for relation in record.get(key, []):
            ids = [int(item) for item in relation.get("p", []) if int(item) in selected_ids]
            if ids:
                relation_copy = copy.deepcopy(relation)
                relation_copy["p"] = ids
                filtered.append(relation_copy)
        if key in record:
            record[key] = filtered


def _scope_subset(records: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    by_id = {int(record["i"]): record for record in records}
    departments = {
        int(record["i"])
        for record in records
        if int(record.get("l", 0)) == 2 and str(record.get("c", "")) == "0700"
    }
    if len(departments) != 1:
        raise SampleExportError("no se encontró un único ámbito departamental 0700")
    department_id = next(iter(departments))
    selected_ids = {department_id}
    municipality_ids: list[int] = []
    for record in records:
        if int(record.get("l", 0)) != 3:
            continue
        if normalize_name(str(record.get("n", ""))) not in REQUIRED_MUNICIPALITIES:
            continue
        if department_id not in _relation_ids(record, "p"):
            continue
        municipality_ids.append(int(record["i"]))
    if len(municipality_ids) != len(REQUIRED_MUNICIPALITIES):
        raise SampleExportError(
            "cobertura municipal incompleta en nomenclator: "
            f"{len(municipality_ids)}/{len(REQUIRED_MUNICIPALITIES)}"
        )
    pending = list(municipality_ids)
    while pending:
        record_id = pending.pop()
        if record_id in selected_ids:
            continue
        selected_ids.add(record_id)
        record = by_id.get(record_id)
        if record is None:
            raise SampleExportError(f"ámbito hijo inexistente: {record_id}")
        pending.extend(_relation_ids(record, "h"))

    subset: list[dict[str, Any]] = []
    for record in records:
        if int(record["i"]) not in selected_ids:
            continue
        item = copy.deepcopy(dict(record))
        _filter_relations(item, selected_ids)
        subset.append(item)
    return subset


def _party_codes(payload: Mapping[str, Any]) -> set[int]:
    return {
        int(party["act"]["codpar"])
        for camera in payload.get("camaras", [])
        for party in camera.get("partotabla", [])
    }


def _minimize_act_payload(value: Any) -> Any:
    """Elimina identificadores publicados que el parser y los retos no requieren."""

    if isinstance(value, dict):
        return {
            key: _minimize_act_payload(item)
            for key, item in value.items()
            if key != "cedula"
        }
    if isinstance(value, list):
        return [_minimize_act_payload(item) for item in value]
    return copy.deepcopy(value)


def build_nomenclator_sample(
    nomenclator: Mapping[str, Any], act_payloads: Sequence[Mapping[str, Any]]
) -> dict[str, Any]:
    scopes = nomenclator.get("amb")
    if not isinstance(scopes, list):
        raise SampleExportError("nomenclator sin bloques de ámbitos")
    parties_needed = set().union(*(_party_codes(payload) for payload in act_payloads))
    result = {
        key: copy.deepcopy(nomenclator[key])
        for key in ("ver", "y", "elec", "levels")
        if key in nomenclator
    }
    result["amb"] = [
        {**copy.deepcopy(dict(block)), "ambitos": _scope_subset(block["ambitos"])}
        for block in scopes
        if int(block.get("elec", -1)) in {1, 2}
    ]
    result["partidos"] = [
        copy.deepcopy(item)
        for item in nomenclator.get("partidos", [])
        if int(item.get("i", -1)) in parties_needed
    ]
    available = {int(item["i"]) for item in result["partidos"]}
    if available != parties_needed:
        raise SampleExportError(
            f"catálogo de partidos incompleto: faltan {sorted(parties_needed - available)}"
        )
    return result


def _write_json(
    path: Path, payload: Mapping[str, Any], *, pretty: bool = True
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    formatting = {"indent": 2} if pretty else {"separators": (",", ":")}
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, **formatting) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def export_samples(cache_dir: Path, output_dir: Path) -> dict[str, Any]:
    nomenclator_capture = _read_capture(cache_dir, NOMENCLATOR_URL)
    act_captures = {
        filename: _read_capture(cache_dir, url) for filename, url in ACT_URLS.items()
    }
    act_payloads = [record["payload"] for record in act_captures.values()]
    outputs: dict[str, Path] = {}
    for filename, record in act_captures.items():
        path = output_dir / filename
        _write_json(path, _minimize_act_payload(record["payload"]), pretty=False)
        outputs[filename] = path
    nomenclator_path = output_dir / "nomenclator_boyaca_sample.json"
    _write_json(
        nomenclator_path,
        build_nomenclator_sample(nomenclator_capture["payload"], act_payloads),
        pretty=False,
    )
    outputs[nomenclator_path.name] = nomenclator_path

    sources = {
        "nomenclator_boyaca_sample.json": {
            "url": NOMENCLATOR_URL,
            "etag": nomenclator_capture.get("etag"),
            "fetched_at": nomenclator_capture.get("fetched_at"),
            "transformation": "subconjunto Boyacá para los cuatro municipios obligatorios",
        },
        **{
            filename: {
                "url": ACT_URLS[filename],
                "etag": record.get("etag"),
                "fetched_at": record.get("fetched_at"),
                "transformation": (
                    "payload extraído de la envoltura de caché, sin el campo cedula "
                    "por minimización, y reserializado"
                ),
            }
            for filename, record in act_captures.items()
        },
    }
    provenance = {
        "schema_version": 1,
        "provenance": "candidate_captured_from_public_api_cache",
        "official_utl_sample": False,
        "source_base_url": DEFAULT_BASE_URL,
        "scope": {
            "municipalities_in_nomenclator": list(REQUIRED_MUNICIPALITIES),
            "act_sample_municipality": "TUNJA",
            "act_sample_table": SCOPE_CODE,
            "corporations": ["CA", "SE"],
        },
        "serialization": "UTF-8 JSON compacto, claves ordenadas; bytes HTTP originales no disponibles",
        "files": {
            name: {
                **sources[name],
                "bytes": path.stat().st_size,
                "sha256": _sha256(path),
            }
            for name, path in sorted(outputs.items())
        },
    }
    _write_json(output_dir / "provenance.json", provenance)
    return provenance


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache-dir", type=Path, default=Path(".cache/http"))
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("sample_data/candidate_captured"),
    )
    args = parser.parse_args(argv)
    provenance = export_samples(args.cache_dir, args.output_dir)
    print(
        "SAMPLE_DATA OK | "
        f"archivos={len(provenance['files'])} | "
        f"salida={args.output_dir} | procedencia={provenance['provenance']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
