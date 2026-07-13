# Bonus de municipios adicionales de Boyacá

## Objetivo y aislamiento

El bonus B6 extiende el scraper sin alterar los cuatro municipios obligatorios.
La ejecución normal sigue procesando Tunja, Paipa, Sogamoso y Duitama en
`db/puestos_2026.db`. La opción `--incluir-bonus` añade tres municipios y escribe
una base separada cuando se usa el comando recomendado.

Esta separación evita que la ampliación cambie los resultados SQL, las
visualizaciones o el futuro manifest calculados sobre el alcance base. El
dashboard 2.0 consume explícitamente la base ampliada, etiqueta esos tres
municipios como bonus y mantiene su analítica sobre el alcance obligatorio.

## Criterio de selección

El nomenclátor oficial contiene 123 municipios de Boyacá. Se eligieron los tres
municipios no obligatorios con mayor cantidad de mesas y cobertura CA/SE idéntica:

| Municipio | Código | Puestos | Mesas CA | Mesas SE |
|---|---|---:|---:|---:|
| Chiquinquirá | `0700067` | 12 | 139 | 139 |
| Puerto Boyacá | `0700214` | 14 | 125 | 125 |
| Moniquirá | `0700160` | 5 | 61 | 61 |
| **Bonus** |  | **31** | **325** | **325** |

Junto con los cuatro municipios base, el alcance ampliado tiene 7 municipios,
104 puestos, 1.432 mesas y 2.864 respuestas ACT.

## Ejecución reproducible

```bash
python scraper/scraper.py --preflight --incluir-bonus
python scraper/scraper.py --incluir-bonus --db db/puestos_2026_bonus.db
python scripts/audit_database.py --db db/puestos_2026_bonus.db \
  --output outputs/auditoria_bonus_local.json --require-bonus
python dashboard/export_data.py --db db/puestos_2026_bonus.db --include-bonus
```

El parser ya no usa una lista cerrada para `--municipios`: normaliza y elimina
duplicados, mientras el resolver del nomenclátor valida pertenencia a Boyacá,
existencia en CA/SE y equivalencia de código, puestos y mesas. El flag agrega los
tres nombres de forma determinista.

## Evidencia observada

```text
PREFLIGHT 7/7 municipios | puestos=104 | mesas=1432 | solicitudes_ACT=2864
AUDITORIA ok=True municipios_obligatorios=4/4 municipios_bonus=3/3 mesas=1432/1432 resultados=2864/2864 anomalias_censo=66
SCRAPER mesas=1432 cargas=2864 leidas=1652528 insertadas=0 omitidas=1652528
```

La auditoría reportó integridad SQLite `ok`, cero violaciones FK, cero balances
inválidos, ambas corporaciones en todas las mesas y las tres consultas SQL
ejecutadas correctamente. Las 66 observaciones `votantes > censo` se conservan
como anomalías de fuente, con el mismo tratamiento no imputativo del alcance base.

## Controles

- fixture offline con los siete municipios y ambas corporaciones;
- selección bonus determinista, normalizada y sin duplicados;
- rechazo de nombres fuera de Boyacá por el nomenclátor;
- preflight real sin escritura de base ni descarga ACT;
- carga completa en base ignorada por Git;
- auditoría versionable en `outputs/auditoria_bonus_local.json`;
- segunda corrida completa con cero inserciones.

Los puntos son potenciales y su asignación final corresponde al evaluador.
