# Estrategia analítica y ML responsable

## Núcleo obligatorio

1. Descriptivo: votos CA, líderes SE y top candidatos.
2. Arrastre Verde: `votos_SE_codpar57 / votos_CA_codpar5` por puesto y municipio.
3. Dominancia: participación del candidato dentro del partido por mesa >60%.
4. Atribución: repartir voto SE según participación CA usando exactamente la fórmula dada.
5. Relación CA-SE: OLS y Pearson por mesa, con n y pendiente visibles.

## Diferenciador recomendado

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

Entregable opcional: `analysis/model_diagnostics.py` y `outputs/model_metrics.json`, solo cuando el pipeline base esté verde.

