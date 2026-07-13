# Manifest contractual y datos de muestra

## Decisión

El paquete recibido contenía únicamente `Prueba Analista de Datos .pdf`. La
revisión de las siete páginas y de la estructura interna del PDF confirmó que no
había ZIP ni archivos adjuntos embebidos.

La interpretación aplicable es:

| Evidencia del PDF | Interpretación implementada |
|---|---|
| Página 2: editar `META`, ejecutar `outputs/generar_manifest.py` y subir `evaluation_manifest.json` | El candidato debe entregar y ejecutar el generador |
| Página 4: los tres archivos de `outputs/` son obligatorios | Se generan y versionan; su ausencia activa la penalización estructural |
| Página 5: el manifest valida conteos, tablas y líder SE | El generador consulta SQLite y registra esos controles |
| Páginas 5-6: captura SQL 3.x y stdout del scatter | El manifest ejecuta las tres consultas y calcula Pearson/OLS |
| Página 4: `sample_data/` son «datos de muestra provistos» | No fueron recibidos; se incluyen capturas reales propias con procedencia explícita |

No existe una frase que indique que `generar_manifest.py` o el ejemplo serían
suministrados. Esperarlos dejaba tres archivos obligatorios ausentes. Tampoco era
correcto presentar capturas propias como archivos oficiales. La solución separa
claramente obligación, procedencia y limitación.

## Datos de muestra

`sample_data/candidate_captured/` contiene:

- `nomenclator_boyaca_sample.json`: subconjunto real para Tunja, Paipa,
  Sogamoso y Duitama;
- `act_ca_tunja_mesa_001.json`: resultado real CA de una mesa;
- `act_se_tunja_mesa_001.json`: resultado real SE de la misma mesa;
- `provenance.json`: URL, ETag, fecha de captura, bytes, SHA-256 y transformación.

Los payloads se extrajeron de la caché creada por `JsonHttpClient`. El
nomenclátor se reduce de forma mecánica a los cuatro municipios y a los partidos
referenciados por las dos respuestas ACT. Las respuestas ACT conservan la
estructura y valores necesarios para los retos; se elimina `cedula` por
minimización de datos y se reserializan como JSON UTF-8 compacto y determinista. Por eso la
procedencia declara:

```text
provenance=candidate_captured_from_public_api_cache
official_utl_sample=false
```

Regeneración opcional desde una caché que contenga exactamente las fuentes
registradas:

```bash
python scripts/export_sample_data.py
```

La prueba `tests/integration/test_sample_data.py` recalcula hashes, resuelve el
municipio/puesto, carga CA y SE mediante el ETL real y ejecuta la integridad de
SQLite.

## Generador y contrato JSON

`outputs/generar_manifest.py` mantiene la sección `META` solicitada en el PDF:

```python
META = {
    "nombre": "Hosneydert Mesa",
    "email": "hosneydert92@gmail.com",
    "repositorio": "https://github.com/HosneydertMesa/mesa_prueba_utl_2026",
}
```

El generador produce dos archivos:

- `evaluation_manifest.json`: evidencia real de la base contractual;
- `evaluation_manifest.example.json`: ejemplo compacto del mismo schema.

El resultado contiene:

- procedencia del generador y estado global;
- alcance 4/4, 1.107 mesas y CA/SE;
- SHA-256, tamaño, conteos, integridad, cobertura y calidad de SQLite;
- partido líder SE para cada municipio;
- resultado, columnas, filas y muestra de SQL 3.1, 3.2 y 3.3;
- existencia, tamaño y hash del dashboard y PNG;
- Pearson, OLS, `n_mesas` y stdout contractual;
- verificación de procedencia y hashes de `sample_data`.

La salida observada es:

```text
4/4 municipios | mesas=1107
SQL OK 3.1 | filas=73
SQL OK 3.2 | filas=3780
SQL OK 3.3 | filas=5
r=0.964 | pendiente=0.933 | n_mesas=1107
MANIFEST OK | salida=outputs\evaluation_manifest.json
```

El JSON se escribe atómicamente, con claves ordenadas y sin timestamp de
generación variable. `source_data_updated_at` procede de `carga_log`, por lo que
repetir el comando sobre la misma base produce el mismo contenido.

## Ejecución y puertas

```bash
python outputs/generar_manifest.py
python -m unittest discover -s tests -v
python scripts/quality_gate.py release
```

RELEASE verifica la presencia de todos los archivos, carga el manifest y exige:

- `overall_status=OK`;
- metadata completa;
- cobertura `4/4`;
- SQL `OK` para 3.1, 3.2 y 3.3;
- muestras verificadas;
- formato exacto del stdout del scatter.

No se debe editar `evaluation_manifest.json` manualmente. Ante un error se
corrige la fuente —base, SQL, artefacto o muestra— y se regenera.

## Compatibilidad con un eventual paquete UTL

Si posteriormente se recibe material adicional, debe guardarse intacto en una
ruta separada, registrar su SHA-256 y comparar su contrato con esta
implementación. No se sobrescribirán las capturas ni se cambiará retroactivamente
su procedencia. Si el evaluador oficial exigiera un schema distinto, se adaptará
el generador conservando esta evidencia como versión 1.
