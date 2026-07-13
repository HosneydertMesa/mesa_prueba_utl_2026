# Hoja de ruta de cierre y mejoras

> Corte: 13 de julio de 2026. Base de partida del incremento: merge commit
> `8c7e4ea53a83212cc0b25971fb7c6772bbf50d15`. Estado posterior a PR #10 y #11:
> dashboard publicado y 60 pruebas verdes.

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
| Dashboard | workspace BI, `file://`, 4/7, modo guiado, URL compartible, dark mode y CSV | QA manual multinavegador |
| Publicación | Pages HTTPS activo, Actions Node 24 y smoke posdespliegue | validar cada despliegue de `main` |
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

| ID | Propuesta | Estado | Evidencia o criterio pendiente |
|---|---|---|---|
| P1-01 | Modo presentación guiada | Implementado | recorrido accesible Resumen → Municipio → Analítica → Bonus, reversible con botón o `Esc` |
| P1-02 | Estado completo en URL | Implementado | hash conserva vista, municipio, alcance y filtro; acepta hashes simples anteriores |
| P1-03 | Smoke posdespliegue en CI | Implementado | comprueba HTTP, schema v2, 7 municipios, 1.432 mesas/puntos y huella SHA-256 |
| P1-04 | Auditoría accesible y de rendimiento | Pendiente | Lighthouse/axe documentados, sin errores críticos y presupuesto acordado |
| P1-05 | Tarjeta de procedencia | Implementado | fuente, alcance, control local no oficial, anomalías preservadas y SHA-256 reproducible |
| P1-06 | Regresión visual controlada | Pendiente | capturas estables de cuatro vistas en claro/oscuro y viewport desktop/móvil |
| P1-07 | Actualizar runtimes de GitHub Actions | Implementado | `checkout@v7`, `setup-python@v6` y actions Pages compatibles con Node 24 |

### CI y recuperación de Pages

La deuda de Node 20 quedó resuelta en rama con los majors oficiales basados en
Node 24: `actions/checkout@v7`, `actions/setup-python@v6`,
`actions/configure-pages@v6`, `actions/upload-pages-artifact@v5` y
`actions/deploy-pages@v5`. Los permisos mínimos y la composición del artefacto
se conservaron.

El error de Pages del 13 de julio no fue causado por el dashboard: el repositorio
había pasado a privado y el plan de la cuenta no admite Pages para repositorios
privados. GitHub eliminó la configuración del sitio y el deploy respondió 404.
Se restauró la visibilidad pública autorizada, se reactivó Pages con origen
`workflow` y la ejecución `29226541060` volvió a concluir `success`.

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
6. Completar auditoría accesible/rendimiento y regresión visual (P1-04/P1-06).
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
