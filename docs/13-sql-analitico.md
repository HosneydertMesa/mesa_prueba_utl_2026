# SQL analítico - Reto 3

## Contrato

Las tres consultas se ejecutan sobre los cuatro municipios combinados y usan
orden determinista. No modifican la base.

- `tarea_3_1.sql`: ratio Verde SE/CA por puesto, con `5→57` y denominador cero
  representado como `NULL`.
- `tarea_3_2.sql`: candidatos individuales de CA o SE cuya concentración es
  estrictamente mayor que `0.60`; se excluye `SOLO POR LA LISTA`.
- `tarea_3_3.sql`: atribución por mesa y top 5 consolidado mediante
  `A_ij=(votos_cand/votos_partido_CA)×votos_SE_partido`.

## Homologación para la atribución

La prueba sólo fija explícitamente `5→57`, pero la atribución consolidada requiere
resolver las demás colectividades. Se contrastaron los nombres reales de la base
con el [modelo de referencia citado por el enunciado](https://github.com/willamaya/Insidencia-Electoral/blob/main/config/homologacion_partidos.csv):

| CA | SE | Peso |
|---:|---:|---:|
| 5 | 57 | 1.0 |
| 87 | 92 | 1.0 |
| 10 | 10 | 1.0 |
| 2 | 2 | 1.0 |
| 121 | 3 | 0.5 |
| 121 | 17 | 0.5 |
| 122 | 44 | 1.0 |
| 137 | 44 | 1.0 |
| 120 | 9 | 1.0 |

`codpar_CA=15` no tiene homologación publicada y queda fuera de 3.3. No se le
asigna un partido Senado por similitud de nombre. Los pesos `0.5` evitan atribuir
dos veces el total a la coalición CA `121`.

## Evidencia calculable

El fixture de integración contiene una mesa donde Alianza Verde obtiene 40 votos
CA, 45 votos SE y una candidata obtiene 30 votos CA:

- 3.1: `45/40 = 1.125`.
- 3.2: `30/40 = 0.75`, por tanto supera `0.60`; al cambiarla a `24/40`, queda
  excluida porque el umbral es estricto.
- 3.3: `(30/40)×45 = 33.75` votos SE atribuidos.

## Resultados de la base completa

| Consulta | Filas | Tiempo local observado |
|---|---:|---:|
| 3.1 | 73 | 0,009 s |
| 3.2 | 3.780 | 0,536 s |
| 3.3 | 5 | 0,063 s |

Top 5 de atribución SE consolidada:

| Pos. | Candidato CA | codpar | Votos CA | Atribución SE |
|---:|---|---:|---:|---:|
| 1 | Yamit Noé Hurtado Neira | 5 | 11.206 | 9.670,753632 |
| 2 | Jaime Raúl Salamanca Torres | 5 | 9.406 | 9.586,687851 |
| 3 | Ramiro Barragán Adame | 5 | 8.936 | 9.415,791702 |
| 4 | Héctor David Chaparro Chaparro | 2 | 13.861 | 7.749,201165 |
| 5 | Eduar Alexis Triana Rincón | 10 | 4.440 | 6.647,953080 |

## Interpretación y bonus 3.3

El top de votos CA no tiene por qué coincidir con el top de atribución SE. Héctor
David Chaparro lidera el voto CA directo con 13.861 votos, pero Yamit Noé Hurtado
lidera la atribución. La segunda métrica pondera, mesa por mesa, la participación
del candidato dentro de su partido por el desempeño Senado de la colectividad
homologada. Por eso importa dónde se concentra el voto y cómo rinde el partido SE,
no sólo el total CA del candidato.

La atribución es una regla determinística descriptiva; no prueba que una persona
haya causado votos de Senado ni identifica intención individual.
