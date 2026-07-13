# Evidencia de Release, clon limpio y QA final

> Corte: 13 de julio de 2026. El ensayo inicial se ejecutó antes de implementar
> el manifest; el cierre posterior documentado aquí resolvió ese último gate.

## Release de datos

Release público: [`data-v1.0.0`](https://github.com/HosneydertMesa/mesa_prueba_utl_2026/releases/tag/data-v1.0.0).

| Asset | Bytes | SHA-256 | Auditoría |
|---|---:|---|---|
| `puestos_2026.db` | 67.227.648 | `19B017DD003654A086D44080F01ACF817BC65947965B6A1E84D864FFF25BD553` | 4/4, 1.107 mesas, 2.214 resultados, `ok=True` |
| `puestos_2026_bonus.db` | 86.376.448 | `A72C4EBB1D4ACC6EE5DDB8E64383D81E69465C7AE6BEBAA9B5353D3FF27CFF82` | 7/7, 1.432 mesas, 2.864 resultados, `ok=True` |

GitHub informó ambos assets en estado `uploaded` y publicó el digest SHA-256
coincidente con el archivo local. La base bonus se incluye porque el dashboard
versionado y sus contratos requieren reproducir el alcance ampliado 8×7/1.432.

## Ensayo desde clon limpio

Punto de partida: clon `--depth 1 --branch main` del commit
`85269d683fbaaecf59d62d5ac4331e759cbd1987`, sin reutilizar `.venv` ni bases del
workspace original.

Secuencia validada:

```bash
python -m venv .venv
python -m pip install -r requirements.txt -r requirements-dev.txt
gh release download data-v1.0.0 --pattern puestos_2026.db --dir db
gh release download data-v1.0.0 --pattern puestos_2026_bonus.db --dir db
python dashboard/export_data.py --db db/puestos_2026_bonus.db --include-bonus
python -m unittest discover -s tests
python scripts/quality_gate.py all
python scripts/audit_database.py --db db/puestos_2026_bonus.db \
  --output outputs/auditoria_bonus_local.json --require-bonus
python viz/heatmap.py
python viz/scatter.py
```

Resultados observados:

- instalación declarada completada en 33 segundos con caché normal de `pip`;
- descarga de las dos bases en 16 segundos combinados;
- 60 pruebas `OK`;
- gates DEV, QA, SEC y REVIEW `PASS`;
- dashboard regenerado con 7 municipios, 104 puestos y 1.432 mesas;
- heatmap 8×4 de 205.436 bytes;
- scatter de 266.728 bytes y stdout
  `r=0.964 | pendiente=0.933 | n_mesas=1107`;
- recorrido completo observado por debajo de dos minutos, muy inferior al
  presupuesto de diez minutos.

## Cierre posterior de muestras y manifest

Una segunda lectura literal del PDF confirmó que los tres archivos de `outputs/`
son obligatorios, pero no afirma que el generador o el ejemplo sean suministrados.
Sólo `sample_data/` aparece descrito como «provisto» y el paquete recibido no lo
incluía. El PDF tampoco contiene adjuntos embebidos.

Se implementó entonces:

```text
sample_data/candidate_captured/nomenclator_boyaca_sample.json
sample_data/candidate_captured/act_ca_tunja_mesa_001.json
sample_data/candidate_captured/act_se_tunja_mesa_001.json
sample_data/candidate_captured/provenance.json
outputs/generar_manifest.py
outputs/evaluation_manifest.example.json
```

Las muestras proceden de respuestas reales conservadas en la caché del scraper.
`provenance.json` registra URL, ETag, fecha, tamaño y SHA-256, y declara
`official_utl_sample=false`. El generador declara
`candidate_implemented_from_pdf_contract`, produce el manifest real y no se
presenta como herramienta oficial recibida.

Resultado actual observado:

```text
4/4 municipios | mesas=1107
SQL OK 3.1 | filas=73
SQL OK 3.2 | filas=3780
SQL OK 3.3 | filas=5
r=0.964 | pendiente=0.933 | n_mesas=1107
MANIFEST OK | salida=outputs\evaluation_manifest.json
[PASS] DEV
[PASS] QA
[PASS] SEC
[PASS] REVIEW
[PASS] RELEASE
```

La suite actual contiene 65 pruebas y valida además la procedencia/hash/carga ETL
de las muestras y el contrato JSON del manifest. Antes del tag final se repetirá
el ensayo limpio sobre el SHA ya fusionado.

## QA del dashboard publicado

URL: `https://hosneydertmesa.github.io/mesa_prueba_utl_2026/`.

| Verificación | Resultado |
|---|---|
| Cuatro vistas y navegación con `ArrowRight` | OK |
| Modo claro/oscuro y estado accesible | OK |
| Moniquirá bonus: top 10, 5 puestos y 61 mesas | OK |
| CSV `dashboard-moniquira.csv`, 2.105 bytes y cabeceras UTF-8 | OK |
| Obligatorio: heatmap 8×4 y scatter 1.107 | OK |
| Ampliado: heatmap 8×7 y scatter 1.432 | OK |
| Filtro Moniquirá: 61 puntos y estado en URL | OK |
| Presentación guiada y salida con `Esc` | OK |
| Consola del navegador | 0 warnings, 0 errores |
| 360, 768, 1.280 y 1.920 px × cuatro vistas | sin overflow de página |

La automatización disponible expuso Chrome y un navegador embebido basado en
Chromium, pero no Firefox. La política de la superficie automatizada tampoco
permite navegar a `file://`. Por ello quedan dos comprobaciones manuales antes
de congelar la entrega: Firefox y apertura directa de `dashboard/index.html`.

## Estado de cierre

- Reproducibilidad de código y datos: cerrada.
- Distribución de bases: cerrada.
- QA web automatizable: cerrada.
- Manifest contractual y RELEASE: cerrados.
- QA Firefox/`file://`: manual pendiente.
- Tag final y envío: pendientes del QA manual y autorización de congelamiento.
