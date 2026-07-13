---
name: desarrollar-prueba-utl-datos
description: Desarrollar y revisar incrementos de la Prueba Tecnica UTL Senado 2026 en este repositorio, manteniendo trazabilidad entre retos 1-5, archivos obligatorios, penalizaciones, manifest, pruebas, dashboard, visualizaciones y bonus. Usar al implementar scraper electoral, SQLite/ETL, SQL de arrastre, dashboard estatico, graficos CA-SE, analitica suplementaria o preparacion de la entrega.
---

# Desarrollar Prueba Utl Datos

## Flujo obligatorio

1. Leer `references/contrato-evaluacion.md` y el plan relacionado.
2. Identificar ID, puntaje, artefacto, salida observable y penalización.
3. Verificar insumos reales; no inventar campos o endpoints.
4. Implementar el incremento mínimo que atraviese las capas necesarias.
5. Agregar una prueba proporcional al riesgo y ejecutar validaciones.
6. Actualizar documentación sin cambiar los headings del README.
7. No declarar terminado sin evidencia reproducible.

## Guardas

- Preservar rutas, nombres, colores, `codpar`, fórmulas y stdout exigidos.
- Respaldar `INSERT OR IGNORE` con `UNIQUE` y demostrar doble ejecución.
- Activar `PRAGMA foreign_keys=ON` en cada conexión.
- Tratar denominador cero como `NULL` documentado.
- Separar valor fuente de valor normalizado.
- No convertir correlación o atribución en causalidad.
- Priorizar 100 puntos base; hacer ML/bonus con manifest base verde.
- No copiar el PDF confidencial al repositorio público.

## Validación mínima

- Scraper: fixture, retry simulado, filtro, preflight y segunda corrida.
- ETL/DB: conteos, insertadas/omitidas, FK, nulos y votos negativos.
- SQL: casos calculables a mano, orden determinista y cuatro municipios.
- Dashboard: `file://`, consola limpia, cuatro municipios, colores y línea 1.0.
- Viz/ML: stdout exacto, etiquetas legibles, validación agrupada y lenguaje no causal.
- Entrega: estructura, manifest contractual reproducible, clon cronometrado y repo público.
