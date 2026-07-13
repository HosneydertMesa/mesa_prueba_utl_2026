# Dashboard HTML autocontenido

## Objetivo y alcance

El incremento 4.2 implementa los 15 puntos base del Reto 4 en un único
`dashboard/index.html`. El archivo abre directamente desde disco, no necesita
servidor y no depende de CDN, librerías, fuentes, imágenes o APIs externas.

El bonus de dark mode y exportación CSV se implementó después, como incremento
4.3 separado, y se documenta en `docs/18-bonus-dashboard.md`.

## Flujo reproducible

```bash
python dashboard/export_data.py --db db/puestos_2026_bonus.db --include-bonus
```

El comando genera `dashboard/data.json` y reemplaza atómicamente el bloque
`application/json` del HTML. Esto evita `fetch`, conserva una fuente de datos
auditable y permite abrir el archivo mediante `file://` sin problemas de CORS.

Después de regenerar, abrir `dashboard/index.html` directamente en Chrome o
Firefox. No se debe usar un servidor local para demostrar el requisito.

## Vistas implementadas

- Comparativo de votos totales CA para cuatro municipios obligatorios y tres
  bonus, con alcance visualmente identificado.
- Selector de municipio que actualiza las vistas relacionadas.
- Top 10 de candidaturas CA con votos y porcentaje municipal.
- Partido líder SE con código, nombre, votos y participación.
- Arrastre del candidato Verde `codcan=5` CA frente a `codcan=57` SE por puesto.
- Línea de referencia `1.0` y tratamiento explícito de ratios sin denominador.

Colores contractuales:

| Elemento | Color |
|---|---|
| Verde 5/57 | `#007C34` |
| Partido 87/92 | `#7B2D8B` |
| Partido 10 | `#1E477D` |
| Partido 2 | `#E07B00` |

## Decisiones de ingeniería

- Los gráficos se construyen con HTML y CSS; no se introducen librerías ni SVG
  generados manualmente.
- El exportador valida los cuatro municipios obligatorios, los tres bonus y la
  evidencia +15 antes de escribir artefactos.
- La serialización es determinista y el HTML conserva el mismo contrato JSON.
- El contenido usa lenguaje descriptivo: el arrastre es una razón observable y
  no demuestra transferencia, intención ni causalidad electoral.
- El selector tiene etiqueta accesible, las regiones tienen encabezados y el
  diseño contempla navegación por teclado y reducción de movimiento.

## Evidencia y aceptación

```bash
python -m unittest tests.integration.test_dashboard_export \
  tests.contract.test_dashboard_html -v
python -m unittest discover -s tests -v
python scripts/quality_gate.py all
```

Resultado local consolidado: 56 pruebas aprobadas, Ruff limpio, JavaScript
sintácticamente válido, auditoría 4/4 municipios y gates DEV/QA/SEC/REVIEW
verdes.

La automatización verifica:

- ausencia de recursos externos y `fetch`;
- identidad entre JSON exportado y embebido;
- 7 municipios, 104 puestos y 1.432 mesas, diferenciados por alcance;
- 6 bonus cuya suma es +15 y 1.107 mesas analíticas obligatorias;
- vistas obligatorias para cada municipio;
- colores exactos y referencia `1.0`;
- landmarks interactivos y accesibilidad básica.

La revisión manual de entrega debe abrir el archivo en Chrome y Firefox,
cambiar los siete municipios, inspeccionar el comportamiento responsive y
confirmar una consola limpia. Esta comprobación complementa los contratos; no
se sustituye por un servidor local.

La evolución suplementaria del mismo archivo está descrita en
`docs/20-dashboard-analitico-2.md`.

La organización espacial en cuatro vistas y la publicación mínima están
descritas en `docs/21-dashboard-workspace-pages.md`.
