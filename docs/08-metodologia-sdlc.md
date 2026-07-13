# Metodología SDLC local

## Enfoque

Se adopta desarrollo troncal ligero para una prueba individual de 48 horas:

- `main` representa el último estado local revisado.
- Cada incremento funcional se desarrolla en una rama corta `codex/<tipo>-<alcance>`.
- Un incremento resuelve un requisito o una capacidad verificable, no varias capas inconexas.
- No se configura remoto ni se publica nada hasta autorización explícita.
- La promoción se realiza por evidencia: DEV -> QA -> SEC -> REVIEW.

No se mantendrán ramas largas llamadas `dev`, `qa` o `sec`: para una persona y una ventana corta añadirían merges y divergencia sin ofrecer aislamiento real. Esos nombres representan puertas de calidad repetibles.

## Flujo de un incremento

1. **Seleccionar:** identificar requisito, puntaje, riesgo y criterio de aceptación.
2. **Diseñar:** registrar decisiones que afecten contrato, datos o seguridad.
3. **Implementar:** cambio mínimo, reversible y con responsabilidad única.
4. **DEV:** compilar y comprobar estructura y contratos básicos.
5. **QA:** ejecutar pruebas unitarias, integración y casos borde aplicables.
6. **SEC:** buscar secretos, datos confidenciales y prácticas inseguras.
7. **REVIEW:** revisar diff, trazabilidad, README y evidencia observable.
8. **Integrar:** commit local atómico únicamente cuando las cuatro puertas estén verdes.

## Puertas

| Puerta | Pregunta | Evidencia mínima |
|---|---|---|
| DEV | ¿El incremento ejecuta y respeta la estructura? | sintaxis, imports, rutas obligatorias |
| QA | ¿Hace lo esperado y falla correctamente? | pruebas, fixture, invariantes y regresión |
| SEC | ¿Evita exposición o corrupción? | escaneo de secretos, parámetros SQL, límites API |
| REVIEW | ¿Es comprensible, trazable y entregable? | diff pequeño, requisito enlazado, docs y salida |
| RELEASE | ¿La prueba completa puede enviarse? | manifest oficial, 4/4, SQL OK, PNG, metadata y repo |

## Comandos

```bash
python scripts/quality_gate.py dev
python scripts/quality_gate.py qa
python scripts/quality_gate.py sec
python scripts/quality_gate.py review
python scripts/quality_gate.py all
python scripts/quality_gate.py release
```

`all` debe pasar antes de aceptar un incremento. `release` puede fallar durante el desarrollo y solo debe quedar verde al cierre.

## Convenciones locales

- Ramas: `codex/feat-reto-1-2-scraper`, `codex/test-idempotencia`, `codex/docs-api`.
- Commits: `feat(scraper): add municipal preflight`, `test(db): prove idempotent reload`.
- Un commit no mezcla refactor amplio, feature y documentación ajena.
- No usar `--no-verify` para saltar controles.
- No guardar tokens en archivos, comandos persistentes, URLs remotas o historial del shell.

## Definición de terminado por incremento

- Criterio de aceptación satisfecho.
- Prueba nueva o justificación explícita de por qué no aplica.
- DEV, QA, SEC y REVIEW verdes.
- Documentación contractual actualizada.
- Sin secretos, datos confidenciales ni artefactos temporales.
- Diff revisable y listo para commit local.

