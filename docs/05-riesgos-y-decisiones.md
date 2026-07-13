# Registro de riesgos y decisiones

## Riesgos vigentes

| ID | Riesgo | Estado | Impacto | Mitigación/evidencia |
|---|---|---|---|---|
| R1 | El paquete recibido no incluyó muestras ni generador | Cerrado | Crítico | capturas reales con hashes y manifest derivado del PDF; procedencia no oficial explícita |
| R2 | API cambiante o cuerpo inválido | Mitigado/monitor | Alto | timeout, retry/backoff, caché atómica y prueba de JSON inválido transitorio |
| R3 | Clave natural incorrecta o duplicados | Cerrado local | Crítico | UNIQUE, comparación, doble corrida completa con cero inserciones |
| R4 | Confusión CA/SE o `codpar` | Mitigado | Alto | corporación en claves y homologación explícita/probada |
| R5 | División por cero | Cerrado local | Medio | `NULLIF`, resultado `NULL` y pruebas calculables |
| R6 | Dashboard falla en un navegador o viewport no cubierto | Abierto residual | Alto | contrato `file://` verde; falta QA manual Chrome/Firefox y móvil |
| R7 | Dependencia web/CDN no disponible | Cerrado | Medio | dashboard autocontenido, sin CDN, `fetch` ni recursos externos |
| R8 | ML consume tiempo base | Controlado | Alto | pospuesto hasta QA manual y congelamiento de la entrega |
| R9 | DB supera 50 MB | Confirmado | Alto | 64 MB; Git ignore + GitHub Release asset + enlace README |
| R10 | Publicar PDF confidencial | Controlado | Crítico | permanece en Downloads; SEC y `git status` antes de push |
| R11 | Commits posteriores al formulario | Abierto final | Crítico | congelar SHA y enviar una sola vez |
| R12 | `votantes > censo` en fuente | Aceptado/documentado | Medio | conservar ambos valores; 53 registros reportados; no imputar |
| R13 | PR acumula varios retos | Cerrado para 4.5 | Medio | PR #7 revisado, CI verde y fusión autorizada a `main` |
| R14 | Sitio Pages diverge del artefacto local | Mitigado/monitor | Alto | mismo HTML/JSON, workflow mínimo y smoke HTTPS con 7/7 y 1.432 puntos |

## Camino crítico

1. Muestras trazables, manifest contractual y gate RELEASE: completados.
2. Release de bases con SHA-256 y enlace README: completado en `data-v1.0.0`.
3. Clon limpio <10 minutos y gates base: completados.
4. Completar QA manual Firefox y `file://`; Chrome/responsive/teclado están verdes.
5. Congelar el SHA final y realizar una única entrega.

ML adicional y refactors amplios no pertenecen al camino crítico. Los tres
municipios extra y Pages ya están implementados y auditados.

## ADR-001: pipeline vertical primero

Estado: aplicada. Una mesa CA+SE se completó antes de escalar; esto permitió
descubrir el uso real de totales por cámara y `codpar=i`.

## ADR-002: ML como anexo explicable

Estado: aceptada. OLS/Pearson son la salida evaluada. Ridge y diagnósticos sólo
como suplemento agrupado, no causal y posterior a los 100 puntos base.

## ADR-003: no versionar el enunciado

Estado: aplicada. El PDF confidencial permanece fuera del repositorio público.

## ADR-004: auditoría detallada complementa el manifest

Estado: aplicada. `outputs/auditoria_local.json` conserva
`audit_type=local_non_official`, mientras el generador contractual produce la
salida de entrega con procedencia propia explícita.

## ADR-005: homologación CA→SE explícita

Estado: aplicada. La atribución usa un CTE de códigos y pesos contrastado con el
modelo citado por el enunciado. Un partido sin homologación publicada no se asigna
por similitud de nombre.

## ADR-006: distribución de SQLite mediante Release

Estado: aplicada. Las bases base y bonus permanecen fuera de Git y están
publicadas en `data-v1.0.0` con URL, tamaños y SHA-256 documentados.

## ADR-007: resolver el paquete incompleto sin atribución falsa

Estado: aplicada. El PDF llama «provistos» únicamente a los datos de muestra y
no afirma que el generador sea entregado. Como sólo se recibió el PDF, se
exportaron capturas reales de la API con `official_utl_sample=false` y se
implementó el manifest con
`generator_provenance=candidate_implemented_from_pdf_contract`. Si aparece un
paquete UTL posterior, se conservará por separado para comparar contratos.

Los cierres del camino crítico y las mejoras opcionales se gestionan en
`docs/22-hoja-ruta-mejoras.md`.
