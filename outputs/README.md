# Manifest de evaluación

El PDF recibido exige `generar_manifest.py`, `evaluation_manifest.json` y
`evaluation_manifest.example.json`, pero el paquete no contenía archivos
adicionales. El generador de este directorio implementa los observables descritos
en el documento y declara
`generator_provenance=candidate_implemented_from_pdf_contract`.

```bash
python outputs/generar_manifest.py
```

El comando regenera de forma determinista tanto el resultado real como el ejemplo
de contrato. Valida 4/4 municipios, conteos e integridad, líderes SE municipales,
SQL 3.1-3.3, artefactos, muestras y estadísticas del scatter. Nunca se debe editar
`evaluation_manifest.json` manualmente.

`auditoria_local.json` y `auditoria_bonus_local.json` conservan controles más
detallados para los alcances base y ampliado; complementan el manifest contractual.
