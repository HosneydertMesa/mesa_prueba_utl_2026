# Registro de riesgos y decisiones

## Riesgos vigentes

| ID | Riesgo | Estado | Impacto | Mitigación/evidencia |
|---|---|---|---|---|
| R1 | Faltan `sample_data` y evaluador oficial | Abierto externo | Crítico | no fabricar manifest; auditoría local etiquetada; solicitar originales |
| R2 | API cambiante o cuerpo inválido | Mitigado/monitor | Alto | timeout, retry/backoff, caché atómica y prueba de JSON inválido transitorio |
| R3 | Clave natural incorrecta o duplicados | Cerrado local | Crítico | UNIQUE, comparación, doble corrida completa con cero inserciones |
| R4 | Confusión CA/SE o `codpar` | Mitigado | Alto | corporación en claves y homologación explícita/probada |
| R5 | División por cero | Cerrado local | Medio | `NULLIF`, resultado `NULL` y pruebas calculables |
| R6 | Dashboard falla en `file://` | Abierto | Alto | contrato de datos embebidos y QA real en Chrome/Firefox |
| R7 | CDN no disponible | Abierto | Medio | preferir dashboard autocontenido o degradación documentada |
| R8 | ML consume tiempo base | Controlado | Alto | bloqueado hasta completar retos 4/5 y manifest |
| R9 | DB supera 50 MB | Confirmado | Alto | 64 MB; Git ignore + GitHub Release asset + enlace README |
| R10 | Publicar PDF confidencial | Controlado | Crítico | permanece en Downloads; SEC y `git status` antes de push |
| R11 | Commits posteriores al formulario | Abierto final | Crítico | congelar SHA y enviar una sola vez |
| R12 | `votantes > censo` en fuente | Aceptado/documentado | Medio | conservar ambos valores; 53 registros reportados; no imputar |
| R13 | PR acumula varios retos | Abierto gestionado | Medio | commits atómicos, CI por push y no fusionar sin review final |

## Camino crítico

1. Exportación JSON y dashboard `file://`.
2. Heatmap y scatter con contratos exactos.
3. Insumos oficiales y manifest.
4. Release asset de SQLite.
5. Clon limpio, gate RELEASE y promoción del PR.

ML, municipios extra y refactors amplios no pertenecen al camino crítico.

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
