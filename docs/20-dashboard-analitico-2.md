# Dashboard Analítico 2.0

## Objetivo

La versión 2.0 convierte las salidas estáticas del Reto 5 en vistas interactivas
dentro del mismo `dashboard/index.html`. El comparativo, selector, top 10, líder,
arrastre y CSV abarcan cuatro municipios obligatorios y tres bonus. Heatmap y
scatter permiten alternar entre el contrato obligatorio y el alcance ampliado;
los valores oficiales permanecen disponibles sin modificación.

No se introduce servidor, CDN, `fetch` ni librería JavaScript. El dashboard sigue
abriendo directamente mediante `file://`; la publicación activa en GitHub Pages
sirve el mismo artefacto estático y no reemplaza el contrato local.

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

`analitica` conserva `heatmap` y `scatter` como contrato obligatorio y añade
`ampliada` con siete municipios. El dashboard abre en ampliado, pero ofrece un
selector explícito para comparar ambos universos.

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

Resultado suplementario ampliado:

```text
heatmap=8x7
r=0.957094
pendiente=0.938568
intercepto=11.607821
n_mesas=1432
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
- El selector de alcance regenera tarjetas, heatmap, filtros, recta OLS y
  tooltips con los datos del universo elegido.
- El modo presentación guía cuatro hallazgos y puede abandonarse sin recargar.
- Vista, municipio, alcance y filtro del scatter se serializan en una URL
  compartible, con compatibilidad hacia atrás para los hashes simples.
- La franja de procedencia muestra fuente, alcance, carácter local no oficial,
  anomalías conservadas y una huella SHA-256 reproducible del contenido.

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
schema v2, matrices 8×4/8×7, 1.107/1.432 puntos, estadísticos separados,
controles interactivos, presentación, estado compartible, procedencia y ausencia
de recursos externos.
La revisión manual pendiente debe abrir el archivo en Chrome y Firefox, alternar
el tema, recorrer la tabla, filtrar cada municipio y comprobar los tooltips.

La evolución espacial y su despliegue están documentados en
`docs/21-dashboard-workspace-pages.md`.
