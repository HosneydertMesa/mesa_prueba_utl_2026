# Plan maestro de desarrollo

## Objetivo

Construir un pipeline electoral reproducible, idempotente y auditable que obtenga
Cámara (CA) y Senado (SE), modele datos en SQLite, responda las tres preguntas
SQL, genere un dashboard estático y produzca las dos visualizaciones exigidas. La
meta sigue siendo **100/100 base antes de ampliar el alcance analítico**.

## Estado ejecutivo - 13 de julio de 2026

| Bloque | Puntos base | Estado | Evidencia |
|---|---:|---|---|
| Reto 1 - API y scraper | 25 | Implementado y validado por manifest | 4/4, 1.107 mesas, 2.214 ACT, segunda corrida sin inserciones |
| Reto 2 - SQLite y ETL | 25 | Implementado y validado por manifest | integridad `ok`, cero FK inválidas y líderes SE municipales |
| Reto 3 - SQL analítico | 25 | Implementado y probado | SQL 3.1/3.2/3.3 `ok`, casos calculables |
| Reto 4 - Dashboard | 15 | Implementado y probado | HTML autocontenido, 4 obligatorios + 3 bonus etiquetados |
| Reto 5 - Visualizaciones | 10 | Implementado y probado | heatmap 8×4 + scatter de 1.107 mesas |

Cobertura funcional interna: **100/100 puntos base potenciales**. Esta cifra no es
una calificación oficial. El `generar_manifest.py` implementado desde el contrato
observable del PDF queda verde con 4/4 municipios y SQL `OK` en los tres retos.

Bonus implementados y documentados: `--preflight` (+3 potencial), cinco índices
(+2), explicación CA vs atribución SE (+2), modo oscuro (+3), exportación CSV
(+2) y tres municipios adicionales (+3). Total potencial: **+15/+15**, sujeto a
evaluación.

## Principios

1. Contrato antes que código: conservar muestras y documentar endpoint, campos y claves naturales.
2. Camino feliz pequeño: validar una mesa CA+SE antes de escalar.
3. Idempotencia demostrada: segunda ejecución con cero duplicados y conteos estables.
4. Evidencia automática: cada requisito tiene artefacto, prueba y salida observable.
5. Analítica responsable: separar descripción, atribución determinística y modelos; no inferir causalidad.
6. Reproducibilidad en 10 minutos: instalación, comandos claros, artefactos y manifest final.

## Fases y puertas de calidad

| Fase | Estado | Resultado | Puerta de salida |
|---|---|---|---|
| 0. Descubrimiento | Completada | Contrato API y nomenclator | endpoint real, campos y fallback documentados |
| 1. Esqueleto vertical | Completada | Mesa CA+SE hasta SQLite | reejecución estable y FK activas |
| 2. Cobertura | Completada localmente | Cuatro municipios | 4/4 y 2.214 resultados en auditoría local |
| 3. SQL | Completada | Tres consultas | casos manuales, orden estable y ejecución real |
| 4. Dashboard | Completada | HTML autocontenido + datos embebidos | contrato `file://`, 7 municipios con alcance explícito y JS válido |
| 5. Visualizaciones | Completada | Heatmap + scatter | ambos PNG >10 KB y stdout 5.2 exacto |
| 6. Entrega | En curso | Repo, Pages, Release, muestras, manifest y clon limpio verificados | QA Firefox/`file://` y tag final |

## Plan atómico restante

### Incremento 4.1 - Contrato de exportación (completado)

- Implementar `dashboard/export_data.py` desde SQLite.
- Generar `dashboard/data.json` determinista con cuatro municipios.
- Incluir votos CA totales, top 10 CA, líder SE y arrastre Verde por puesto.
- Probar schema JSON, orden, colores y regeneración estable.

Evidencia: cuatro municipios, 73 puestos, 1.107 mesas, colores exactos, top 10,
líder SE y arrastre por puesto. Serialización determinista y contrato integrado a
la auditoría local.

### Incremento 4.2 - Dashboard base (completado, 15 puntos)

- Construir un único `dashboard/index.html` autocontenido.
- Abrir directamente mediante `file://`, sin servidor ni fetch bloqueado por CORS.
- Incorporar comparativo CA, selector municipal, top 10 CA, líder SE y arrastre.
- Preservar `#007C34`, `#7B2D8B`, `#1E477D`, `#E07B00` y referencia `1.0`.
- Validar Chrome/Firefox, consola limpia, responsive y accesibilidad básica.

Evidencia: un único `dashboard/index.html`, sin dependencias externas ni
`fetch`; cuatro municipios, comparativo CA, top 10, líder SE, arrastre, colores
exactos y referencia `1.0`. Los datos embebidos coinciden byte a byte con el
contrato exportado y las pruebas verifican los landmarks accesibles.

### Incremento 4.3 - Bonus de interfaz (completado, +5 potencial)

- Dark mode mediante CSS custom properties (+3).
- Exportación CSV de la selección visible (+2).

Evidencia: tema oscuro implementado con CSS custom properties, preferencia del
sistema y persistencia local; exportación CSV UTF-8 de la selección municipal
visible. Ambos funcionan desde `file://`, sin recursos externos, y están bajo
pruebas contractuales. Véase `docs/18-bonus-dashboard.md`.

### Incremento 4.4 - Dashboard Analítico 2.0 (completado, suplementario)

- Extender el contrato embebido a schema v2 sin cambiar las vistas obligatorias.
- Conservar la matriz contractual 8×4 y las 1.107 observaciones del Reto 5.
- Añadir una vista suplementaria 8×7 con las 1.432 mesas de los siete
  municipios, con estadísticas calculadas de forma independiente.
- Añadir hallazgos ejecutivos, heatmap semántico y scatter Canvas interactivo.
- Incorporar los tres municipios extra y la evidencia de los seis bonus sin
  cambiar el universo analítico obligatorio.
- Mantener `file://`, accesibilidad, tema oscuro y ausencia de dependencias web.

Evidencia: `dashboard/data.json` contiene siete municipios, seis bonus por
15 puntos potenciales, la matriz y los puntos auditados; el HTML ofrece filtro
municipal, tooltips, OLS global y una explicación no causal.
Véase `docs/20-dashboard-analitico-2.md`.

### Incremento 4.5 - Workspace analítico y Pages (completado, suplementario)

- Sustituir la lectura tipo landing por cuatro espacios de trabajo navegables.
- Preservar un solo HTML, apertura `file://`, dark mode, CSV y accesibilidad.
- Mantener el universo analítico obligatorio separado de los municipios bonus.
- Publicar únicamente los artefactos estáticos del dashboard mediante GitHub
  Pages después de revisión y fusión a `main`.

Evidencia: navegación lateral/inferior accesible, estado por fragmento de URL,
redibujado seguro del Canvas, workflow con permisos mínimos y publicación HTTPS
verificada desde `main` mediante el PR #7. Véase
`docs/21-dashboard-workspace-pages.md`.

### Incremento B6 - Municipios adicionales (completado, +3 potencial)

- Extender el nomenclátor y el scraper a municipios adicionales de Boyacá.
- Mantener separados el alcance obligatorio de cuatro municipios y la ampliación.
- Regenerar base, auditoría y evidencia sin romper los conteos contractuales.

Evidencia: Chiquinquirá, Puerto Boyacá y Moniquirá fueron seleccionados por ser
los tres municipios no obligatorios con más mesas. El preflight confirmó 7/7,
104 puestos, 1.432 mesas y 2.864 ACT. La base ampliada auditó `ok=True` y la
segunda corrida registró `insertadas=0`. Véase
`docs/19-bonus-municipios-boyaca.md`.

### Incremento 5.1 - Heatmap (completado, 5 puntos)

- Top 8 candidatos CA por criterio documentado.
- Matriz 8×4 con porcentaje del total municipal y anotaciones.
- Generar `viz/heatmap_municipios.png` legible y >10 KB.

Evidencia: top 8 por votación CA consolidada en los cuatro municipios, matriz
8×4 con porcentaje sobre votos CA municipales, anotaciones visibles y PNG de
más de 200 KB. Pruebas cubren ranking, fórmula, cobertura y dimensiones.

### Incremento 5.2 - Scatter (completado, 5 puntos)

- Una observación por mesa y color por municipio.
- OLS, Pearson y línea ajustada sin lenguaje causal.
- Stdout exacto: `r=X.XXX | pendiente=X.XXX | n_mesas=NNN`.
- Generar `viz/scatter_ca_se.png` legible y >10 KB.

Evidencia: 1.107 mesas pareadas mediante `resumen_mesa`, cuatro colores
municipales, OLS global, Pearson anotado y stdout exacto. Resultado observado:
`r=0.964 | pendiente=0.933 | n_mesas=1107`; PNG superior a 260 KB.

### Incremento 6 - Preparación de entrega

- Incorporar muestras reales con procedencia explícita y sin atribuirlas a la UTL.
- Implementar y ejecutar `generar_manifest.py` desde el contrato observable del PDF.
- Generar `evaluation_manifest.json` y su ejemplo de forma determinista.
- Release `data-v1.0.0` publicado con bases 4/4 y 7/7, tamaños y SHA-256.
- Clon limpio ensayado en menos de 2 minutos observados; gates base verdes.
- Ejecutar gate `release`, revisar `file://`/Firefox y congelar el tag final.

## Decisión sobre insumos no incluidos

- El PDF describe `sample_data/` como provisto, pero el paquete recibido sólo
  contenía el PDF y no tenía adjuntos embebidos.
- El PDF exige el generador y el ejemplo, pero no afirma que sean suministrados.
- Se incluyeron capturas reales de la API con `official_utl_sample=false` y se
  implementó el generador con
  `generator_provenance=candidate_implemented_from_pdf_contract`.

La ausencia del paquete adicional ya no se trata como bloqueo externo. Si la UTL
entrega posteriormente archivos originales, se conservarán aparte y se compararán
sin reescribir la evidencia actual.

## Definición de terminado global

- Clon limpio reproducible en menos de 10 minutos.
- Primera y segunda ejecución exitosas; la segunda no duplica resultados.
- Cuatro municipios y ambas corporaciones presentes.
- `PRAGMA foreign_key_check` vacío e invariantes de votos aprobadas.
- Tres SQL ejecutadas por el manifest sin error.
- Dashboard desde `file://`, siete municipios etiquetados y consola limpia; la
  vista contractual conserva cuatro municipios y 1.107 mesas, mientras la vista
  suplementaria cubre siete municipios y 1.432 mesas.
- PNG legibles y mayores de 10 KB.
- README conserva exactamente los headings obligatorios.
- Base accesible mediante Release, metadata real, manifest contractual y repo público.

Las decisiones contrastadas con fuentes están en
[07-fuentes-investigacion.md](07-fuentes-investigacion.md).
Los cierres pendientes y evoluciones opcionales están priorizados en
[22-hoja-ruta-mejoras.md](22-hoja-ruta-mejoras.md).
