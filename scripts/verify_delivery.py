"""Comprueba el contrato estructural sin afirmar funcionalidad."""

from pathlib import Path

REQUIRED = (
    "README.md", "requirements.txt", "sample_data", "scraper/scraper.py",
    "db/schema.sql", "db/etl.py", "sql/tarea_3_1.sql", "sql/tarea_3_2.sql",
    "sql/tarea_3_3.sql", "dashboard/export_data.py", "dashboard/data.json",
    "dashboard/index.html", "viz/heatmap.py", "viz/scatter.py",
    "sample_data/candidate_captured/provenance.json",
    "sample_data/candidate_captured/nomenclator_boyaca_sample.json",
    "sample_data/candidate_captured/act_ca_tunja_mesa_001.json",
    "sample_data/candidate_captured/act_se_tunja_mesa_001.json",
    "outputs/generar_manifest.py", "outputs/evaluation_manifest.json",
    "outputs/evaluation_manifest.example.json",
)


def main() -> None:
    missing = [item for item in REQUIRED if not Path(item).exists()]
    if missing:
        raise SystemExit("Faltan rutas obligatorias:\n- " + "\n- ".join(missing))
    print(f"Estructura base OK: {len(REQUIRED)}/{len(REQUIRED)} rutas presentes")
    print("AVISO: la conformidad funcional final se verifica con quality_gate.py release")


if __name__ == "__main__":
    main()
