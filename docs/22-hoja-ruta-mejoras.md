# Hoja de ruta de cierre y mejoras

> Corte: 13 de julio de 2026. Base funcional de referencia: merge commit
> `7c5272e04f6e1a329c96ab55e5ccc9da95ffe0e6`, dashboard publicado y 58 pruebas
> verdes.

## Propósito

Este documento separa tres clases de trabajo que no deben mezclarse:

1. **Cierre de entrega:** condiciones que todavía impiden declarar la prueba
   completamente entregable.
2. **Mejoras de alto impacto:** evoluciones pequeñas que elevan presentación,
   accesibilidad o confiabilidad sin cambiar el contrato evaluado.
3. **Analítica exploratoria:** diferenciadores opcionales que solo se ejecutan
   cuando la entrega base está congelada y reproducible.

Las mejoras nunca deben reemplazar el heatmap 8×4, el scatter de 1.107 mesas,
los tres SQL, los nombres/colores exigidos ni el manifest oficial.

## Estado de partida

| Área | Estado confirmado | Asunto abierto |
|---|---|---|
| Retos 1-5 | 100/100 potenciales, auditados localmente | validación con manifest oficial |
| Bonus | +15/+15 potenciales | validación del evaluador |
| Datos base | 4 municipios, 1.107 mesas, 2.214 ACT | publicar SQLite como Release asset |
| Datos bonus | 7 municipios, 1.432 mesas, 2.864 ACT | ninguno funcional |
| Dashboard | workspace BI, `file://`, 4/7, dark mode y CSV | QA manual multinavegador |
| Publicación | Pages HTTPS activo y workflows verdes | automatizar smoke posdespliegue |
| Reproducibilidad | runbook, auditorías y gates | ensayo desde clon limpio <10 minutos |
| Insumos UTL | PDF revisado, contrato documentado | faltan muestras y generador oficiales |

## Prioridad P0: cerrar antes de entregar

| ID | Mejora o cierre | Valor | Esfuerzo estimado | Criterio de terminado |
|---|---|---|---:|---|
| P0-01 | Incorporar insumos oficiales | Evita falsos positivos frente al evaluador | depende de UTL | archivos originales sin modificar, manifest ejecutado y SQL `OK` ×3 |
| P0-02 | Publicar SQLite contractual en Release | Permite reproducir sin descargar nuevamente 2.214 ACT | 30-45 min | asset descargable, tamaño y SHA-256 documentados en README |
| P0-03 | Ensayar clon limpio | Prueba que no dependemos de caché o conocimiento implícito | 45-60 min | ejecución documentada en menos de 10 minutos y gate RELEASE verde |
| P0-04 | QA manual de interfaz | Cubre riesgos visuales que los contratos HTML no detectan | 30-45 min | Chrome y Firefox; desktop y móvil; teclado, tema, CSV, tooltips y consola limpios |
| P0-05 | Congelar entrega | Evita que el SHA evaluado cambie | 15 min | `main` limpio, tag/release, SHA registrado y formulario enviado una vez |

### Evidencia mínima de P0-04

- Abrir tanto `dashboard/index.html` mediante `file://` como la URL de Pages.
- Recorrer Resumen, Municipio, Analítica y Bonus solo con teclado.
- Alternar `Obligatorio 4` y `Ampliado 7`; comprobar 8×4/1.107 y 8×7/1.432.
- Probar cada municipio, modo oscuro persistente y CSV con tildes correcto.
- Revisar anchuras aproximadas de 360, 768, 1.280 y 1.920 px.
- Confirmar ausencia de errores, recursos bloqueados o scroll horizontal.

## Prioridad P1: alto impacto y riesgo bajo

| ID | Propuesta | Por qué hace diferencia | Criterio de aceptación |
|---|---|---|---|
| P1-01 | Modo presentación guiada | Permite explicar el proyecto en 3-5 minutos sin navegar libremente | recorrido Resumen → Municipio → Analítica → Bonus, reversible y accesible |
| P1-02 | Estado completo en URL | Hace compartible una vista exacta del análisis | hash conserva vista, municipio, alcance y filtro sin romper `file://` |
| P1-03 | Smoke posdespliegue en CI | Detecta Pages verde pero contenido incompleto | verifica HTTP 200, schema v2, 7 municipios y 1.432 puntos después del deploy |
| P1-04 | Auditoría accesible y de rendimiento | Aporta evidencia objetiva adicional | Lighthouse/axe documentados, sin errores críticos y presupuesto acordado |
| P1-05 | Tarjeta de procedencia | Mejora confianza y lectura ejecutiva | muestra fuente, fecha de corrida, alcance, anomalías preservadas y SHA del dataset |
| P1-06 | Regresión visual controlada | Evita romper el layout al ajustar CSS | capturas estables de cuatro vistas en claro/oscuro y viewport desktop/móvil |
| P1-07 | Actualizar runtimes de GitHub Actions | Elimina la advertencia de Node 20 obsoleto observada en CI | majors compatibles con Node 24, gates verdes y cero anotaciones de deprecación |

### Deuda técnica de CI observada

El workflow `quality` del merge documental concluyó correctamente, pero la
ejecución `29227104337` informó que `actions/checkout@v4` y
`actions/setup-python@v5` usan Node 20 y están siendo forzadas a Node 24 por el
runner alojado de GitHub. No bloquea la entrega actual, pero debe resolverse
antes de que la compatibilidad transitoria desaparezca.

Plan de actualización:

1. Probar en una rama un major compatible con Node 24 para ambas actions.
2. Conservar `python-version` explícito y los permisos mínimos actuales.
3. Ejecutar `quality` y `deploy-dashboard-pages` sin warnings de deprecación.
4. Fusionar solo si artefacto Pages, caché y gates permanecen idénticos.

Al corte de este documento, las fuentes oficiales registran majors modernos con
Node 24: [releases de `actions/checkout`](https://github.com/actions/checkout/releases)
y [releases de `actions/setup-python`](https://github.com/actions/setup-python/releases).
La compatibilidad del runner debe verificarse antes de seleccionar el major.

### Recomendación de diseño

La mejor siguiente evolución no es agregar más gráficos al mismo lienzo. El
workspace ya resolvió el problema de la landing larga; ahora conviene mejorar la
**narrativa**:

- una franja discreta con alcance, fuente y última actualización;
- un botón de presentación que avance por cuatro hallazgos preparados;
- títulos que expresen la conclusión y no solo el tipo de gráfico;
- estado de filtros visible y compartible;
- una tabla/resumen textual equivalente para cada visualización.

No se recomienda incrementar la densidad del Resumen ni volver a un scroll
vertical extenso. La regla de diseño debe ser: una pregunta analítica principal
por vista y detalle bajo demanda.

## Prioridad P2: analítica suplementaria responsable

| ID | Propuesta | Método | Límite interpretativo |
|---|---|---|---|
| P2-01 | Diagnóstico de OLS | residuos, QQ, leverage y distancia de Cook | influencia estadística no significa fraude |
| P2-02 | Sensibilidad territorial | leave-one-municipality-out y métricas por municipio | siete municipios siguen siendo una muestra pequeña |
| P2-03 | Incertidumbre | bootstrap agrupado por puesto/municipio e intervalos | no usar partición aleatoria por mesa |
| P2-04 | Regresión robusta | comparar OLS con Huber/Theil-Sen | es sensibilidad, no reemplazo del Reto 5 |
| P2-05 | Explorador de calidad | detalle de `votantes > censo`, cobertura y balances | conservar fuente; no imputar ni acusar irregularidad |
| P2-06 | Ridge con predictores válidos | baseline, validación agrupada y MAE/RMSE | no llamarlo predicción electoral del mismo evento |

El primer diferenciador recomendado es **P2-01 + P2-02**, porque profundiza el
modelo ya exigido y conserva explicabilidad. Un algoritmo más complejo solo se
justifica si aparece una pregunta predictiva real y variables anteriores al
resultado; con los datos actuales, boosting o redes neuronales añadirían más
riesgo de sobreajuste que valor.

## Mejoras deliberadamente pospuestas

- Migrar a React, Angular, Power BI embebido o un backend: rompe la simplicidad
  de un HTML autocontenido sin aportar puntos del contrato.
- Añadir autenticación o base en nube: no existe requisito ni dato sensible que
  lo justifique.
- Incluir mapas o librerías desde CDN: introduce red, licencias y nuevos modos
  de fallo; solo considerar una solución local y accesible después de P0.
- Generar conclusiones automáticas con IA: reduce trazabilidad y puede convertir
  asociación en una afirmación causal incorrecta.
- Mezclar los siete municipios en los PNG oficiales: el dashboard puede ampliar,
  pero los artefactos contractuales deben seguir siendo 8×4 y 1.107 mesas.

## Orden recomendado de ejecución

1. Solicitar o recibir insumos oficiales (P0-01).
2. Completar QA manual mientras se espera el insumo (P0-04).
3. Publicar la base y documentar checksum (P0-02).
4. Ensayar clon limpio y corregir cualquier paso implícito (P0-03).
5. Congelar SHA/tag y entregar (P0-05).
6. Solo con reserva de tiempo, implementar P1-03 y P1-01.
7. Presentar P2-01/P2-02 como idea o anexo; no arriesgar el artefacto final.

## Regla de decisión

Una mejora entra antes de entregar únicamente si:

- no modifica una salida contractual ni los headings obligatorios del README;
- cuenta con prueba o evidencia reproducible;
- puede revertirse en un commit atómico;
- deja al menos 90 minutos para ejecutar el runbook final;
- eleva claridad, reproducibilidad o confianza más que complejidad.

La trazabilidad base permanece en `docs/01-trazabilidad-requisitos.md`, el camino
de entrega en `docs/06-runbook-entrega.md` y la estrategia estadística en
`docs/04-estrategia-analitica-ml.md`.
