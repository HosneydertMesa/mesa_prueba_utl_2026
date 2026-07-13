# Estrategia analítica y ML responsable

## Núcleo obligatorio

1. **Completado:** descriptivo de votos CA, líderes SE y top candidatos.
2. **Completado:** arrastre Verde `votos_SE_codpar57 / votos_CA_codpar5` por puesto.
3. **Completado:** dominancia individual por mesa estrictamente mayor a 60%.
4. **Completado:** atribución SE con fórmula exacta y homologación documentada.
5. **Completado (Reto 5.2):** OLS y Pearson por mesa, con n y pendiente visibles.

## Diferenciador recomendado después del Reto 5

Añadir un análisis suplementario, no requerido por el manifest:

- OLS base idéntico al gráfico obligatorio.
- Intervalos de confianza y diagnóstico de residuos.
- Distancia de Cook o leverage para mesas influyentes, sin etiquetarlas como fraude.
- Sensibilidad `leave-one-municipality-out`: entrenar con tres y evaluar el cuarto.
- Ridge comparativo si existen predictores válidos; comparar MAE/RMSE contra baseline.
- Resultados por municipio y consolidado para evitar dominancia por tamaño.

La validación debe agrupar por municipio o puesto; una partición aleatoria mezclaría observaciones relacionadas. Con cuatro municipios, las métricas tienen alta incertidumbre y son exploratorias.

## Qué no hacer

- No usar modelos complejos solo para impresionar: elevan sobreajuste y reducen explicabilidad.
- No llamar “predicción electoral” a una regresión del mismo evento.
- No interpretar `r` alto como transferencia causal CA→SE.
- No ocultar outliers ni imputar votos sin regla documentada.

Entregable opcional: `analysis/model_diagnostics.py` y
`outputs/model_metrics.json`, sólo cuando dashboard, heatmap, scatter y manifest
base estén verdes. Los 100 puntos base y el manifest ya están verdes; el modelo
continúa pospuesto hasta cerrar los controles manuales y congelar la entrega.

## Criterio de activación ML

ML se autoriza únicamente si:

- Reto 4 y Reto 5 pasan sus contratos;
- el manifest contractual y el gate RELEASE están verdes;
- quedan al menos 90 minutos de reserva;
- el resultado se presenta como sensibilidad exploratoria y no como predicción.

La secuencia priorizada, criterios de terminado y mejoras que no conviene
ejecutar antes de la entrega están en `docs/22-hoja-ruta-mejoras.md`.
