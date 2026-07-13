# Plan maestro de desarrollo

## Objetivo

Construir en 48 horas un pipeline electoral reproducible, idempotente y auditable que obtenga Cámara (CA) y Senado (SE), modele datos en SQLite, responda las tres preguntas SQL, genere un dashboard estático y produzca las dos visualizaciones exigidas. La meta es **100/100 base antes de perseguir los 15 puntos bonus**.

## Principios

1. Contrato antes que código: conservar muestras y documentar endpoint, campos y claves naturales.
2. Camino feliz pequeño: completar Tunja CA+SE de extremo a extremo antes de escalar.
3. Idempotencia demostrada: segunda ejecución con cero duplicados y conteos estables.
4. Evidencia automática: cada requisito tiene artefacto, prueba y salida observable.
5. Analítica responsable: separar descripción, atribución determinística y modelos; no inferir causalidad.
6. Reproducibilidad en 10 minutos: instalación, comandos claros y manifest final.

## Fases y puertas de calidad

| Fase | Tiempo | Resultado | Puerta de salida |
|---|---:|---|---|
| 0. Descubrimiento | 1.5 h | Contrato API/muestras | Endpoint o fallback reproducible; 8+ campos descritos |
| 1. Esqueleto vertical | 2 h | Tunja CA+SE hasta SQLite | Reejecución estable; FK activas |
| 2. Cobertura | 2 h | Cuatro municipios | Manifest reporta 4/4 y conteos plausibles |
| 3. SQL | 2.5 h | Tres consultas | Corren juntas, columnas estables, casos borde probados |
| 4. Productos | 4 h | JSON, dashboard y PNG | 4 municipios, consola limpia, PNG >10 KB |
| 5. Calidad/bonus | 3 h | Pruebas e índices | Pipeline limpio desde cero y segunda corrida |
| 6. Entrega | 1.5 h | README, manifest y repo | Checklist en incógnito, commit congelado |
| Reserva | 3.5 h | Correcciones | No usar en nuevas funciones con base pendiente |

## Backlog priorizado

### P0 - bloquea puntaje base

- Incorporar `sample_data` y evaluador oficiales sin modificarlos.
- Descubrir nomenclator, URL, cabeceras, jerarquía y claves de CA/SE.
- Diseñar claves naturales y `UNIQUE` antes de descargar masivamente.
- Implementar scraper parametrizable, retry/backoff y logging.
- Implementar schema, transacciones, FK, ETL y `carga_log`.
- Resolver y probar SQL 3.1, 3.2 y 3.3.
- Exportar `data.json`, construir dashboard y generar PNG.
- Ejecutar el manifest oficial y corregir discrepancias.

### P1 - asegura calidad y 100 puntos

- Pruebas unitarias de normalización, claves, ratios y denominador cero.
- Integración fixture -> SQLite -> SQL -> exportación.
- Contratos de nombres, rutas, headings y salida de consola.
- Validación de dashboard desde `file://`, accesibilidad y responsive.
- README cronometrado desde clon limpio.

### P2 - bonus de bajo riesgo

- `--preflight` (+3), tres índices medidos con `EXPLAIN QUERY PLAN` (+2).
- Explicación de ranking CA vs atribución SE (+2).
- Dark mode (+3) y exportación CSV (+2).

### P3 - diferenciadores tras manifest verde

- Diagnóstico OLS: intervalos, residuos, influencia y sensibilidad por municipio.
- Ridge comparativo con validación agrupada; se presenta como exploratorio, no pronóstico.
- Ficha de datos con cobertura, procedencia, limitaciones y checksums.
- Municipios adicionales (+3) detrás de configuración separada.

## Definición de terminado

- Clon limpio reproducible en menos de 10 minutos.
- Primera y segunda ejecución exitosas; la segunda no duplica resultados.
- Cuatro municipios y ambas corporaciones presentes.
- `PRAGMA foreign_key_check` vacío e invariantes de votos aprobadas.
- Tres SQL ejecutadas por el manifest sin error.
- Dashboard desde `file://`, cuatro municipios y consola limpia.
- PNG legibles y mayores de 10 KB.
- README conserva exactamente los headings obligatorios.
- Metadata real, manifest generado, repo público y commit anterior al cierre.

Las decisiones técnicas contrastadas con documentación oficial están registradas en [07-fuentes-investigacion.md](07-fuentes-investigacion.md).

