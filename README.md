# MESA — Prueba Técnica UTL Senado 2026

> Estado: desarrollo incremental local con gates DEV, QA, SEC y REVIEW.

## Candidato

- Nombre: Hosneydert Mesa
- Email: hosneydert92@gmail.com
- Repositorio público: https://github.com/HosneydertMesa/mesa_prueba_utl_2026
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
python scraper/scraper.py --preflight --municipios TUNJA PAIPA
python scraper/scraper.py
python db/etl.py
python dashboard/export_data.py
python viz/heatmap.py
python viz/scatter.py
python outputs/generar_manifest.py
python scripts/verify_delivery.py
```

Durante el incremento 1.2a, `--preflight` ya es funcional; la ejecución de descarga sin el flag se habilitará junto con la persistencia idempotente en 1.2b.

El schema normalizado, las claves de idempotencia y los índices están documentados en [docs/10-schema-sqlite.md](docs/10-schema-sqlite.md).


La secuencia y criterios de salida están en [docs/06-runbook-entrega.md](docs/06-runbook-entrega.md). Cada incremento debe pasar la metodología local [DEV → QA → SEC → REVIEW](docs/08-metodologia-sdlc.md) mediante `python scripts/quality_gate.py all`.


## API

- Portal: `https://resultadospreccongreso2026.registraduria.gov.co`.
- Nomenclator: `GET /json/nomenclator.json`.
- Resultados: `GET /json/ACT/{SE|CA}/{scope_code}.json`.
- Códigos: Tunja `0700001`, Paipa `0700181`, Sogamoso `0700277`, Duitama `0700079`.
- Mesa: código de puesto de 13 caracteres + número de mesa en 6 dígitos.
- Acceso público sin autenticación; se recomienda `Accept: application/json`, User-Agent identificable, timeout y backoff.
- Campos verificados: `elec`, `amb`, `dept`, `mdhm`, `metota`, `mesesc`, `centota`, `votant`, `codpar`, `codcan`, `nomcan`, `apecan`, `vot` y `pref`, entre otros.
- Contrato, evidencias, jerarquía y fallback: [docs/09-contrato-api-registraduria.md](docs/09-contrato-api-registraduria.md).

Si la API no responde durante la ejecución, se usarán los archivos oficiales de `sample_data/` y se documentará el intento, sin cambiar el modelo de dominio.


## Municipios en la BD

Objetivo obligatorio: Tunja, Paipa, Sogamoso y Duitama. La base aún no ha sido cargada.

## Hallazgos principales

Todavía no existen hallazgos de datos. La estrategia evita presentar correlaciones como causalidad y exige reportar cobertura, faltantes, duplicados, denominadores y sensibilidad por municipio. Véase [docs/04-estrategia-analitica-ml.md](docs/04-estrategia-analitica-ml.md).

## Bonus implementados

Ninguno todavía. Orden recomendado: `--preflight`, tres índices justificados, explicación CA vs atribución SE, dark mode, exportación CSV y municipios adicionales solo después de asegurar los 100 puntos base.
