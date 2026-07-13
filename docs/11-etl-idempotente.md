# Parser ACT y ETL idempotente - Retos 1.2 y 2.2

## Flujo implementado

```text
nomenclator -> municipios/puestos/mesas virtuales
ACT por mesa -> parser estricto -> modelos tipados
             -> carga_log INICIADA
             -> transacción SQLite
             -> dimensiones + hechos
             -> COMPLETADA o rollback + FALLIDA
```

## Validaciones antes de persistir

- `elec` coincide con CA o SE y se selecciona la cámara correcta.
- Los balances usan los totales de esa cámara, no el agregado superior de otras circunscripciones.
- `amb` es una mesa de 19 caracteres y corresponde al puesto esperado.
- Conteos son enteros no negativos.
- Se conservan censo y votantes tal como los publica la fuente. Los casos
  `votantes > censo` se reportan como anomalía de calidad porque existen en ACT
  oficiales; no se corrigen ni se descartan silenciosamente.
- `válidos + nulos + no marcados = votantes`.
- `votos de partidos + blancos = votos válidos`.
- La suma de candidatos coincide con los votos del partido.
- No hay `codpar` ni `codcan` duplicados dentro de la mesa.
- Cada `codpar` ACT existe en el catálogo por el campo `i` del nomenclator.

## Idempotencia

Las dimensiones y hechos usan sus claves `UNIQUE` con `INSERT OR IGNORE` después de validar el payload. Si la fila existente tiene los mismos valores, se cuenta como omitida. Si la misma clave llega con votos o metadata distintos, la transacción revierte y `carga_log` queda `FALLIDA`; no se conserva silenciosamente una mezcla de versiones.

La prueba de integración ejecuta CA dos veces sobre la misma mesa:

| Ejecución | Leídas | Insertadas | Omitidas |
|---|---:|---:|---:|
| Primera | 7 | 7 | 0 |
| Segunda | 7 | 0 | 7 |

Una prueba adicional carga CA y SE en la misma mesa sin colisión.

### Smoke test con datos oficiales

Se ejecutó dos veces la primera mesa de Tunja contra respuestas ACT reales conservadas
en la caché local (la caché no se versiona):

| Ejecución | Cargas | Leídas | Insertadas | Omitidas |
|---|---:|---:|---:|---:|
| Primera | 2 (CA + SE) | 1.154 | 1.154 | 0 |
| Segunda | 2 (CA + SE) | 1.154 | 0 | 1.154 |

Después de ambas ejecuciones, `PRAGMA integrity_check` devolvió `ok`,
`PRAGMA foreign_key_check` no reportó filas y las cuatro cargas quedaron
`COMPLETADA`. Este smoke test valida el camino real sin sustituir la corrida final
de las 1.107 mesas.

## CLI

```bash
python scraper/scraper.py --preflight
python scraper/scraper.py --municipios TUNJA --limit-mesas 1
python scraper/scraper.py
```

`--limit-mesas` existe únicamente para smoke tests. La ejecución final omite el flag y recorre las 1.107 mesas, dos corporaciones y 2.214 respuestas ACT. La caché HTTP evita repetir descargas durante reejecuciones locales.

## Riesgo conocido

La estrategia actual trata un cambio de votos para una clave ya cargada como conflicto auditable. Si se decide consumir avances durante escrutinio, se requerirá una política explícita de versionado o reemplazo por snapshot; para la prueba se usa el resultado ACT publicado y estable.
