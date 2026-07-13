# Arquitectura del pipeline

## Estado

Las capas de adquisición, parsing, ETL, SQLite, auditoría, SQL, exportación JSON
y presentación HTML están implementadas. Heatmap 5.1 y scatter 5.2 completan el
camino funcional base; la preparación de entrega es el siguiente bloque.

## Flujo actual y planificado

```text
Nomenclator + ACT públicos
  -> JsonHttpClient (timeout, retry/backoff, caché atómica)
  -> parser ACT (contrato, ámbito, cámara y balances)
  -> ETL transaccional e idempotente
  -> SQLite normalizado + carga_log
  -> SQL 3.1 / 3.2 / 3.3
  -> auditoría local reproducible
  -> export_data.py -> data.json + JSON embebido
  -> dashboard/index.html autocontenido + analítica interactiva
  -> heatmap.py -> heatmap_municipios.png
  -> scatter.py -> scatter_ca_se.png + stdout contractual
  -> [bloqueado] generar_manifest.py oficial
```

## Responsabilidades

- `scraper/http_client.py`: transporte estándar `urllib`, caché, timeout,
  Retry-After y reintento de HTTP/JSON transitorio.
- `scraper/nomenclator.py`: jerarquía electoral, municipios, puestos, mesas,
  URLs ACT y catálogo de partidos.
- `scraper/act_parser.py`: modelos tipados e invariantes por cámara/mesa.
- `scraper/scraper.py`: CLI, filtros, preflight, recorrido y progreso.
- `db/schema.sql`: restricciones, claves naturales e índices.
- `db/etl.py`: dimensiones, hechos, transacciones, idempotencia y auditoría.
- `scripts/audit_database.py`: cobertura, integridad, calidad y ejecución SQL.
- `sql/`: consultas puras, deterministas e independientes de Python.
- `dashboard/export_data.py`: contrato determinista SQLite→JSON, validaciones y
  sincronización atómica del bloque embebido en el HTML.
- `dashboard/index.html`: presentación estática autocontenida compatible con
  apertura directa, sin runtime ni recursos externos; administra el tema local
  y construye la exportación CSV, heatmap semántico y scatter Canvas en memoria.
- `viz/heatmap.py`: selección top 8 consolidada, matriz porcentual y PNG.
- `viz/scatter.py`: pareo CA/SE por mesa, Pearson, OLS, PNG y stdout contractual.
- `outputs/`: auditoría local; evaluador oficial cuando sea suministrado.
- `tests/`: unitarias e integración de contratos y casos calculables.

## Modelo lógico implementado

```text
municipios 1---N puestos 1---N mesas

partidos 1---N candidatos

mesas 1---N resumen_mesa
mesas 1---N resultados_partido N---1 partidos
mesas 1---N resultados_candidato N---1 candidatos

carga_log 1---N resumen_mesa/resultados_*
```

Tablas implementadas:

- `municipios(id, codigo, nombre, departamento_codigo)`
- `puestos(id, municipio_id, codigo, nombre, mesas_esperadas)`
- `mesas(id, puesto_id, numero, codigo)`
- `partidos(id, corporacion, codpar, nombre)`
- `candidatos(id, partido_id, codcan, nombre_fuente, nombre_normalizado, es_lista)`
- `resumen_mesa(..., corporacion, censo, votantes, votos_*)`
- `resultados_partido(mesa_id, partido_id, carga_id, votos)`
- `resultados_candidato(mesa_id, candidato_id, carga_id, votos)`
- `carga_log(..., estado, fuente_sha256, filas_leidas, insertadas, omitidas)`

`codpar` no es global: la clave de partido incluye corporación y la relación CA→SE
se expresa sólo en las consultas que la necesitan.

## Decisiones técnicas vigentes

- Python 3.11/3.12 y librería estándar para el pipeline base.
- SQLite con `foreign_keys=ON`, WAL y transacción por respuesta ACT.
- `INSERT OR IGNORE` únicamente sobre claves `UNIQUE`, seguido de comparación.
- Conflictos de una clave con valores diferentes hacen rollback y dejan evidencia.
- Datos fuente y nombres normalizados se conservan por separado.
- Orden explícito y `NULLIF` en SQL para resultados repetibles y cero seguro.
- La base de 64 MB no se versiona; la entrega prevista es GitHub Release asset.
- La ampliación bonus usa `db/puestos_2026_bonus.db`; separar bases impide que los
  tres municipios adicionales alteren los resultados contractuales de cuatro.
- El dashboard incorpora los datos como JSON embebido para ser compatible con
  `file://` sin servidor ni solicitudes bloqueadas por CORS.
- El dashboard ampliado consume siete municipios con `alcance` explícito. El
  bloque `analitica` conserva en la raíz las 1.107 mesas obligatorias y agrega
  `ampliada` con las 1.432 mesas, su heatmap y su regresión independientes.
- El tema se resuelve con CSS custom properties y una preferencia local; el CSV
  se genera con `Blob` desde el mismo JSON embebido. Ninguna función requiere red.
- El schema v2 reutiliza `load_heatmap_data`, `load_scatter_data` y
  `fit_regression`; así los PNG y las vistas interactivas comparten fórmulas.
- La capa de presentación 3.0 conserva un único documento, pero organiza sus
  secciones como cuatro paneles accesibles controlados por fragmento de URL.
- GitHub Pages recibe un artefacto mínimo con `index.html` y `data.json`; el
  pipeline, SQLite y evidencias internas permanecen fuera del sitio público.

## Límites deliberados

- No se persiste `cedula` porque no es necesaria para los retos.
- No se imputa `censo` cuando la fuente publica `votantes > censo`.
- La atribución SE es determinística y descriptiva, no causal.
- ML queda fuera del camino crítico hasta cerrar manifest, revisión manual
  Firefox/`file://` y congelamiento final de entrega.
