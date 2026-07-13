"""Puertas locales DEV, QA, SEC, REVIEW y RELEASE sin dependencias externas."""

from __future__ import annotations

import argparse
import compileall
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {".py", ".md", ".yml", ".yaml", ".json", ".toml", ".txt", ".sql", ".html"}
TEXT_NAMES = {".gitignore", ".editorconfig"}
IGNORED_PARTS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".cache",
    "tmp",
}

REQUIRED_BASE = (
    "README.md",
    "requirements.txt",
    "scraper/scraper.py",
    "scraper/nomenclator.py",
    "scraper/http_client.py",
    "scraper/act_parser.py",
    "db/schema.sql",
    "db/database.py",
    "db/etl.py",
    "scripts/audit_database.py",
    "sql/tarea_3_1.sql",
    "sql/tarea_3_2.sql",
    "sql/tarea_3_3.sql",
    "dashboard/export_data.py",
    "dashboard/data.json",
    "dashboard/index.html",
    "viz/heatmap.py",
    "viz/scatter.py",
    "outputs/generar_manifest.py",
    "outputs/evaluation_manifest.example.json",
    "scripts/export_sample_data.py",
    "sample_data/candidate_captured/provenance.json",
    "sample_data/candidate_captured/nomenclator_boyaca_sample.json",
    "sample_data/candidate_captured/act_ca_tunja_mesa_001.json",
    "sample_data/candidate_captured/act_se_tunja_mesa_001.json",
)

REQUIRED_H2 = [
    "## Candidato",
    "## Instalación",
    "## Pipeline de ejecución",
    "## API",
    "## Municipios en la BD",
    "## Hallazgos principales",
    "## Bonus implementados",
]

SECRET_PATTERNS = {
    "GitHub token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b"),
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
}


class GateFailure(RuntimeError):
    """Una puerta de calidad no fue satisfecha."""


def text_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(part in IGNORED_PARTS for part in path.parts):
            continue
        if path.suffix.lower() in TEXT_SUFFIXES or path.name in TEXT_NAMES:
            files.append(path)
    return files


def find_secrets(content: str) -> list[str]:
    return [name for name, pattern in SECRET_PATTERNS.items() if pattern.search(content)]


def markdown_headings(content: str) -> list[str]:
    headings: list[str] = []
    in_fence = False
    for line in content.splitlines():
        if line.strip().startswith("```"):
            in_fence = not in_fence
        elif not in_fence and line.startswith("#"):
            headings.append(line.strip())
    return headings


def gate_dev() -> None:
    missing = [item for item in REQUIRED_BASE if not (ROOT / item).exists()]
    if missing:
        raise GateFailure("rutas faltantes: " + ", ".join(missing))
    targets = [ROOT / name for name in ("scraper", "db", "dashboard", "viz", "scripts")]
    if not all(compileall.compile_dir(str(path), quiet=1) for path in targets):
        raise GateFailure("falló la compilación de Python")


def gate_qa() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py", "-v"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    output = (result.stdout + result.stderr).strip()
    if result.returncode != 0:
        raise GateFailure("pruebas fallidas:\n" + output)
    if "Ran 0 tests" in output:
        raise GateFailure("no se descubrieron pruebas")


def gate_sec() -> None:
    findings: list[str] = []
    for path in text_files():
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for secret_type in find_secrets(content):
            findings.append(f"{path.relative_to(ROOT)}: {secret_type}")
    if findings:
        raise GateFailure("posibles secretos detectados:\n- " + "\n- ".join(findings))


def gate_review() -> None:
    headings = markdown_headings((ROOT / "README.md").read_text(encoding="utf-8"))
    if not headings or not re.fullmatch(r"# .+ — Prueba Técnica UTL Senado 2026", headings[0]):
        raise GateFailure("título contractual del README inválido")
    if headings[1:] != REQUIRED_H2:
        raise GateFailure("headings H2 del README no coinciden exactamente con el contrato")
    pdfs = [
        path.relative_to(ROOT)
        for path in ROOT.rglob("*.pdf")
        if not any(part in IGNORED_PARTS for part in path.relative_to(ROOT).parts)
    ]
    if pdfs:
        raise GateFailure("PDF dentro del repo público: " + ", ".join(map(str, pdfs)))


def validate_release_manifest(manifest: object) -> list[str]:
    if not isinstance(manifest, dict):
        return ["la raíz debe ser un objeto JSON"]
    failures: list[str] = []
    if manifest.get("generator_provenance") != "candidate_implemented_from_pdf_contract":
        failures.append("procedencia del generador inválida")
    if manifest.get("overall_status") != "OK":
        failures.append("overall_status no es OK")
    meta = manifest.get("meta", {})
    if not isinstance(meta, dict) or any(
        not str(meta.get(key, "")).strip() for key in ("nombre", "email", "repositorio")
    ):
        failures.append("META incompleta")
    scope = manifest.get("scope", {})
    if not isinstance(scope, dict) or (
        scope.get("municipalities_loaded"), scope.get("municipalities_expected")
    ) != (4, 4):
        failures.append("cobertura del manifest distinta de 4/4")
    sql_tasks = manifest.get("sql_tasks", {})
    if not isinstance(sql_tasks, dict) or set(sql_tasks) != {"3.1", "3.2", "3.3"}:
        failures.append("tareas SQL incompletas")
    elif any(
        not isinstance(task, dict) or task.get("status") != "OK"
        for task in sql_tasks.values()
    ):
        failures.append("alguna tarea SQL no está OK")
    sample_data = manifest.get("sample_data", {})
    if not isinstance(sample_data, dict) or sample_data.get("status") != "OK":
        failures.append("sample_data no está verificado")
    scatter = manifest.get("scatter_statistics", {})
    if not isinstance(scatter, dict) or not re.fullmatch(
        r"r=-?\d+\.\d{3} \| pendiente=-?\d+\.\d{3} \| n_mesas=\d+",
        str(scatter.get("stdout", "")),
    ):
        failures.append("stdout del scatter inválido")
    return failures


def gate_release() -> None:
    required_release = (
        "db/puestos_2026.db",
        "outputs/generar_manifest.py",
        "outputs/evaluation_manifest.json",
        "outputs/evaluation_manifest.example.json",
        "sample_data/candidate_captured/provenance.json",
        "sample_data/candidate_captured/nomenclator_boyaca_sample.json",
        "sample_data/candidate_captured/act_ca_tunja_mesa_001.json",
        "sample_data/candidate_captured/act_se_tunja_mesa_001.json",
        "viz/heatmap_municipios.png",
        "viz/scatter_ca_se.png",
    )
    missing = [item for item in required_release if not (ROOT / item).exists()]
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    if "PENDIENTE" in readme or "APELLIDO" in readme:
        missing.append("metadata real del candidato en README")
    if missing:
        raise GateFailure("entrega aún incompleta:\n- " + "\n- ".join(missing))
    manifest_path = ROOT / "outputs/evaluation_manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise GateFailure(f"evaluation_manifest.json inválido: {error}") from error
    failures = validate_release_manifest(manifest)
    if failures:
        raise GateFailure("manifest no conforme:\n- " + "\n- ".join(failures))


GATES = {"dev": gate_dev, "qa": gate_qa, "sec": gate_sec, "review": gate_review}


def run(name: str) -> int:
    selected = list(GATES) if name in {"all", "release"} else [name]
    try:
        for gate_name in selected:
            GATES[gate_name]()
            print(f"[PASS] {gate_name.upper()}")
        if name == "release":
            gate_name = "release"
            gate_release()
            print("[PASS] RELEASE")
    except GateFailure as exc:
        print(f"[FAIL] {gate_name.upper() if 'gate_name' in locals() else name.upper()}: {exc}")
        return 1
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("gate", choices=[*GATES, "all", "release"])
    args = parser.parse_args()
    raise SystemExit(run(args.gate))


if __name__ == "__main__":
    main()
