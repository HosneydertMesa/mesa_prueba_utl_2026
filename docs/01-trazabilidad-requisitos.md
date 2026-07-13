# Matriz de trazabilidad y puntaje

| ID | Pts | Artefacto | Verificación prevista | Prioridad |
|---|---:|---|---|---|
| 1.1 API | 8 | README `## API` y contrato | 8+ campos, URL, nomenclator y headers con evidencia | P0 |
| 1.2 Scraper | 12 | `scraper/scraper.py` | defaults, filtro, retry, progreso, segunda corrida | P0 |
| 1.3 Validación | 5 | manifest oficial | mesas y filas por municipio | P0 |
| 2.1 Schema | 10 | `db/schema.sql` | UNIQUE, NOT NULL, FK, carga_log, foreign_key_check | P0 |
| 2.2 ETL | 10 | `db/etl.py` | normalización, deduplicación, insertadas/omitidas | P0 |
| 2.3 Verificación | 5 | manifest oficial | filas por tabla y líder SE | P0 |
| 3.1 Arrastre | 9 | `sql/tarea_3_1.sql` | CA=5, SE=57, puesto+municipio, cero seguro | P0 |
| 3.2 Dominancia | 8 | `sql/tarea_3_2.sql` | candidato/partido >0.60 por mesa | P0 |
| 3.3 Atribución | 8 | `sql/tarea_3_3.sql` | fórmula exacta y top 5 consolidado | P0 |
| 4 Dashboard | 15 | `dashboard/index.html` | 4 municipios, selectores, referencia 1.0, colores | P0 |
| 5.1 Heatmap | 5 | script + PNG | 8x4, porcentajes y anotaciones | P0 |
| 5.2 Scatter | 5 | script + PNG | mesa, municipio, OLS, Pearson, stdout exacto | P0 |
| B1 Preflight | +3 | scraper | no persiste ni descarga payload completo | P2 |
| B2 Índices | +2 | schema + justificación | 3+ índices y `EXPLAIN QUERY PLAN` | P2 |
| B3 Explicación | +2 | README | CA directo vs reparto proporcional SE | P2 |
| B4 Dark mode | +3 | dashboard | variables CSS | P2 |
| B5 CSV | +2 | dashboard | exporta selección con encabezados | P2 |
| B6 Municipios | +3 | configuración | adicionales sin alterar alcance base | P3 |

## Penalizaciones convertidas en controles

| Riesgo | Descuento | Control preventivo |
|---|---:|---|
| Duplicados | -5 | UNIQUE + transacción + doble ejecución |
| Menos de 3 municipios | -10 | puerta estricta 4/4 |
| Dashboard incompleto | -5 | prueba contractual por municipio |
| README no reproducible | -10 | ensayo desde clon limpio |
| Archivo ausente | -2 c/u | verificador estructural y CI |

## Estado de incrementos

- Reto 1.1 API: implementado y verificado contra el portal oficial; contrato en `docs/09-contrato-api-registraduria.md` y resolución en `scraper/nomenclator.py`.
- Reto 1.2a preflight/HTTP: implementado; 4/4 municipios, 73 puestos, 1.107 mesas y 2.214 solicitudes ACT estimadas sin descargar resultados.
- Reto 1.2b descarga, parsing y persistencia idempotente: implementado; corrida completa y segunda ejecución con cero inserciones verificadas.
- Reto 1.3 validación: auditoría local 4/4, 73 puestos, 1.107 mesas y 2.214 resultados aprobada; manifest oficial pendiente de recibir.
- Reto 2.1 schema SQLite: implementado con FK, NOT NULL, CHECK, carga_log, claves UNIQUE y cinco índices justificados.
- Reto 2.2 ETL: implementado con normalización, catálogo de partidos, transacciones y filas insertadas/omitidas.
- Reto 2.3 verificación: conteos, balances, integridad, anomalías de fuente y líderes SE incluidos en `outputs/auditoria_local.json`; manifest oficial pendiente.
- Reto 3.1 arrastre: implementado con homologación `5→57`, 73 puestos y denominador cero como `NULL`.
- Reto 3.2 dominancia: implementado para CA/SE, candidatos individuales y umbral estricto `>0.60`.
- Reto 3.3 atribución: implementado con homologación ponderada, fórmula por mesa y top 5 consolidado.
- Retos 4 y 5: pendientes.

