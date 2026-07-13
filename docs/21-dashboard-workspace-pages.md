# Dashboard Workspace 3.0 y GitHub Pages

## Objetivo

El incremento 4.5 reemplaza la navegación vertical tipo landing por un workspace
analítico inspirado en herramientas BI, sin convertir el proyecto en una SPA ni
romper el requisito de un único `dashboard/index.html` autocontenido.

## Arquitectura de información

La interfaz se divide en cuatro vistas activadas desde una navegación persistente:

| Vista | Contenido | Alcance |
|---|---|---|
| Resumen | Cobertura y comparativo territorial CA | 4 obligatorios + 3 bonus |
| Municipio | Top 10 CA, líder SE, CSV y arrastre por puesto | municipio seleccionado |
| Analítica | Hallazgos, heatmap 8×4 y scatter OLS/Pearson | 4 obligatorios, 1.107 mesas |
| Bonus | Seis mejoras y +15 puntos potenciales | evidencia suplementaria |

Cada vista conserva un fragmento de URL (`#overview`, `#municipality`,
`#analytics`, `#bonus`). Los botones implementan semántica de pestañas,
`aria-selected`, foco roving y navegación con flechas, Inicio y Fin.

En escritorio la barra lateral y el lienzo analítico ocupan el alto de la ventana;
solo el espacio activo se desplaza. En pantallas pequeñas la navegación se
convierte en una barra inferior y el contenido recupera el desplazamiento normal.

## Guardas del contrato

- Sigue existiendo un solo HTML sin CDN, recursos externos ni `fetch`.
- `file://` continúa siendo un flujo soportado y prioritario para evaluación.
- Los colores obligatorios, ratio `1.0`, dark mode y CSV no cambian.
- Los siete municipios se muestran, pero ML/OLS y heatmap conservan exactamente
  cuatro municipios y 1.107 mesas.
- Cambiar de vista no recalcula datos; solo controla presentación y redibuja el
  Canvas al abrir la vista analítica.

## Publicación en GitHub Pages

`.github/workflows/pages.yml` despliega desde `main` mediante GitHub Actions. El
artefacto público contiene únicamente:

```text
index.html
data.json
.nojekyll
```

No se publica la base SQLite, el PDF, el scraper, documentación interna ni
credenciales. El sitio esperado del proyecto es:

```text
https://hosneydertmesa.github.io/mesa_prueba_utl_2026/
```

La configuración usa permisos mínimos `contents: read`, `pages: write` e
`id-token: write`, el entorno `github-pages` y concurrencia serializada. La
activación del sitio es una operación administrativa separada de la revisión del
código; el despliegue ocurre al fusionar el PR a `main`.

## Validación

```bash
python dashboard/export_data.py --db db/puestos_2026_bonus.db --include-bonus
python -m unittest tests.contract.test_dashboard_html -v
python scripts/quality_gate.py all
```

Los contratos verifican las cuatro vistas, navegación por hash, semántica BI,
identidad JSON/HTML y que Pages empaquete exclusivamente los artefactos del
dashboard.
