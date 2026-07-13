# Arquitectura propuesta

## Flujo

```text
API Registraduría o sample_data
  -> scraper (adquisición y validación de forma)
  -> ETL normalizador -> SQLite
  -> SQL 3.x + export_data.py + viz/*.py
  -> manifest y dashboard/index.html
```

## Responsabilidades

- `scraper/`: red, nomenclator, retry/backoff, municipios y parsing; sin reglas analíticas.
- `db/`: schema, normalización, transacciones, deduplicación y auditoría.
- `sql/`: consultas puras e independientes de Python.
- `dashboard/`: contrato de exportación y presentación estática.
- `viz/`: productos reproducibles derivados de SQLite.
- `outputs/`: evaluador provisto y resultado; no duplicar su lógica.
- `tests/`: unitarias, integración y contratos.

## Modelo lógico mínimo a confirmar

- `municipios(id, codigo, nombre)`
- `puestos(id, municipio_id, codigo, nombre)`
- `mesas(id, puesto_id, numero)`
- `partidos(id, corporacion, codpar, nombre)`
- `candidatos(id, partido_id, codigo, nombre_normalizado, nombre_fuente)`
- `resultados(id, mesa_id, candidato_id, corporacion, votos, fuente_hash)`
- `carga_log(id, inicio, fin, fuente, estado, leidas, insertadas, omitidas, error)`

Las claves naturales finales se definen al observar el JSON. `codpar` no debe asumirse global: el enunciado muestra homologaciones distintas entre CA y SE.

## Decisiones técnicas

- Python 3.11/3.12 y SQLite por compatibilidad.
- `requests.Session` + retry/backoff; timeouts explícitos y jitter.
- Transacción por unidad de carga, nunca `commit` por fila.
- `INSERT OR IGNORE` respaldado por `UNIQUE`; no ocultar errores de FK.
- JSON agregado y pequeño para el dashboard.
- Orden explícito en SQL para resultados repetibles.

Cada etapa registrará municipio, corporación, fuente, leídas, insertadas, omitidas, duración y resultado, sin secretos ni payloads completos.
