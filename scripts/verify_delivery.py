"""Comprueba el contrato estructural sin afirmar funcionalidad."""

from pathlib import Path

REQUIRED = (
    "README.md", "requirements.txt", "sample_data", "scraper/scraper.py",
    "db/schema.sql", "db/etl.py", "sql/tarea_3_1.sql", "sql/tarea_3_2.sql",
    "sql/tarea_3_3.sql", "dashboard/export_data.py", "dashboard/data.json",
    "dashboard/index.html", "viz/heatmap.py", "viz/scatter.py",
)


def main() -> None:
    missing = [item for item in REQUIRED if not Path(item).exists()]
    if missing:
        raise SystemExit("Faltan rutas obligatorias:\n- " + "\n- ".join(missing))
    print(f"Estructura base OK: {len(REQUIRED)}/{len(REQUIRED)} rutas presentes")
    print("AVISO: no sustituye el manifest oficial ni pruebas funcionales")


if __name__ == "__main__":
    main()

