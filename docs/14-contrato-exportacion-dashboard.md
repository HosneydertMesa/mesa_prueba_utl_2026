# Contrato de exportación del dashboard - Incremento 4.1

## Objetivo

`dashboard/export_data.py` transforma la base SQLite completa en
`dashboard/data.json` sin dependencias externas. La salida es pequeña,
determinista y contiene todo lo necesario para construir el dashboard sin volver
a consultar SQLite desde el navegador.

## Ejecución

```bash
python dashboard/export_data.py
python dashboard/export_data.py --db db/puestos_2026.db --output dashboard/data.json
```

Salida observada:

```text
DASHBOARD_EXPORT municipios=4 puestos=73 mesas=1107 json_bytes=198208 html_bytes=249578
INFO salida=dashboard\data.json html=dashboard\index.html schema_version=2
```

## Schema lógico

```text
meta
  schema_version, dataset, corporaciones
  municipios, puestos, mesas, referencia_arrastre

colores_partido
  codpar -> color hexadecimal

comparativo_ca[]
  municipio, votos_ca_total

municipios[]
  codigo, nombre, puestos, mesas
  votos_ca_total, votos_se_total
  top_candidatos_ca[10]
  lider_se
  arrastre_verde[un elemento por puesto]

analitica
  heatmap: municipios[4], candidatos[8], maximo
  scatter: puntos[1107], colores_municipio, estadisticas OLS/Pearson
```

Cada candidato CA incluye posición, `codpar`, `codcan`, nombre, partido, votos,
porcentaje sobre los votos CA a partidos del municipio y color. `SOLO POR LA
LISTA` se excluye porque no es un candidato individual.

El líder SE incluye partido, votos, participación municipal y color. El arrastre
reutiliza la consulta 3.1, por lo que mantiene `5→57`, orden por puesto y ratio
`NULL` ante denominador cero.

## Colores obligatorios

| codpar | Color |
|---:|---|
| 5 / 57 | `#007C34` |
| 87 / 92 | `#7B2D8B` |
| 10 | `#1E477D` |
| 2 | `#E07B00` |

Los demás partidos reciben `#64748B` como color neutral. Los códigos y colores
obligatorios se validan antes de escribir el archivo.

## Reproducibilidad

- No se incluye timestamp ni ruta absoluta.
- El orden municipal es Tunja, Paipa, Sogamoso y Duitama.
- Top 10 y líderes usan desempate por códigos.
- JSON se escribe como UTF-8 con LF mediante reemplazo atómico.
- Dos ejecuciones sobre la misma base producen los mismos bytes.
- Las vistas interactivas reutilizan las funciones que generan los PNG, evitando
  fórmulas paralelas entre el Reto 5 y el dashboard.

## Controles bloqueantes

- Existen los cuatro municipios requeridos.
- Metadata coincide con el detalle.
- Cada municipio tiene top 10 CA y líder SE.
- Cada puesto tiene exactamente un resultado de arrastre.
- Colores obligatorios están completos y sin cambios.
- El contrato forma parte de `scripts/audit_database.py`.

Este incremento no declara terminado el Reto 4: aún falta construir y validar
`dashboard/index.html` desde `file://`.
