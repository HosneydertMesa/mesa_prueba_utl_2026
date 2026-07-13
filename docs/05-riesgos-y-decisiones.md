# Registro de riesgos y decisiones

| ID | Riesgo | Prob. | Impacto | Mitigación |
|---|---|---|---|---|
| R1 | Faltan `sample_data` y evaluador | Alta | Crítico | incorporarlos antes del contrato; no inventar schemas |
| R2 | API cambiante o caída | Alta | Alto | fixtures, timeout, retry+jitter y evidencia |
| R3 | Clave natural incorrecta | Media | Crítico | explorar muestras, UNIQUE y doble ejecución |
| R4 | Confusión CA/SE o codpar | Media | Alto | corporación en claves y homologación explícita |
| R5 | División por cero | Media | Medio | `NULLIF`, NULL y prueba |
| R6 | Dashboard falla en `file://` | Media | Alto | datos embebidos/cargador compatible y prueba real |
| R7 | CDN no disponible | Media | Medio | decidir si incrustar librería y degradar claramente |
| R8 | ML consume tiempo base | Alta | Alto | solo tras 100/100, timebox 90 min |
| R9 | DB >50 MB | Media | Alto | medir pronto, Release asset y link README |
| R10 | Publicar PDF confidencial | Media | Crítico | mantener fuera y revisar `git status` |
| R11 | Commit tras formulario | Media | Crítico | congelar SHA y enviar una vez |

## ADR-001: pipeline vertical primero

Estado: aceptada. Implementar un municipio CA+SE de extremo a extremo antes de escalar permite descubrir incompatibilidades temprano.

## ADR-002: ML como anexo explicable

Estado: aceptada. OLS/Pearson son la salida evaluada. Ridge y diagnósticos solo como suplemento agrupado y no causal.

## ADR-003: no versionar el enunciado

Estado: aceptada. El PDF marcado confidencial permanece en Downloads y no se copia al repositorio público.

