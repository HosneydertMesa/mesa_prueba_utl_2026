# Acta de cierre de entrega

## Identificación

- Candidato: Hosneydert Mesa.
- Repositorio: `HosneydertMesa/mesa_prueba_utl_2026`.
- Rama evaluable: `main`.
- Tag de congelamiento: `entrega-v1.0.0`.
- Release de datos: `data-v1.0.0`.
- Fecha de cierre técnico: 13 de julio de 2026.

## Resultado

La solución conserva 100/100 puntos base potenciales y 15/15 puntos bonus
potenciales. Estas cifras representan cobertura interna del contrato y no una
calificación oficial de la UTL.

La ejecución final confirmó:

- manifest `OK`, 4/4 municipios y 1.107 mesas contractuales;
- SQL 3.1, 3.2 y 3.3 en estado `OK`;
- `r=0.964 | pendiente=0.933 | n_mesas=1107`;
- 66 pruebas, Ruff y gates DEV/QA/SEC/REVIEW/RELEASE verdes;
- estructura obligatoria 21/21;
- repositorio público, cero PR abiertos y CI de `main` exitoso;
- Pages público con HTTPS y dashboard autocontenido;
- bases contractual y bonus en Release, con tamaños y SHA-256 coincidentes.

## QA del dashboard

La verificación pública automatizada recorrió Resumen, Municipio, Analítica y
Bonus; seleccionó Moniquirá, alternó 4/7 municipios, activó modo oscuro y generó
el estado de CSV preparado. No se observaron errores de consola ni desbordamiento
horizontal en 360×800 o 1.280×800.

La apertura directa `file://` en Firefox fue confirmada manualmente por el
candidato. Se conserva esta distinción para no presentar una observación manual
como evidencia automatizada.

## Artefactos de entrega

- Repositorio: https://github.com/HosneydertMesa/mesa_prueba_utl_2026
- Dashboard: https://hosneydertmesa.github.io/mesa_prueba_utl_2026/
- Bases SQLite: https://github.com/HosneydertMesa/mesa_prueba_utl_2026/releases/tag/data-v1.0.0
- Manifest: `outputs/evaluation_manifest.json`.
- Evidencia reproducible: `docs/23-evidencia-cierre-reproducibilidad.md`.

## Acción externa restante

Responder una sola vez el correo o formulario indicado por la UTL incluyendo el
repositorio, dashboard, Release de datos y tag final. No modificar `main` después
de enviar, salvo solicitud explícita del evaluador.
