# Dashboard Analítico 2.0

## Objetivo

La versión 2.0 convierte las salidas estáticas del Reto 5 en vistas interactivas
dentro del mismo `dashboard/index.html`. El comparativo, selector, top 10, líder,
arrastre y CSV abarcan cuatro municipios obligatorios y tres bonus. El heatmap,
scatter, colores y ratios contractuales permanecen sobre el alcance obligatorio.

No se introduce servidor, CDN, `fetch` ni librería JavaScript. El dashboard sigue
abriendo directamente mediante `file://` y no se publica en hosting para preservar
el contrato de entrega local.

## Contrato de datos v2

`dashboard/export_data.py` reutiliza las funciones auditadas de `viz/heatmap.py`
y `viz/scatter.py`. El bloque `analitica` contiene:

- matriz de porcentajes y votos del top 8 CA en cuatro municipios;
- celda máxima observada;
- 1.107 observaciones CA/SE con código de mesa y municipio;
- colores municipales;
- Pearson, pendiente, intercepto y tamaño de muestra OLS.

El contrato raíz también contiene siete municipios con `alcance`, contadores
separados y seis bonificaciones cuya suma es +15 potencial. La metadata distingue
`mesas=1432` de `mesas_analiticas=1107` para impedir una mezcla accidental.

Resultado observado:

```text
schema_version=2
heatmap=8x4
maximo=Yamit Noe Hurtado Neira · PAIPA · 28.2977%
r=0.963699
pendiente=0.933433
intercepto=13.673280
n_mesas=1107
```

## Experiencia interactiva

- Cuatro tarjetas resumen presentan asociación, pendiente, máxima participación
  y número de observaciones.
- El heatmap se renderiza como tabla HTML semántica con votos en cada tooltip.
- El scatter se dibuja con Canvas adaptable a la pantalla.
- Los botones filtran puntos por municipio y exponen estado `aria-pressed`.
- El tooltip identifica municipio, mesa, votos CA y votos SE.
- La recta continúa siendo el ajuste OLS global aunque se filtre la visualización.
- El tema oscuro redibuja el Canvas con los tokens CSS activos.
- Una sección de ingeniería presenta los seis bonus y su evidencia reproducible.

## Accesibilidad e interpretación

El Canvas expone descripción dinámica y resumen textual; el heatmap conserva
encabezados de filas y columnas. La información no depende únicamente del color.
El texto metodológico declara que asociación, residuos o puntos alejados no
demuestran causalidad, transferencia de votos ni fraude.

## Validación

```bash
python dashboard/export_data.py --db db/puestos_2026_bonus.db --include-bonus
python -m unittest tests.integration.test_dashboard_export \
  tests.contract.test_dashboard_html -v
python -m unittest discover -s tests -v
python scripts/quality_gate.py all
```

Los contratos verifican identidad JSON/HTML, siete municipios, suma bonus +15,
schema v2, matriz 8×4, 1.107 puntos, estadísticos observados, controles
interactivos y ausencia de recursos externos.
La revisión manual pendiente debe abrir el archivo en Chrome y Firefox, alternar
el tema, recorrer la tabla, filtrar cada municipio y comprobar los tooltips.
