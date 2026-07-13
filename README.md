# MESA — Prueba Técnica UTL Senado 2026

> Estado: retos 1-5 y manifest contractual implementados; 100/100 base potencial.
> Desarrollo incremental con gates DEV, QA, SEC, REVIEW y validación en CI.

## Candidato

- Nombre: Hosneydert Mesa
- Email: hosneydert92@gmail.com
- Repositorio público: https://github.com/HosneydertMesa/mesa_prueba_utl_2026
- Dashboard público: https://hosneydertmesa.github.io/mesa_prueba_utl_2026/
- Plan maestro: [docs/00-plan-maestro.md](docs/00-plan-maestro.md)

## Instalación

Requisito previsto: Python 3.11 o 3.12.

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt -r requirements-dev.txt
```

El paquete recibido contenía únicamente el PDF. Por ello, `sample_data/` incluye
capturas reproducibles de la API pública con procedencia y SHA-256, mientras
`outputs/generar_manifest.py` implementa el contrato observable descrito en el
PDF. Ninguno se presenta como archivo oficial suministrado por la UTL.
La decisión y el schema están documentados en
[docs/24-manifest-y-sample-data.md](docs/24-manifest-y-sample-data.md).

## Pipeline de ejecución

Pipeline implementado hasta la auditoría local de cobertura:

```bash
# Comando literal del PDF; delega en scraper/scraper.py
python scraper.py --preflight
python scraper.py

# Punto de entrada canónico, con las mismas opciones
python scraper/scraper.py --preflight
python scraper/scraper.py --preflight --municipios TUNJA PAIPA
python scraper/scraper.py
python scripts/audit_database.py

# Bonus: base separada con siete municipios
python scraper/scraper.py --preflight --incluir-bonus
python scraper/scraper.py --incluir-bonus --db db/puestos_2026_bonus.db
python scripts/audit_database.py --db db/puestos_2026_bonus.db \
  --output outputs/auditoria_bonus_local.json --require-bonus

# SQL analítico: las tres tareas también se validan en la auditoría
python dashboard/export_data.py --db db/puestos_2026_bonus.db --include-bonus
# Abrir dashboard/index.html directamente en el navegador

# Artefactos y verificación final
python viz/heatmap.py
python viz/scatter.py
python outputs/generar_manifest.py
python scripts/verify_delivery.py
python scripts/quality_gate.py release
```

`--preflight` valida cobertura sin descargar mesas. La ejecución sin el flag descarga CA/SE por mesa, valida el payload y carga SQLite de forma idempotente. Para smoke tests puede usarse `--limit-mesas 1`; la entrega final debe omitirlo.

El schema normalizado, las claves de idempotencia y los índices están documentados en [docs/10-schema-sqlite.md](docs/10-schema-sqlite.md).

El parser, las invariantes y la prueba de doble ejecución están en [docs/11-etl-idempotente.md](docs/11-etl-idempotente.md).

La implementación, homologación y resultados del Reto 3 están en
[docs/13-sql-analitico.md](docs/13-sql-analitico.md).

El contrato SQLite→JSON del dashboard está documentado en
[docs/14-contrato-exportacion-dashboard.md](docs/14-contrato-exportacion-dashboard.md).

La implementación y validación del dashboard autocontenido están documentadas
en [docs/15-dashboard-html.md](docs/15-dashboard-html.md).

La evolución interactiva con hallazgos, heatmap y scatter está documentada en
[docs/20-dashboard-analitico-2.md](docs/20-dashboard-analitico-2.md).

La navegación espacial tipo BI y la publicación controlada mediante GitHub Pages
están documentadas en
[docs/21-dashboard-workspace-pages.md](docs/21-dashboard-workspace-pages.md).
La interfaz incluye modo presentación, filtros compartibles por URL y procedencia
visible con huella SHA-256, sin añadir servidor ni dependencias de red.

Los pendientes de entrega y las mejoras opcionales priorizadas están en
[docs/22-hoja-ruta-mejoras.md](docs/22-hoja-ruta-mejoras.md).

El criterio, la fórmula y la validación del heatmap 8×4 están documentados en
[docs/16-heatmap-municipios.md](docs/16-heatmap-municipios.md).

El pareo por mesa, OLS, Pearson y contrato stdout del scatter están documentados
en [docs/17-scatter-ca-se.md](docs/17-scatter-ca-se.md).

La selección, carga e idempotencia de los tres municipios adicionales están en
[docs/19-bonus-municipios-boyaca.md](docs/19-bonus-municipios-boyaca.md).

La secuencia y criterios de salida están en [docs/06-runbook-entrega.md](docs/06-runbook-entrega.md). Cada incremento debe pasar la metodología local [DEV → QA → SEC → REVIEW](docs/08-metodologia-sdlc.md) mediante `python scripts/quality_gate.py all`.


## API

- Portal: `https://resultadospreccongreso2026.registraduria.gov.co`.
- Nomenclator: `GET /json/nomenclator.json`.
- Resultados: `GET /json/ACT/{SE|CA}/{scope_code}.json`.
- Códigos: Tunja `0700001`, Paipa `0700181`, Sogamoso `0700277`, Duitama `0700079`.
- Mesa: código de puesto de 13 caracteres + número de mesa en 6 dígitos.
- Acceso público sin autenticación; se recomienda `Accept: application/json`, User-Agent identificable, timeout y backoff.
- Campos verificados: `elec`, `amb`, `dept`, `mdhm`, `metota`, `mesesc`, `centota`, `votant`, `codpar`, `codcan`, `nomcan`, `apecan`, `vot` y `pref`, entre otros.
- Contrato, evidencias, jerarquía y fallback: [docs/09-contrato-api-registraduria.md](docs/09-contrato-api-registraduria.md).

Si la API no responde durante la ejecución, se usarán las capturas trazables de
`sample_data/candidate_captured/` y se documentará el intento, sin cambiar el
modelo de dominio ni atribuir esas muestras a la UTL.


## Municipios en la BD

La corrida completa validada contiene los cuatro municipios y ambas corporaciones:

| Municipio | Puestos | Mesas | CA | SE |
|---|---:|---:|---:|---:|
| Tunja | 26 | 424 | 424 | 424 |
| Paipa | 7 | 95 | 95 | 95 |
| Sogamoso | 18 | 301 | 301 | 301 |
| Duitama | 22 | 287 | 287 | 287 |

La base local `db/puestos_2026.db` se excluye de Git por tamaño. La auditoría
reproducible y versionable está en `outputs/auditoria_local.json`. Las bases se
distribuyen en el Release público
[`data-v1.0.0`](https://github.com/HosneydertMesa/mesa_prueba_utl_2026/releases/tag/data-v1.0.0):

```bash
gh release download data-v1.0.0 --pattern puestos_2026.db --dir db
gh release download data-v1.0.0 --pattern puestos_2026_bonus.db --dir db
```

| Asset | Alcance | Tamaño | SHA-256 |
|---|---|---:|---|
| `puestos_2026.db` | 4 municipios · 1.107 mesas | 67.227.648 bytes | `19B017DD003654A086D44080F01ACF817BC65947965B6A1E84D864FFF25BD553` |
| `puestos_2026_bonus.db` | 7 municipios · 1.432 mesas | 86.376.448 bytes | `A72C4EBB1D4ACC6EE5DDB8E64383D81E69465C7AE6BEBAA9B5353D3FF27CFF82` |

El ensayo independiente desde clon limpio está registrado en
[docs/23-evidencia-cierre-reproducibilidad.md](docs/23-evidencia-cierre-reproducibilidad.md).

## Hallazgos principales

- Cobertura: 1.107/1.107 mesas y 2.214/2.214 resultados CA/SE.
- Partido líder agregado en SE dentro de los cuatro municipios: Pacto Histórico
  Senado (`codpar=92`), con 53.700 votos.
- Candidato líder agregado en SE: John Edickson Amaya Rodriguez
  (`codpar=57`, `codcan=5`), con 14.036 votos.
- El candidato con más votos CA es Héctor David Chaparro Chaparro (13.861),
  mientras el primer lugar por atribución SE es Yamit Noé Hurtado Neira
  (9.670,753632 votos atribuidos). Son métricas diferentes.
- La fuente presenta 53 registros CA/SE con `votantes > censo`. Se conservan y
  reportan sin imputación; los balances de votos, partidos y candidatos sí son
  consistentes en toda la base.
- En el heatmap, Yamit Noé Hurtado Neira registra la mayor participación de una
  celda: 28,3% de los votos CA de Paipa. El ranking de filas es consolidado en
  los cuatro municipios, por lo que no equivale al top individual de cada ciudad.
- Los votos válidos CA y SE por mesa presentan una asociación lineal alta
  (`r=0,964`, pendiente OLS `0,933`, `n=1.107`). Es una relación descriptiva del
  mismo evento electoral y no demuestra transferencia ni causalidad.
- En el alcance ampliado de siete municipios la asociación sigue siendo alta
  (`r=0,957`, pendiente OLS `0,939`, `n=1.432`); es una vista suplementaria y no
  sustituye los valores contractuales anteriores.

Son hallazgos descriptivos del alcance cargado, no evidencia causal. La estrategia
analítica está en [docs/04-estrategia-analitica-ml.md](docs/04-estrategia-analitica-ml.md).
El dictamen de rigor, riesgos y mejoras priorizadas está en
[docs/25-auditoria-ciencia-datos.md](docs/25-auditoria-ciencia-datos.md).

## Bonus implementados

- `--preflight` funcional sin escritura de base ni descarga de ACT (+3 previsto).
- Cinco índices analíticos justificados y verificados con `EXPLAIN QUERY PLAN`
  (+2 previsto).
- Explicación documentada de por qué el top CA puede diferir del top por
  atribución SE (+2 previsto).
- Modo oscuro accesible basado en CSS custom properties, preferencia del sistema
  y persistencia local (+3 previsto).
- Exportación CSV funcional de la selección municipal visible, sin servidor ni
  dependencias externas (+2 previsto).
- Scraper extendido a Chiquinquirá, Puerto Boyacá y Moniquirá, con preflight,
  base separada, auditoría 7/7 e idempotencia completa (+3 previsto).

Bonus implementado potencial: **+15/+15**. La base obligatoria de cuatro
municipios permanece separada de `db/puestos_2026_bonus.db`, por lo que la
ampliación no altera el manifest, SQL ni las visualizaciones contractuales. El
dashboard publicado muestra los siete municipios y permite alternar heatmap y
scatter entre el contrato 8×4/1.107 y la extensión 8×7/1.432, con estadísticos
separados.
