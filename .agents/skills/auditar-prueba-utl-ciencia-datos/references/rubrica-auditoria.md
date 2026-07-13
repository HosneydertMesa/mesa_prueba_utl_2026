# Rúbrica de auditoría científica

## 1. Contrato y entrega

- Trazar cada requisito, penalización y bonus a archivo, prueba y salida.
- Confirmar estructura, comandos literales, repo público, `main`, README,
  manifest, Release y apertura estática.
- Tratar una excepción documentada por el PDF, como SQLite mayor a 50 MB en un
  Release, como cumplimiento y no como archivo ausente.

## 2. Procedencia y calidad de datos

- Identificar fuente, fecha, alcance, ETag/hash y condición oficial/no oficial.
- Verificar cobertura CA/SE, unicidad, FK, campos obligatorios, enteros no
  negativos, denominadores cero y reconciliación de conteos.
- Conservar anomalías de fuente en una capa explícita; no corregir, excluir ni
  imputar sin una regla oficial reproducible.

## 3. Validez analítica

- Distinguir votos observados, porcentajes, cocientes, atribución determinista,
  asociación estadística y predicción.
- Verificar unidad de análisis, universo y denominador de cada métrica.
- Para OLS/Pearson revisar linealidad, heterocedasticidad, residuos, leverage,
  distancia de Cook y dependencia entre mesas de un mismo puesto o municipio.
- No interpretar correlación alta como transferencia, intención o causalidad.

## 4. Modelado responsable

Antes de aceptar ML exigir:

- objetivo que no sea una reformulación del mismo resultado observado;
- predictores temporalmente válidos y sin fuga;
- baseline simple;
- partición por puesto o municipio, nunca aleatoria por mesa relacionada;
- MAE/RMSE e incertidumbre fuera de muestra;
- sensibilidad territorial y explicación de límites.

Orden recomendado con estos datos:

1. diagnóstico del OLS contractual;
2. `leave-one-municipality-out`;
3. bootstrap agrupado por puesto o municipio;
4. comparación OLS vs Huber/Theil-Sen;
5. Ridge solo con predictores defendibles.

Boosting, redes neuronales o afirmaciones de fraude no están justificados por el
alcance actual.

## 5. Visualización y comunicación

- Una pregunta principal por vista; títulos orientados a conclusión.
- Fuente, universo, unidad, denominador, filtros y alcance visibles.
- Colores consistentes, texto alternativo, teclado y tabla/resumen equivalente.
- Separar visualmente cuatro municipios obligatorios y tres bonus.
- Presentar anomalías como controles de calidad, no como irregularidades.

## 6. Reproducibilidad y operación

- Repetir desde clon limpio o usar evidencia reciente y verificable.
- Registrar versiones, comandos, tiempo, hashes y SHA del commit evaluado.
- Mantener un único camino canónico y wrappers mínimos para comandos ambiguos.
- Congelar la entrega cuando base, bonus, CI y QA manual estén verdes.

## Priorización

| Prioridad | Criterio |
|---|---|
| P0 | Evita penalización, ausencia o resultado incorrecto |
| P1 | Eleva confianza o experiencia con riesgo bajo |
| P2 | Diferenciador exploratorio no contractual |

Una mejora entra antes de entregar únicamente si es reversible, tiene prueba,
no altera salidas contractuales y deja margen para repetir RELEASE y QA manual.
