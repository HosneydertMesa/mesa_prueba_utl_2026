---
name: auditar-prueba-utl-ciencia-datos
description: Auditar la Prueba Tecnica UTL Senado 2026 con criterio de ciencia de datos, separando cumplimiento contractual de calidad profesional. Usar al revisar penalizaciones, datos y procedencia, SQLite/ETL, SQL, modelos, OLS/Pearson, dashboard, visualizaciones, reproducibilidad, sesgos, validez estadistica o al priorizar mejoras analiticas y ML sin comprometer la entrega base.
---

# Auditar Prueba UTL como ciencia de datos

## Flujo obligatorio

1. Leer `../desarrollar-prueba-utl-datos/references/contrato-evaluacion.md`,
   `docs/01-trazabilidad-requisitos.md` y `references/rubrica-auditoria.md`.
2. Confirmar el estado real con archivos, consultas y comandos; no aceptar como
   evidencia una afirmación documental sin artefacto verificable.
3. Separar siempre tres capas: 100 puntos base, 15 puntos bonus y mejoras
   profesionales no puntuables.
4. Auditar en orden: contrato y penalizaciones, procedencia, calidad de datos,
   validez analítica, visualización, reproducibilidad y comunicación ética.
5. Ejecutar primero verificaciones no destructivas. No regenerar bases,
   artefactos ni manifest durante una revisión salvo autorización explícita.
6. Priorizar recomendaciones por impacto, riesgo de regresión y esfuerzo.

## Evidencia mínima

- Ejecutar `python scripts/verify_delivery.py` y el gate aplicable.
- Revisar `outputs/evaluation_manifest.json`, auditorías y hashes de Release.
- Verificar idempotencia, claves naturales, FK, nulos, valores negativos,
  cobertura municipal y separación entre alcance obligatorio y bonus.
- Contrastar fórmulas SQL y métricas con casos manuales o fixtures.
- Comprobar que OLS/Pearson usan mesas pareadas y que no se presentan como
  predicción, transferencia de votos o causalidad.
- Revisar agrupamiento territorial, dependencia entre observaciones, puntos
  influyentes, incertidumbre y riesgo de fuga antes de recomendar ML.
- Evaluar si cada gráfico responde una pregunta y tiene alternativa textual,
  denominador, universo, fuente y limitación interpretativa.

## Regla para modelos y ML

No recomendar un algoritmo por complejidad o apariencia. Exigir una pregunta
analítica legítima, predictores disponibles antes del resultado, baseline,
validación agrupada, métricas fuera de muestra e interpretación no causal. Si
esas condiciones no existen, preferir diagnósticos del OLS, bootstrap agrupado,
regresión robusta o sensibilidad territorial.

## Formato del dictamen

Entregar:

1. conclusión ejecutiva y riesgo de penalización;
2. matriz `criterio | evidencia | estado | riesgo`;
3. fortalezas que deben preservarse;
4. hallazgos ordenados P0/P1/P2 con beneficio, esfuerzo y prueba requerida;
5. decisión explícita `entra antes de entregar` o `posponer`;
6. límites: distinguir hechos, inferencias e información no disponible.

No inventar una calificación oficial. Si todo el contrato está cubierto, decirlo
y evitar cambios de último minuto cuyo riesgo supere su valor.
