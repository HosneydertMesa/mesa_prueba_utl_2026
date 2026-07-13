# Estrategia de calidad y ciclo de vida

## Flujo de trabajo

1. Issue o backlog con ID del enunciado.
2. Rama corta `feature/reto-X-Y-descripcion`.
3. Prueba/fixture que expresa el contrato antes del código riesgoso.
4. Implementación mínima y revisión del diff.
5. Validación local, auditoría/manifest aplicable y documentación.
6. Commit pequeño, push a rama y CI en PR borrador.

Estado actual: 33 pruebas pasan, Ruff está limpio, los gates
DEV/QA/SEC/REVIEW están verdes y GitHub Actions valida el PR #1. El gate RELEASE
sigue rojo por diseño mientras falten dashboard, PNG y manifest oficial.

## Pirámide de pruebas

- Unitarias: normalización, parsing, claves, ratios, atribución y stdout.
- Integración: fixture CA+SE -> SQLite temporal -> SQL -> exportación.
- Contrato: archivos, headings, colores, JSON y columnas.
- End-to-end: cuatro municipios ya auditados; manifest, PNG y dashboard desde
  `file://` pendientes.

## Reglas de calidad de datos

- Campos esenciales no nulos; votos enteros y no negativos.
- Un resultado por clave natural confirmada.
- Ratios con denominador cero son `NULL`, no infinito ni cero inventado.
- Conservar nombre fuente y normalizado por separado.
- Comparar conteos de preflight, payload, staging y SQLite.
- Investigar sumas de candidatos que superen el total de partido/mesa.
- Reportar `votantes > censo` como anomalía de fuente conservando ambos valores;
  no imputar ni excluir la mesa sin una regla oficial.

## Seguridad y ética

- Consumir solo endpoints públicos observados, con límites conservadores.
- Usar timeouts, pausa, User-Agent y logs sin secretos ni payloads completos.
- No publicar el PDF confidencial; mantenerlo fuera del repo.
- Comunicar asociación, no intención individual ni causalidad.

## Comandos de revisión

```bash
python -m unittest discover -s tests -v
python -m compileall scraper db dashboard viz outputs scripts
python scripts/quality_gate.py all
python scripts/audit_database.py

# Con dependencias de desarrollo instaladas
ruff check scraper scripts tests db
pytest --cov

# Sólo cuando lleguen los insumos oficiales
python scripts/verify_delivery.py
python outputs/generar_manifest.py
```

`scripts/audit_database.py` es una verificación local explícitamente no oficial;
no reemplaza el generador del evaluador.
