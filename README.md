# APELLIDO — Prueba Técnica UTL Senado 2026

> Estado: planificación y estructura base. La solución funcional aún no está implementada.

## Candidato

- Nombre: `PENDIENTE`
- Email: `PENDIENTE`
- Repositorio público: `PENDIENTE`
- Plan maestro: [docs/00-plan-maestro.md](docs/00-plan-maestro.md)

## Instalación

Requisito previsto: Python 3.11 o 3.12.

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt -r requirements-dev.txt
```

Antes de desarrollar, incorporar en `sample_data/` los archivos provistos por la UTL y en `outputs/` el generador y el manifest de ejemplo originales. No se encontraron junto al PDF inicial.

## Pipeline de ejecución

Contrato objetivo, aún pendiente de implementación:

```bash
python scraper/scraper.py --preflight
python scraper/scraper.py
python db/etl.py
python dashboard/export_data.py
python viz/heatmap.py
python viz/scatter.py
python outputs/generar_manifest.py
python scripts/verify_delivery.py
```

La secuencia y criterios de salida están en [docs/06-runbook-entrega.md](docs/06-runbook-entrega.md). Cada incremento debe pasar la metodología local [DEV → QA → SEC → REVIEW](docs/08-metodologia-sdlc.md) mediante `python scripts/quality_gate.py all`.


## API

- Portal oficial: `https://resultadospreccongreso2026.registraduria.gov.co`.
- El patrón exacto de endpoints, nomenclator, cabeceras y campos JSON se descubrirá y congelará como contrato antes de implementar el scraper.
- Si el portal no responde, el parser se desarrollará contra `sample_data/` y se documentará el intento, como autoriza el enunciado.
- No se asumirán endpoints ni cabeceras sin evidencia de Network/F12 o muestras provistas.

## Municipios en la BD

Objetivo obligatorio: Tunja, Paipa, Sogamoso y Duitama. La base aún no ha sido cargada.

## Hallazgos principales

Todavía no existen hallazgos de datos. La estrategia evita presentar correlaciones como causalidad y exige reportar cobertura, faltantes, duplicados, denominadores y sensibilidad por municipio. Véase [docs/04-estrategia-analitica-ml.md](docs/04-estrategia-analitica-ml.md).

## Bonus implementados

Ninguno todavía. Orden recomendado: `--preflight`, tres índices justificados, explicación CA vs atribución SE, dark mode, exportación CSV y municipios adicionales solo después de asegurar los 100 puntos base.
