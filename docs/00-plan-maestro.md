# Plan maestro de desarrollo

## Objetivo

Construir un pipeline electoral reproducible, idempotente y auditable que obtenga
Cámara (CA) y Senado (SE), modele datos en SQLite, responda las tres preguntas
SQL, genere un dashboard estático y produzca las dos visualizaciones exigidas. La
meta sigue siendo **100/100 base antes de ampliar el alcance analítico**.

## Estado ejecutivo - 12 de julio de 2026

| Bloque | Puntos base | Estado | Evidencia |
|---|---:|---|---|
| Reto 1 - API y scraper | 25 | Implementado; manifest oficial pendiente | 1.107 mesas, 2.214 ACT, segunda corrida sin inserciones |
| Reto 2 - SQLite y ETL | 25 | Implementado; manifest oficial pendiente | integridad `ok`, cero FK inválidas, auditoría local |
| Reto 3 - SQL analítico | 25 | Implementado y probado | SQL 3.1/3.2/3.3 `ok`, casos calculables |
| Reto 4 - Dashboard | 15 | Implementado y probado | HTML autocontenido, contrato embebido y 4/4 municipios |
| Reto 5 - Visualizaciones | 10 | En progreso; 5.1 completo | heatmap 8×4 generado y probado; scatter pendiente |

Cobertura funcional interna: **95/100 puntos base potenciales**. Esta cifra no es
una calificación oficial: los retos 1.3 y 2.3 sólo quedan cerrados para entrega
cuando se ejecute `generar_manifest.py` original, aún no suministrado.

Bonus implementados y documentados: `--preflight` (+3 potencial), cinco índices
(+2 potencial) y explicación CA vs atribución SE (+2 potencial). Total potencial
adicional actual: **+7**, sujeto a evaluación.

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
| 4. Dashboard | Completada | HTML autocontenido + datos embebidos | contrato `file://`, 4 municipios y JS válido |
| 5. Visualizaciones | En progreso | Heatmap completo; scatter pendiente | ambos PNG >10 KB y stdout 5.2 exacto |
| 6. Entrega | Pendiente | Manifest, Release y repo | clon limpio, manifest oficial y PR integrado |

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

### Incremento 4.3 - Bonus de interfaz (+5 potencial)

- Dark mode mediante CSS custom properties (+3).
- Exportación CSV de la selección visible (+2).

4.2 ya está verde. Este bonus se mantiene pospuesto hasta completar el Reto 5 y
alcanzar los 100 puntos base.

### Incremento 5.1 - Heatmap (completado, 5 puntos)

- Top 8 candidatos CA por criterio documentado.
- Matriz 8×4 con porcentaje del total municipal y anotaciones.
- Generar `viz/heatmap_municipios.png` legible y >10 KB.

Evidencia: top 8 por votación CA consolidada en los cuatro municipios, matriz
8×4 con porcentaje sobre votos CA municipales, anotaciones visibles y PNG de
más de 200 KB. Pruebas cubren ranking, fórmula, cobertura y dimensiones.

### Incremento 5.2 - Scatter (5 puntos)

- Una observación por mesa y color por municipio.
- OLS, Pearson y línea ajustada sin lenguaje causal.
- Stdout exacto: `r=X.XXX | pendiente=X.XXX | n_mesas=NNN`.
- Generar `viz/scatter_ca_se.png` legible y >10 KB.

### Incremento 6 - Preparación de entrega

- Incorporar `sample_data`, `generar_manifest.py` y ejemplo originales sin modificarlos.
- Ejecutar manifest oficial y corregir cualquier diferencia contractual.
- Publicar `db/puestos_2026.db` de 64 MB como GitHub Release asset y enlazarlo.
- Ensayar clon limpio en menos de 10 minutos.
- Ejecutar gate `release`, revisar en incógnito y fusionar el PR sólo con autorización.

## Bloqueos externos

- No se recibieron `sample_data/` oficiales.
- No se recibieron `outputs/generar_manifest.py` ni
  `evaluation_manifest.example.json` originales.

Estos bloqueos no impiden Reto 4 o 5. Sí impiden declarar cerrados oficialmente
1.3, 2.3 y la entrega final.

## Definición de terminado global

- Clon limpio reproducible en menos de 10 minutos.
- Primera y segunda ejecución exitosas; la segunda no duplica resultados.
- Cuatro municipios y ambas corporaciones presentes.
- `PRAGMA foreign_key_check` vacío e invariantes de votos aprobadas.
- Tres SQL ejecutadas por el manifest sin error.
- Dashboard desde `file://`, cuatro municipios y consola limpia.
- PNG legibles y mayores de 10 KB.
- README conserva exactamente los headings obligatorios.
- Base accesible mediante Release, metadata real, manifest oficial y repo público.

Las decisiones contrastadas con fuentes están en
[07-fuentes-investigacion.md](07-fuentes-investigacion.md).
