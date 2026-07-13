# Dashboard Workspace 3.0 y GitHub Pages

> Estado al 13 de julio de 2026: PR #10 y #11 fusionados, workflows `quality` y
> `deploy-dashboard-pages` verdes, HTTPS activo y contenido público verificado.

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
| Analítica | Selector 8×4/8×7, scatter y OLS/Pearson | 4 obligatorios o 7 ampliados |
| Bonus | Seis mejoras y +15 puntos potenciales | evidencia suplementaria |

Cada vista conserva estado compartible en el hash: vista, municipio, alcance
analítico y filtro del scatter. También acepta los fragmentos anteriores
(`#overview`, `#municipality`, `#analytics`, `#bonus`). Los botones implementan semántica de pestañas,
`aria-selected`, foco roving y navegación con flechas, Inicio y Fin.

El modo presentación recorre cuatro hallazgos preparados sin duplicar datos ni
crear rutas especiales. Se puede retroceder, avanzar, finalizar o salir con
`Esc`; cada paso reutiliza los mismos controles y queda reflejado en la URL.

En escritorio la barra lateral y el lienzo analítico ocupan el alto de la ventana;
solo el espacio activo se desplaza. En pantallas pequeñas la navegación se
convierte en una barra inferior y el contenido recupera el desplazamiento normal.
Los paneles del workspace anulan el ancho mínimo implícito de gráficos y tablas;
así, los recursos anchos desplazan su propio contenedor sin ampliar la página.

## Guardas del contrato

- Sigue existiendo un solo HTML sin CDN, recursos externos ni `fetch`.
- `file://` continúa siendo un flujo soportado y prioritario para evaluación.
- Los colores obligatorios, ratio `1.0`, dark mode y CSV no cambian.
- La vista obligatoria conserva exactamente cuatro municipios y 1.107 mesas;
  la vista suplementaria calcula por separado siete municipios y 1.432 mesas.
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
credenciales. La URL pública verificada del proyecto es:

```text
https://hosneydertmesa.github.io/mesa_prueba_utl_2026/
```

La configuración usa permisos mínimos `contents: read`, `pages: write` e
`id-token: write`, el entorno `github-pages` y concurrencia serializada. Las
Actions usan runtimes Node 24: `checkout@v7`, `configure-pages@v6`,
`upload-pages-artifact@v5` y `deploy-pages@v5`. Después del deploy, un job smoke
consulta HTML y JSON con reintentos y verifica schema v2, siete municipios,
1.432 mesas/puntos y la huella SHA-256 del contenido.

### Incidente recuperado del 13 de julio de 2026

El repositorio había quedado privado y el plan de la cuenta no soporta GitHub
Pages para repositorios privados. La configuración de Pages dejó de existir y
el job `deploy` falló con HTTP 404 aunque `build` y el artefacto estaban sanos.
Con autorización del propietario se restauró la visibilidad pública, se habilitó
Pages con origen `workflow` y la ejecución `29226541060` terminó correctamente.
La corrección evita atribuir el incidente al dashboard o relajar permisos.

## Evidencia de publicación

- URL: `https://hosneydertmesa.github.io/mesa_prueba_utl_2026/`.
- HTML: respuesta HTTPS `200`, 528.167 bytes y control `Ampliado 7` presente.
- JSON: respuesta HTTPS `200`, 7 municipios, 1.432 mesas y 1.432 puntos en el
  scatter ampliado.
- GitHub Actions: `quality` y `deploy-dashboard-pages` concluyeron `success`.
- Despliegue final: ejecución `29287276211`; `build`, `deploy` y smoke HTTPS
  concluyeron `success` sobre `main`.
- Seguridad: Pages sirve solo HTML, JSON y `.nojekyll`; HTTPS está forzado.
- QA real: recorrido guiado y URL compartible operativos, consola sin warnings ni
  errores y vista Municipio a 360 px sin desbordamiento horizontal de página.

## Validación

```bash
python dashboard/export_data.py --db db/puestos_2026_bonus.db --include-bonus
python -m unittest tests.contract.test_dashboard_html -v
python scripts/quality_gate.py all
```

Los contratos verifican las cuatro vistas, navegación por hash, semántica BI,
identidad JSON/HTML, modo presentación, procedencia y que Pages empaquete
exclusivamente los artefactos del dashboard. El smoke remoto añade evidencia
sobre el contenido realmente publicado, no solo sobre el artefacto construido.
