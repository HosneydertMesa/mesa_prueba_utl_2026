# Estrategia de calidad y ciclo de vida

## Flujo de trabajo

1. Issue o backlog con ID del enunciado.
2. Rama corta `feature/reto-X-Y-descripcion`.
3. Prueba/fixture que expresa el contrato antes del código riesgoso.
4. Implementación mínima y revisión del diff.
5. Validación local, manifest y documentación.
6. Commit pequeño, por ejemplo `feat(scraper): add idempotent municipal load`.

## Pirámide de pruebas

- Unitarias: normalización, parsing, claves, ratios, atribución y stdout.
- Integración: fixture CA+SE -> SQLite temporal -> SQL -> exportación.
- Contrato: archivos, headings, colores, JSON y columnas.
- End-to-end: cuatro municipios, manifest, PNG y dashboard desde `file://`.

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
ruff check .
pytest --cov
python -m compileall scraper db dashboard viz outputs scripts
python scripts/verify_delivery.py
python outputs/generar_manifest.py
```
