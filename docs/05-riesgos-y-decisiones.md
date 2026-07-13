# Registro de riesgos y decisiones

## Riesgos vigentes

| ID | Riesgo | Estado | Impacto | Mitigación/evidencia |
|---|---|---|---|---|
| R1 | Faltan `sample_data` y evaluador oficial | Abierto externo | Crítico | no fabricar manifest; auditoría local etiquetada; solicitar originales |
| R2 | API cambiante o cuerpo inválido | Mitigado/monitor | Alto | timeout, retry/backoff, caché atómica y prueba de JSON inválido transitorio |
| R3 | Clave natural incorrecta o duplicados | Cerrado local | Crítico | UNIQUE, comparación, doble corrida completa con cero inserciones |
| R4 | Confusión CA/SE o `codpar` | Mitigado | Alto | corporación en claves y homologación explícita/probada |
| R5 | División por cero | Cerrado local | Medio | `NULLIF`, resultado `NULL` y pruebas calculables |
| R6 | Dashboard falla en un navegador o viewport no cubierto | Abierto residual | Alto | contrato `file://` verde; falta QA manual Chrome/Firefox y móvil |
| R7 | Dependencia web/CDN no disponible | Cerrado | Medio | dashboard autocontenido, sin CDN, `fetch` ni recursos externos |
| R8 | ML consume tiempo base | Controlado | Alto | bloqueado hasta completar retos 4/5 y manifest |
| R9 | DB supera 50 MB | Confirmado | Alto | 64 MB; Git ignore + GitHub Release asset + enlace README |
| R10 | Publicar PDF confidencial | Controlado | Crítico | permanece en Downloads; SEC y `git status` antes de push |
| R11 | Commits posteriores al formulario | Abierto final | Crítico | congelar SHA y enviar una sola vez |
| R12 | `votantes > censo` en fuente | Aceptado/documentado | Medio | conservar ambos valores; 53 registros reportados; no imputar |
| R13 | PR acumula varios retos | Cerrado para 4.5 | Medio | PR #7 revisado, CI verde y fusión autorizada a `main` |
| R14 | Sitio Pages diverge del artefacto local | Mitigado/monitor | Alto | mismo HTML/JSON, workflow mínimo y smoke HTTPS con 7/7 y 1.432 puntos |

## Camino crítico

1. Obtener los insumos oficiales y ejecutar el manifest sin modificarlo.
2. Publicar el Release asset de SQLite con SHA-256 y enlazarlo desde README.
3. Ensayar clon limpio en menos de 10 minutos y ejecutar gate RELEASE.
4. Completar QA manual Chrome/Firefox, responsive, teclado y consola.
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

## ADR-004: auditoría local no suplanta manifest

Estado: aplicada. `outputs/auditoria_local.json` declara
`audit_type=local_non_official`; al recibir el generador original se ejecutará sin
alterar su lógica.

## ADR-005: homologación CA→SE explícita

Estado: aplicada. La atribución usa un CTE de códigos y pesos contrastado con el
modelo citado por el enunciado. Un partido sin homologación publicada no se asigna
por similitud de nombre.

## ADR-006: distribución de SQLite mediante Release

Estado: aceptada, pendiente de ejecución. La base mide aproximadamente 64 MB y se
mantiene fuera de Git para evitar inflar el historial. Antes de entrega se adjunta
a un GitHub Release y se documentan URL y checksum.

Los cierres del camino crítico y las mejoras opcionales se gestionan en
`docs/22-hoja-ruta-mejoras.md`.
