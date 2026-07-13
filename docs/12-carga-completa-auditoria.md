# Carga completa y auditoría local - Retos 1.3 y 2.3

## Alcance ejecutado

El 12 de julio de 2026 se recorrieron las cuatro ciudades obligatorias contra el
portal público de la Registraduría. La ejecución procesó 1.107 mesas y dos
corporaciones por mesa, para 2.214 respuestas ACT.

| Municipio | Puestos | Mesas | CA | SE |
|---|---:|---:|---:|---:|
| Tunja | 26 | 424 | 424 | 424 |
| Paipa | 7 | 95 | 95 | 95 |
| Sogamoso | 18 | 301 | 301 | 301 |
| Duitama | 22 | 287 | 287 | 287 |
| **Total** | **73** | **1.107** | **1.107** | **1.107** |

## Idempotencia a escala completa

La segunda corrida utilizó la caché HTTP y terminó en 43,9 segundos:

```text
SCRAPER mesas=1107 cargas=2214 leidas=1277478 insertadas=0 omitidas=1277478
```

La base conserva una fila de `carga_log` por intento completado. Por eso el total
de logs puede ser superior a 2.214 después de reanudaciones y pruebas de
idempotencia, mientras las tablas de hechos permanecen protegidas por sus claves
`UNIQUE`.

## Conteos e integridad

- `PRAGMA integrity_check`: `ok`.
- `PRAGMA foreign_key_check`: cero violaciones.
- `resumen_mesa`: 2.214 filas.
- `resultados_partido`: 27.675 filas.
- `resultados_candidato`: 1.247.589 filas.
- Balances de votos, partidos y candidatos inválidos: cero.
- Mesas sin las dos corporaciones: cero.

## Calidad de fuente

Existen 53 registros de corporación con `votantes > censo`. Los valores aparecen
así en las respuestas ACT oficiales. El pipeline conserva ambos campos y la
auditoría los reporta; no imputa un censo nuevo ni elimina esas mesas. Esta
anomalía no rompe los balances de votos dentro de la corporación.

Durante la descarga el portal también entregó ocasionalmente cuerpo no JSON con
estado HTTP 200. El cliente ahora trata ese caso como transitorio, aplica el mismo
backoff acotado y sólo escribe caché después de decodificar JSON válido.

## Auditoría reproducible

```bash
python scripts/audit_database.py
```

El comando genera `outputs/auditoria_local.json`, devuelve código distinto de
cero si falla un control bloqueante y etiqueta la salida como
`local_non_official`. No sustituye `generar_manifest.py` ni el manifest oficial,
que no fueron entregados junto al PDF disponible.

La carga ampliada de siete municipios se conserva separada y está documentada
en `docs/19-bonus-municipios-boyaca.md`; no modifica estos conteos base.
