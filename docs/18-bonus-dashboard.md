# Bonus de interfaz del dashboard

## Alcance

El incremento 4.3 añade los dos bonus de interfaz sin modificar los datos ni los
15 puntos base del dashboard:

- modo oscuro mediante CSS custom properties: +3 puntos potenciales;
- botón funcional para exportar CSV: +2 puntos potenciales.

Este incremento llevó inicialmente el proyecto a +12. Con el bonus municipal
implementado después, el total alcanza **+15/+15 puntos potenciales**. La
valoración final corresponde al evaluador.

## Modo oscuro

El documento define los tokens visuales en `:root` y sus valores alternativos en
`html[data-theme="dark"]`. El botón expone `aria-pressed` y una etiqueta que
describe la acción disponible. Al iniciar se aplica, en este orden:

1. la preferencia guardada en `localStorage` con clave `utl-dashboard-theme`;
2. la preferencia del sistema `prefers-color-scheme`;
3. el tema claro como fallback seguro.

El acceso a almacenamiento está protegido para que una restricción del navegador
no impida abrir el dashboard directamente mediante `file://`.

## Exportación CSV

El botón exporta el municipio seleccionado en ese momento. El archivo incluye:

- las diez candidaturas CA mostradas en el ranking;
- el partido líder agregado de Senado;
- todas las filas de arrastre Verde por puesto del municipio.

El schema estable es:

```text
tipo,municipio,posicion,codpar,codcan,nombre,partido,puesto_codigo,puesto,votos,porcentaje,votos_ca_verde,votos_se_verde,ratio_arrastre
```

La generación ocurre enteramente en el navegador con `Blob`, MIME
`text/csv;charset=utf-8`, BOM UTF-8 y escape RFC 4180 para comas, comillas y
saltos de línea. El nombre sigue `dashboard-<municipio>.csv`. No existe `fetch`,
backend, CDN ni dependencia externa.

## Validación

```bash
python -m unittest tests.contract.test_dashboard_html \
  tests.integration.test_dashboard_export -v
python -m unittest discover -s tests -v
python scripts/quality_gate.py all
```

Los contratos comprueban la declaración del tema oscuro, controles accesibles,
persistencia local, creación del `Blob`, MIME, BOM, nombre descargable y columna
`ratio_arrastre`. La revisión manual final debe alternar ambos temas y descargar
un CSV para cada uno de los cuatro municipios desde Chrome y Firefox.

## Relación con el bonus municipal

El scraper fue extendido posteriormente a tres municipios adicionales de Boyacá
(+3 potencial). Su evidencia permanece separada en
`docs/19-bonus-municipios-boyaca.md`, sin modificar el dashboard contractual.
