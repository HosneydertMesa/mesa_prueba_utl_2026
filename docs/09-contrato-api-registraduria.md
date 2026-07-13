# Contrato API Registraduría - Reto 1.1

## Estado y evidencia

Contrato observado el 12 de julio de 2026 (America/Bogota) sobre el portal público oficial. Se inspeccionó el HTML, el bundle JavaScript `index-QNJ0IV9k.js`, el nomenclator y respuestas ACT reales. No se versionan los payloads completos porque cambian, ocupan varios MB y la solución debe poder regenerarlos.

## Base y rutas

Base URL:

```text
https://resultadospreccongreso2026.registraduria.gov.co
```

| Uso | Método y patrón |
|---|---|
| Configuración | `GET /json/web/config.json` |
| Nomenclator | `GET /json/nomenclator.json` |
| Resultado vigente | `GET /json/ACT/{SE|CA}/{scope_code}.json` |
| Resultado inicial | `GET /json/INI/{SE|CA}/IN_{scope_code}.json` |
| Histórico | `GET /json/HIST/{department}/{SE|CA}/{type}_{advance}/{scope_code}.json` |
| Estadística | `GET /json/EST/{SE|CA}/EST_{stat}.json` |

Para la prueba se usará ACT. `config.json` reportó `source: "act"`, portal abierto, polling activo y nomenclator versión 1.

## Nomenclator

El documento contiene:

- `ver`: versión del nomenclator.
- `y`: año electoral.
- `elec`: elecciones; `SE -> elec 1`, `CA -> elec 2`.
- `levels`: niveles 1-7, desde país hasta mesa.
- `amb`: jerarquía por elección con códigos, padres, hijos y número de mesas.
- `partidos`: catálogo de partidos/candidaturas.

Campos territoriales relevantes: `i` identificador interno, `n` nombre, `c` código, `l` nivel, `m` número de mesas, `p` padres, `h` hijos y `r` referencias internas.

## Municipios verificados

| Municipio | Código | Puestos | Mesas CA | Mesas SE |
|---|---:|---:|---:|---:|
| Tunja | `0700001` | 26 | 424 | 424 |
| Paipa | `0700181` | 7 | 95 | 95 |
| Sogamoso | `0700277` | 18 | 301 | 301 |
| Duitama | `0700079` | 22 | 287 | 287 |

Los conteos del nomenclator coinciden con `totales.act.metota` y `totales.act.mesesc` de las ocho respuestas municipales CA/SE verificadas.

## Códigos de ámbito

- Municipio: 7 caracteres, por ejemplo Tunja `0700001`.
- Puesto: 13 caracteres, por ejemplo `0700001010001`.
- Mesa: puesto + número de mesa con 6 dígitos; mesa 1: `0700001010001000001`.
- Resultado de mesa CA: `/json/ACT/CA/0700001010001000001.json`.

La mesa no aparece como registro físico del nomenclator: es un nivel virtual derivado de `m`, el número de mesas del puesto.

## Campos JSON de resultados

Se verificaron más de ocho campos utilizables:

| Campo | Interpretación operativa |
|---|---|
| `elec` | código de elección: `1` SE, `2` CA |
| `amb` | código territorial consultado |
| `dept` | código de departamento (`07` Boyacá) |
| `mdhm` | marca temporal compacta de actualización |
| `totales.act.metota` | mesas totales del ámbito |
| `totales.act.mesesc` | mesas escrutadas |
| `totales.act.centota` | censo total |
| `camaras[].totales.act.votant` | votantes de la cámara seleccionada |
| `camaras[].totales.act.votnul` | votos nulos de la cámara |
| `camaras[].totales.act.votnma` | votos no marcados de la cámara |
| `camaras[].totales.act.votbla` | votos en blanco de la cámara |
| `camaras[].cam` | cámara/circunscripción dentro de la elección |
| `partotabla[].act.codpar` | código de partido |
| `partotabla[].act.vot` | votos del partido |
| `cantotabla[].codcan` | código de candidato |
| `cantotabla[].cedula` | identificador publicado del candidato |
| `cantotabla[].nomcan` / `apecan` | nombres y apellidos |
| `cantotabla[].vot` | votos del candidato en el ámbito |
| `cantotabla[].pref` | indicador de voto preferente/lista |

Todos los conteos llegan como strings; porcentajes usan coma decimal y `%`. El parser debe convertir conteos explícitamente y conservar el valor fuente cuando se necesite auditoría.

Los totales superiores pueden agregar varias cámaras/circunscripciones. Las invariantes de partido deben compararse contra `camaras[].totales.act` de la cámara seleccionada; el censo `centota` se toma del total superior porque no aparece repetido en la cámara.

Aunque `cedula` aparece publicada en la respuesta, no se persistirá por defecto: los retos pueden resolverse con `codcan`, `codpar`, nombres y votos. Esta minimización evita almacenar un identificador que no aporta al objetivo analítico.

## Cabeceras y acceso

No se observó autenticación, API key, bearer token ni cookie previa obligatoria. Las respuestas públicas funcionan por GET directo. El cliente enviará:

```text
Accept: application/json
User-Agent: utl-electoral-pipeline/1.0 (contacto en README)
```

Además usará timeout explícito, cache local, retry limitado con backoff y concurrencia conservadora. La aplicación oficial solicita ACT con política `cache: no-store`.

## Fallback y control de cambios

1. Descargar y validar primero nomenclator/config.
2. Si ACT falla, usar `sample_data` oficial sin cambiar el parser de dominio.
3. Registrar fecha, URL, status, ETag y checksum de cada fuente.
4. Detectar cambios comparando `versionNomenclator`, claves obligatorias y conteos.
5. No interpretar un 404 como municipio sin votos: revisar extensión `.json`, código y versión.

## Implementación asociada

`scraper/nomenclator.py` resuelve municipios, recorre puestos, calcula mesas y construye URLs ACT. Sus pruebas usan un fixture mínimo con la misma forma del contrato, sin depender de red.

El incremento 1.2a añade `scraper/http_client.py` y `scraper/scraper.py`: cliente JSON con caché atómica, timeout y retry/backoff, más `--preflight` local o remoto. La descarga de ACT y la persistencia idempotente pertenecen al incremento 1.2b.
