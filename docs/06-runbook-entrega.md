# Runbook de ejecución y entrega

## Estado actual

- Completados: contrato API, scraper, schema, ETL, carga 4/4, auditoría y SQL 3.x.
- Verdes localmente: 42 pruebas, Ruff, DEV, QA, SEC y REVIEW.
- En nube: PR #1 borrador, sin conflictos; `main` aún no se fusiona.
- Completado adicional: exportador, contrato `dashboard/data.json` y dashboard
  autocontenido con datos embebidos.
- Pendientes: PNG, insumos/manifest oficial, Release de DB y clon limpio.

## Desarrollo incremental restante

1. Ejecutar `python scripts/audit_database.py` y conservar `ok=True`.
2. Regenerar `dashboard/data.json` y confirmar contrato.
3. Abrir `dashboard/index.html` directamente en Chrome/Firefox y revisar consola.
4. Mantener dark mode/CSV pospuestos hasta completar los 100 puntos base.
5. Implementar `viz/heatmap.py` y validar PNG 8×4 >10 KB.
6. Implementar `viz/scatter.py`, PNG y stdout exacto.
7. Incorporar insumos oficiales sin modificarlos y ejecutar manifest.
8. Publicar SQLite como Release asset y enlazar checksum/URL.
9. Ensayar clon limpio, gate RELEASE, revisión en incógnito y promoción.

## Comandos reproducibles actuales

```bash
python scraper/scraper.py --preflight
python scraper/scraper.py
python scripts/audit_database.py
python dashboard/export_data.py
python -m unittest discover -s tests -v
python scripts/quality_gate.py all
```

La segunda ejecución del scraper debe informar `insertadas=0`. Durante desarrollo
se puede usar la caché ignorada por Git; el clon limpio debe funcionar sin ella.

## Ensayo de clon limpio

1. Clonar el repositorio público en una ruta nueva.
2. Seguir únicamente el README con cronómetro de 10 minutos.
3. Instalar dependencias en un entorno virtual.
4. Obtener la base desde el Release o regenerarla.
5. Ejecutar auditoría, SQL, exportación, PNG y manifest.
6. Abrir dashboard desde disco y revisar DevTools Console.
7. Registrar cualquier conocimiento implícito, corregir README y repetir.

## Checklist final irreversible

- Repo público accesible en incógnito y nombre `mesa_prueba_utl_2026`.
- README conserva exactamente los headings obligatorios y metadata real.
- `evaluation_manifest.json`: 4/4 municipios y SQL OK ×3.
- Base SQLite disponible en Release con enlace y checksum.
- Dashboard: cuatro municipios, colores exactos, línea 1.0 y consola limpia.
- PNG existentes, legibles y mayores de 10 KB.
- Secretos, PDF confidencial, caché y temporales ausentes del commit.
- `python scripts/quality_gate.py release` verde.
- PR revisado, CI exitoso y fusionado a `main` con autorización.
- SHA final guardado; formulario enviado una sola vez antes del cierre.

## Recuperación

- API caída: usar caché o muestras oficiales, conservar evidencia y documentar.
- JSON 200 inválido: retry/backoff automático; nunca cachear cuerpo corrupto.
- SQL ERROR: ejecutar fixture calculable, corregir y regenerar auditoría/manifest.
- Dashboard `file://` falla: eliminar fetch local y embeber/cargar datos compatible.
- DB grande: mantener ignorada, crear Release asset y comprobar descarga.
- Manifest ausente: no fabricarlo; conservar auditoría local y solicitar insumo.
- GitHub falla al final: conservar SHA/evidencia y usar el canal indicado por UTL.
