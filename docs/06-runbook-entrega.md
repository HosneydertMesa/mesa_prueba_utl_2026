# Runbook de ejecución y entrega

## Estado actual

- Completados: contrato API, scraper, schema, ETL, carga 4/4, auditoría y SQL 3.x.
- Verdes localmente: 64 pruebas, Ruff, DEV, QA, SEC, REVIEW y RELEASE.
- En nube: retos 1-5, bonus y Dashboard 2.0 integrados en `main`; toda evolución
  web se valida mediante CI antes de su promoción.
- Completado adicional: exportador, contrato `dashboard/data.json` y dashboard
  autocontenido con datos embebidos.
- Completado adicional: heatmap 8×4 anotado y superior a 10 KB.
- Completado adicional: scatter de 1.107 mesas, OLS/Pearson y stdout exacto.
- Completado adicional: modo oscuro persistente y exportación CSV municipal.
- Completado adicional: tres municipios bonus, auditoría 7/7 e idempotencia.
- Completado adicional: Dashboard Analítico 2.0 con heatmap y scatter interactivos.
- Completado adicional: Workspace 3.0 con cuatro vistas y workflow GitHub Pages.
- Publicado: dashboard HTTPS verificado en
  `https://hosneydertmesa.github.io/mesa_prueba-utl_2026/` desde `main`.
- Publicado: Release `data-v1.0.0` con bases 4/4 y 7/7, tamaños y SHA-256.
- Verificado: clon limpio, descarga de assets, auditorías, exportador, PNG,
  60 pruebas del corte anterior y gates DEV/QA/SEC/REVIEW en menos de 2 minutos observados en esta
  máquina con caché normal de paquetes.
- Verificado adicional: muestras reales trazables, manifest `OK`, 4/4 municipios,
  SQL `OK` ×3 y gate RELEASE verde.
- Pendientes: QA manual Firefox + `file://` y tag final.

## Cierre restante

1. Abrir `dashboard/index.html` mediante `file://` en Chrome y Firefox.
2. Repetir teclado, tema, CSV y tooltips en Firefox; registrar evidencia manual.
3. Regenerar el manifest y confirmar 4/4 municipios, SQL `OK` ×3 y RELEASE verde.
4. Congelar `main`, crear tag final, registrar SHA y enviar una sola vez.

## Comandos reproducibles actuales

```bash
python scraper/scraper.py --preflight
python scraper/scraper.py
python scripts/audit_database.py
python scraper/scraper.py --preflight --incluir-bonus
python scraper/scraper.py --incluir-bonus --db db/puestos_2026_bonus.db
gh release download data-v1.0.0 --pattern puestos_2026.db --dir db
gh release download data-v1.0.0 --pattern puestos_2026_bonus.db --dir db
python scripts/audit_database.py --db db/puestos_2026_bonus.db \
  --output outputs/auditoria_bonus_local.json --require-bonus
python dashboard/export_data.py --db db/puestos_2026_bonus.db --include-bonus
python outputs/generar_manifest.py
python -m unittest discover -s tests -v
python scripts/quality_gate.py all
python scripts/quality_gate.py release
```

La segunda ejecución del scraper debe informar `insertadas=0`. Durante desarrollo
se puede usar la caché ignorada por Git; el clon limpio debe funcionar sin ella.

## Ensayo de clon limpio

Ejecución completada el 13 de julio de 2026. Evidencia, resultados, tiempos y
limitaciones en `docs/23-evidencia-cierre-reproducibilidad.md`.

1. Clonar el repositorio público en una ruta nueva.
2. Seguir únicamente el README con cronómetro de 10 minutos.
3. Instalar dependencias en un entorno virtual.
4. Obtener la base desde el Release o regenerarla.
5. Ejecutar auditoría, SQL, exportación, PNG y manifest contractual.
6. Abrir dashboard desde disco y revisar DevTools Console.
7. Registrar cualquier conocimiento implícito, corregir README y repetir.

## Checklist final irreversible

- Repo público accesible en incógnito y nombre `mesa_prueba_utl_2026`.
- README conserva exactamente los headings obligatorios y metadata real.
- `evaluation_manifest.json`: 4/4 municipios y SQL OK ×3.
- Base SQLite disponible en Release con enlace y checksum.
- Dashboard: 4 municipios obligatorios + 3 bonus identificados, colores exactos,
  línea 1.0 y consola limpia.
- Bonus dashboard: tema claro/oscuro y CSV válido en apertura directa `file://`.
- Bonus scraper: evidencia 7/7 disponible sin sustituir la base contractual 4/4.
- GitHub Pages: workflow verde, HTTPS activo y URL pública verificada.
- PNG existentes, legibles y mayores de 10 KB.
- Secretos, PDF confidencial, caché y temporales ausentes del commit.
- `python scripts/quality_gate.py release` verde.
- PR revisado, CI exitoso y fusionado a `main` con autorización.
- SHA final guardado; formulario enviado una sola vez antes del cierre.

## Recuperación

- API caída: usar caché o `sample_data/candidate_captured/`, conservar evidencia y documentar.
- JSON 200 inválido: retry/backoff automático; nunca cachear cuerpo corrupto.
- SQL ERROR: ejecutar fixture calculable, corregir y regenerar auditoría/manifest.
- Dashboard `file://` falla: eliminar fetch local y embeber/cargar datos compatible.
- DB grande: mantener ignorada, crear Release asset y comprobar descarga.
- Manifest inconsistente: regenerarlo, revisar `overall_status`, corregir la causa
  y repetir `quality_gate.py release`; no editar el JSON manualmente.
- GitHub falla al final: conservar SHA/evidencia y usar el canal indicado por UTL.
