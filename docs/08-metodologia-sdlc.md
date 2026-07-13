# Metodología SDLC local

## Enfoque

Se adopta desarrollo troncal ligero para una prueba individual:

- `main` representa el último estado integrado y entregable, no cada avance local.
- Cada incremento funcional se desarrolla en una rama corta `codex/<tipo>-<alcance>`.
- Un incremento resuelve un requisito o una capacidad verificable, no varias capas inconexas.
- Los commits atómicos se publican en un PR borrador cuando el usuario lo autoriza.
- La promoción se realiza por evidencia: DEV -> QA -> SEC -> REVIEW.

Estado actual: los retos 1-4 fueron promovidos a `main` mediante el PR #1 después
de aprobar CI y recibir autorización. El Reto 5 continúa en ramas cortas e
independientes para conservar revisiones y promociones atómicas.

No se mantendrán ramas largas llamadas `dev`, `qa` o `sec`: para una persona y una ventana corta añadirían merges y divergencia sin ofrecer aislamiento real. Esos nombres representan puertas de calidad repetibles.

## Flujo de un incremento

1. **Seleccionar:** identificar requisito, puntaje, riesgo y criterio de aceptación.
2. **Diseñar:** registrar decisiones que afecten contrato, datos o seguridad.
3. **Implementar:** cambio mínimo, reversible y con responsabilidad única.
4. **DEV:** compilar y comprobar estructura y contratos básicos.
5. **QA:** ejecutar pruebas unitarias, integración y casos borde aplicables.
6. **SEC:** buscar secretos, datos confidenciales y prácticas inseguras.
7. **REVIEW:** revisar diff, trazabilidad, README y evidencia observable.
8. **Publicar:** commit atómico, push y CI en PR borrador cuando las puertas estén verdes.
9. **Promover:** marcar listo y fusionar sólo tras revisión global/autorización.

## Puertas

| Puerta | Pregunta | Evidencia mínima |
|---|---|---|
| DEV | ¿El incremento ejecuta y respeta la estructura? | sintaxis, imports, rutas obligatorias |
| QA | ¿Hace lo esperado y falla correctamente? | pruebas, fixture, invariantes y regresión |
| SEC | ¿Evita exposición o corrupción? | escaneo de secretos, parámetros SQL, límites API |
| REVIEW | ¿Es comprensible, trazable y entregable? | diff pequeño, requisito enlazado, docs y salida |
| RELEASE | ¿La prueba completa puede enviarse? | manifest contractual, muestras trazables, Release DB, 4/4, SQL OK, PNG, metadata y repo |

## Comandos

```bash
python scripts/quality_gate.py dev
python scripts/quality_gate.py qa
python scripts/quality_gate.py sec
python scripts/quality_gate.py review
python scripts/quality_gate.py all
python scripts/quality_gate.py release
```

`all` debe pasar antes de aceptar y publicar un incremento. `release` puede fallar
durante el desarrollo y sólo debe quedar verde al cierre.

## Convenciones locales

- Ramas: `codex/feat-reto-1-2-scraper`, `codex/test-idempotencia`, `codex/docs-api`.
- Commits: `feat(scraper): add municipal preflight`, `test(db): prove idempotent reload`.
- Un commit no mezcla refactor amplio, feature y documentación ajena.
- Un PR puede agrupar varios commits verticales relacionados si cada uno conserva
  evidencia y el diff completo sigue siendo revisable.
- No usar `--no-verify` para saltar controles.
- No guardar tokens en archivos, comandos persistentes, URLs remotas o historial del shell.

## Definición de terminado por incremento

- Criterio de aceptación satisfecho.
- Prueba nueva o justificación explícita de por qué no aplica.
- DEV, QA, SEC y REVIEW verdes.
- Documentación contractual actualizada.
- Sin secretos, datos confidenciales ni artefactos temporales.
- Diff revisable, commit publicado y CI exitoso cuando el remoto está autorizado.
