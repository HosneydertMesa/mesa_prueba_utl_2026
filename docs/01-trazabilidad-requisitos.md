# Matriz de trazabilidad y puntaje

| ID | Pts | Estado | Artefacto/evidencia | Cierre pendiente |
|---|---:|---|---|---|
| 1.1 API | 8 | Implementado | README, contrato y nomenclator real | ninguno local |
| 1.2 Scraper | 12 | Implementado | retry, progreso y segunda corrida completa | ninguno local |
| 1.3 Validación | 5 | Validado local | 4/4 y 2.214 en auditoría | manifest oficial |
| 2.1 Schema | 10 | Implementado | FK, UNIQUE, NOT NULL, checks y cinco índices | ninguno local |
| 2.2 ETL | 10 | Implementado | normalización, transacciones y `carga_log` | ninguno local |
| 2.3 Verificación | 5 | Validado local | conteos, balances y líderes SE | manifest oficial |
| 3.1 Arrastre | 9 | Implementado | 73 puestos, `5→57`, cero seguro | manifest oficial |
| 3.2 Dominancia | 8 | Implementado | 3.780 filas, umbral estricto probado | manifest oficial |
| 3.3 Atribución | 8 | Implementado | fórmula exacta y top 5 | manifest oficial |
| 4 Dashboard | 15 | Implementado + v2 | HTML autocontenido, JSON v2, heatmap y scatter interactivos | revisión manual Chrome/Firefox |
| 5.1 Heatmap | 5 | Implementado | `viz/heatmap.py` + PNG 8×4 anotado | validación oficial |
| 5.2 Scatter | 5 | Implementado | `viz/scatter.py`, OLS/Pearson, PNG y stdout exacto | validación oficial |
| B1 Preflight | +3 | Implementado | 4/4 sin escribir BD ni ACT | validación oficial |
| B2 Índices | +2 | Implementado | cinco índices + `EXPLAIN QUERY PLAN` | validación oficial |
| B3 Explicación | +2 | Implementado | README y `docs/13-sql-analitico.md` | validación oficial |
| B4 Dark mode | +3 | Implementado | CSS custom properties, preferencia y persistencia local | validación oficial |
| B5 CSV | +2 | Implementado | exportación UTF-8 de la selección municipal visible | validación oficial |
| B6 Municipios | +3 | Implementado | 3 adicionales, auditoría 7/7 y segunda corrida en cero | validación oficial |

## Resumen cuantitativo

- Base implementada y verificada internamente: 100/100 puntos potenciales.
- Base pendiente de implementación: 0/100 puntos.
- Bonus implementado: +15/+15 puntos potenciales.
- Validación oficial pendiente: retos 1.3, 2.3 y 3.x por ausencia del generador.

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
- Reto 4.1 exportación: implementado con JSON determinista, cuatro municipios
  obligatorios y tres bonus identificados, top 10 CA, líder SE, arrastre por
  puesto y colores obligatorios.
- Reto 4.2 dashboard HTML: implementado como archivo autocontenido, sin servidor,
  dependencias externas ni `fetch`; contrato validado para 7/7 municipios y
  sección verificable de seis bonus (+15 potenciales).
- Reto 5.1 heatmap: implementado con top 8 CA consolidado, cuatro municipios,
  porcentaje del total CA municipal, anotaciones y PNG >10 KB.
- Reto 5.2 scatter: implementado con una observación por mesa, color por
  municipio, OLS, Pearson, anotación, stdout exacto y PNG >10 KB.

