# Heatmap de candidaturas CA por municipio

## Contrato 5.1

El PDF exige `viz/heatmap_municipios.png` con ocho filas, cuatro columnas,
valores porcentuales y anotaciones. Las columnas se mantienen en el orden
Tunja, Paipa, Sogamoso y Duitama.

Las filas se seleccionan por votación CA consolidada en los cuatro municipios:

```text
top_8 = ORDER BY SUM(votos_candidato_CA) DESC, codpar, codcan LIMIT 8
```

El desempate por `codpar` y `codcan` hace el resultado determinista. Se excluyen
los registros de lista (`es_lista=1`) porque el contrato solicita candidatos.

## Fórmula

Para el candidato `i` y municipio `j`:

```text
porcentaje_ij = 100 × votos_candidato_CA_ij / votos_partido_CA_totales_j
```

El denominador es la suma de `resultados_partido` CA en el municipio, la misma
definición de votos CA totales usada por el dashboard. Un denominador ausente o
no positivo detiene el proceso; no se imputa cero ni se fabrica un porcentaje.

## Ranking consolidado observado

| Pos. | Candidatura | CA partido/candidato | Votos 4 municipios |
|---:|---|---|---:|
| 1 | Héctor David Chaparro Chaparro | 2/106 | 13.861 |
| 2 | Yamit Noé Hurtado Neira | 5/106 | 11.206 |
| 3 | Jaime Raúl Salamanca Torres | 5/101 | 9.406 |
| 4 | Ramiro Barragán Adame | 5/105 | 8.936 |
| 5 | Fabián Camilo Rojas Barrera | 122/102 | 5.121 |
| 6 | Wilder Iván Suesca Ochoa | 121/106 | 4.913 |
| 7 | Ingrid Marlen Sogamoso Alfonso | 121/101 | 4.855 |
| 8 | Eduar Alexis Triana Rincón | 10/102 | 4.440 |

El máximo de la matriz es 28,3% para Yamit Noé Hurtado Neira en Paipa. Es un
resultado descriptivo de participación municipal, no evidencia causal ni una
comparación de poblaciones con igual tamaño.

## Ejecución y salida

```bash
python viz/heatmap.py
```

Salida observable:

```text
HEATMAP candidatos=8 municipios=4 bytes=<N>
INFO salida=viz/heatmap_municipios.png criterio=top_8_votos_ca_consolidados metrica=porcentaje_total_ca_municipal
```

El script permite `--db` y `--output` para pruebas aisladas. La salida por
defecto se rechaza si no supera 10 KB.

## Validación

- fixture manual con nueve candidatos para comprobar ranking y exclusión;
- matriz exacta 8×4 y porcentaje conocido de 9,0%;
- rechazo cuando falta uno de los cuatro municipios;
- dimensiones mínimas 1.600×1.000 y archivo superior a 10 KB;
- inspección visual de nombres, anotaciones, escala, ejes y contraste.
