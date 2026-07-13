# Auditoría de ciencia de datos y oportunidades

## Dictamen ejecutivo

La entrega cubre los 100 puntos base potenciales y los 15 puntos bonus
potenciales con evidencia reproducible; no es una calificación oficial. No se
detecta una mejora contractual adicional pendiente después de añadir el wrapper
raíz `python scraper.py`. Los únicos cierres previos a entrega siguen siendo QA
manual en Firefox/`file://` y congelar el SHA autorizado.

La solución ya supera una prueba de análisis de datos convencional: incorpora
ingeniería reproducible, procedencia, idempotencia, controles de integridad,
CI, Release, dashboard BI y lenguaje analítico no causal. Añadir un modelo
complejo ahora tendría más riesgo de sobreajuste que valor demostrable.

## Matriz de auditoría

| Criterio | Evidencia | Estado | Riesgo residual |
|---|---|---|---|
| Penalizaciones | segunda corrida, 4/4, dashboard 4+3, README y 21/21 rutas | Cubierto | evaluación externa |
| Procedencia | muestras no oficiales declaradas, URLs, ETag y SHA-256 | Sólido | archivos oficiales no recibidos |
| Calidad SQLite | FK, claves naturales, auditoría e invariantes | Sólido | 53 registros fuente con votantes mayores al censo, preservados |
| Validez descriptiva | unidad por mesa, OLS/Pearson y lenguaje no causal | Sólido | faltan diagnósticos de residuos e influencia |
| Reproducibilidad | clon limpio menor a 2 minutos, Release y gates | Sólido | repetir sobre SHA final |
| Dashboard | contrato autocontenido, Pages, accesibilidad y 4/7 separados | Sólido | Firefox y `file://` manuales |
| ML | estrategia y guardas documentadas | Responsable | no existe aún una pregunta predictiva defendible |

## Fortalezas que no deben alterarse

- Separación entre la base contractual de cuatro municipios y la base bonus.
- Artefactos oficiales 8×4 y 1.107 mesas separados de la extensión 8×7/1.432.
- Asociación CA-SE presentada como descripción del mismo evento, no causalidad.
- Anomalías preservadas y visibles sin imputación ni acusaciones.
- Dashboard sin servidor, CDN ni dependencia de red.

## Recomendaciones priorizadas

### P0 — antes de entregar

1. Completar Firefox y apertura directa `file://` con el checklist existente.
2. Repetir `quality_gate.py release`, registrar SHA final y congelar entrega.

El wrapper raíz ya resuelve la única ambigüedad literal encontrada entre el
árbol del PDF (`scraper/scraper.py`) y su comando de ejemplo (`python scraper.py`).

### P1 — solo si no retrasa la entrega

- Ejecutar una auditoría Lighthouse/axe y guardar resultados.
- Incorporar regresión visual estable para las cuatro vistas principales.

Son mejoras de aseguramiento, no nuevos hallazgos analíticos.

### P2 — mejor diferenciador posterior al congelamiento

Implementar un anexo de **diagnóstico y sensibilidad del modelo lineal**:

1. residuos, QQ, leverage y distancia de Cook del OLS contractual;
2. métricas por municipio y `leave-one-municipality-out`;
3. intervalos mediante bootstrap agrupado por puesto;
4. comparación OLS contra Huber o Theil-Sen;
5. salida reproducible en `outputs/model_metrics.json` y una vista suplementaria.

Esto impresiona más que un modelo complejo porque demuestra criterio científico,
reconoce la dependencia territorial y cuantifica incertidumbre. Debe presentarse
como sensibilidad exploratoria y nunca reemplazar el scatter contractual.

## Decisión

- **Entra antes de entregar:** wrapper raíz, QA manual y congelamiento.
- **Posponer:** diagnósticos avanzados, Lighthouse/regresión visual si consumen
  la reserva de cierre, y cualquier Ridge/boosting sin predictores válidos.
- **No recomendado:** redes neuronales, predicción electoral del mismo evento o
  clasificación de anomalías como fraude.

La auditoría se puede repetir con la skill local
`.agents/skills/auditar-prueba-utl-ciencia-datos/`.
