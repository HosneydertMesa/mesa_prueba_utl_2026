# Scatter de votos válidos CA vs SE por mesa

## Contrato 5.2

El PDF exige un punto por mesa, color por municipio, línea OLS, coeficiente de
Pearson anotado y un stdout exacto. La unidad de análisis es la mesa electoral,
no el candidato, partido o puesto.

Para cada mesa se parean los dos registros de `resumen_mesa`:

```text
x_i = votos_validos de Cámara (CA)
y_i = votos_validos de Senado (SE)
```

`votos_validos` incluye votos por partidos y votos en blanco, pero excluye nulos
y no marcados. La misma definición se usa en ambos ejes. Si una mesa carece de
CA o SE, el script falla en vez de reducir silenciosamente la muestra.

## Modelo descriptivo

La recta se ajusta mediante mínimos cuadrados ordinarios:

```text
SE_i = intercepto + pendiente × CA_i + error_i
```

También se calcula el coeficiente de Pearson entre CA y SE. Ambos estadísticos
describen asociación dentro del mismo evento electoral; no identifican
transferencia de votos, intención individual ni causalidad.

## Resultado observado

```text
r=0.964 | pendiente=0.933 | n_mesas=1107
```

- Intercepto OLS: 13,673 votos SE.
- Tunja: 424 mesas.
- Paipa: 95 mesas.
- Sogamoso: 301 mesas.
- Duitama: 287 mesas.

La asociación lineal es alta. Una pendiente menor que uno indica que, en el
ajuste global, cada voto válido CA adicional se asocia con aproximadamente 0,933
votos válidos SE adicionales, más el intercepto. Esta lectura no es causal y
los puntos alejados de la recta no se etiquetan como anomalía o fraude.

## Ejecución

```bash
python viz/scatter.py
```

El primer y único renglón de stdout conserva exactamente:

```text
r=X.XXX | pendiente=X.XXX | n_mesas=NNN
```

El script acepta `--db` y `--output`. El PNG predeterminado se escribe en
`viz/scatter_ca_se.png` y se rechaza si pesa 10 KB o menos.

## Validación

- fixture calculable `SE = 2 × CA + 5` con Pearson 1, pendiente 2 e intercepto 5;
- una observación única por mesa y conteo de las cuatro ciudades;
- rechazo de mesas sin ambas corporaciones;
- stdout con tres decimales y n entero;
- dimensiones mínimas 1.600×1.000 y archivo superior a 10 KB;
- inspección visual de puntos, leyenda, recta, anotación, ejes y contraste.
