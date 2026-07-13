# Estrategia de calidad y ciclo de vida

## Flujo de trabajo

1. Issue o backlog con ID del enunciado.
2. Rama corta `feature/reto-X-Y-descripcion`.
3. Prueba/fixture que expresa el contrato antes del código riesgoso.
4. Implementación mínima y revisión del diff.
5. Validación local, auditoría/manifest aplicable y documentación.
6. Commit pequeño, push a rama y CI en PR borrador.

Estado actual: 64 pruebas pasan, Ruff está limpio y los gates
DEV/QA/SEC/REVIEW/RELEASE están verdes. GitHub Actions ejecuta los controles
base en cada push y PR; RELEASE se ejecuta localmente después de descargar la
base contractual desde el Release.

## Pirámide de pruebas

- Unitarias: normalización, parsing, claves, ratios, atribución y stdout.
- Integración: fixture CA+SE -> SQLite temporal -> SQL -> exportación.
- Contrato: archivos, headings, colores, JSON, columnas y HTML autocontenido.
- End-to-end: cuatro municipios obligatorios auditados, manifest `OK`, dashboard
  7/7, heatmap y scatter completos; sólo resta la revisión manual Firefox/`file://`.

## Evidencia específica del bonus municipal

- El alcance predeterminado continúa siendo exactamente los cuatro municipios.
- `--incluir-bonus` añade tres municipios deterministas y no acepta duplicados.
- El resolver valida que cada nombre pertenezca a Boyacá y exista en CA y SE.
- Preflight real: 7 municipios, 104 puestos, 1.432 mesas y 2.864 ACT.
- Base bonus separada, auditoría completa y segunda corrida con cero inserciones.

## Evidencia específica del dashboard

- El JSON embebido debe ser idéntico a `dashboard/data.json`.
- Se rechazan `fetch`, scripts externos, CDNs y URLs HTTP en el HTML.
- Cada municipio debe exponer top 10 CA, líder SE y arrastre por puesto.
- El contrato exige 4 municipios obligatorios, 3 bonus, 104 puestos, 1.432 mesas
  totales, 1.107 mesas analíticas obligatorias, 1.432 ampliadas y seis
  bonificaciones que suman +15.
- Los cuatro colores obligatorios y la referencia `1.0` están bajo contrato.
- El tema oscuro usa CSS custom properties, conserva estado accesible y persiste
  una preferencia local sin comprometer la apertura mediante `file://`.
- El CSV exportado contiene la selección municipal visible, cabeceras estables,
  BOM UTF-8 y valores escapados; no necesita backend ni acceso de red.
- El JavaScript embebido se compila sintácticamente con Node antes del commit.
- El schema v2 exige matriz 8×4, 1.107 puntos y `n_mesas=1107`.
- La extensión exige matriz 8×7, 1.432 puntos, siete colores y estadísticos
  recalculados sin sobrescribir el contrato 8×4/1.107.
- El heatmap interactivo usa una tabla semántica; el scatter Canvas conserva
  resumen textual, filtros con `aria-pressed` y descripción accesible.
- El workspace exige cuatro vistas, semántica de pestañas, navegación por hash y
  ausencia de identificadores HTML duplicados.
- El workflow Pages solo empaqueta `dashboard/index.html` y `data.json`, con
  permisos mínimos y despliegue desde `main`.
- El despliegue usa Actions con runtime Node 24 y un smoke posterior que valida
  el contenido HTTPS publicado: schema, cobertura, scatter y huella SHA-256.
- La metadata visible declara procedencia local no oficial y conserva el conteo
  de anomalías sin imputación; su huella se deriva del contenido canónico.

## Evidencia específica del heatmap

- Ranking determinista del top 8 por votos CA consolidados.
- Matriz contractual de 8 filas × 4 municipios en orden explícito.
- Fórmula de cada celda probada contra un fixture calculable a mano.
- Error temprano si falta un municipio, un candidato o un denominador positivo.
- PNG real inspeccionado visualmente, con anotaciones y peso superior a 10 KB.
- CI instala las dependencias declaradas antes de ejecutar los gates.

## Evidencia específica del scatter

- Una observación por cada mesa con resúmenes CA y SE; 1.107/1.107 pareadas.
- Cuatro municipios presentes con conteos 424, 95, 301 y 287.
- Fixture exacto `SE = 2 × CA + 5` para validar `r=1`, pendiente 2 e intercepto 5.
- Error temprano si una mesa carece de cualquiera de las dos corporaciones.
- Stdout exacto probado con tres decimales y `n_mesas` entero.
- PNG inspeccionado visualmente y superior a 10 KB; lenguaje no causal.

## Reglas de calidad de datos

- Campos esenciales no nulos; votos enteros y no negativos.
- Un resultado por clave natural confirmada.
- Ratios con denominador cero son `NULL`, no infinito ni cero inventado.
- Conservar nombre fuente y normalizado por separado.
- Comparar conteos de preflight, payload, staging y SQLite.
- Investigar sumas de candidatos que superen el total de partido/mesa.
- Reportar `votantes > censo` como anomalía de fuente conservando ambos valores;
  no imputar ni excluir la mesa sin una regla oficial.

## Seguridad y ética

- Consumir solo endpoints públicos observados, con límites conservadores.
- Usar timeouts, pausa, User-Agent y logs sin secretos ni payloads completos.
- No publicar el PDF confidencial; mantenerlo fuera del repo.
- Comunicar asociación, no intención individual ni causalidad.

## Comandos de revisión

```bash
python -m unittest discover -s tests -v
python -m compileall scraper db dashboard viz outputs scripts
python scripts/quality_gate.py all
python scripts/audit_database.py

# Con dependencias de desarrollo instaladas
ruff check scraper scripts tests db
pytest --cov

python scripts/verify_delivery.py
python outputs/generar_manifest.py
python scripts/quality_gate.py release
```

`scripts/audit_database.py` es una verificación local explícitamente no oficial;
complementa el manifest contractual con evidencia de calidad más detallada.
