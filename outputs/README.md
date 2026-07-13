# Insumos del evaluador pendientes

Incorporar `generar_manifest.py` y `evaluation_manifest.example.json` originales. Generar `evaluation_manifest.json` al final; no fabricarlo manualmente.

Mientras se reciben esos insumos, `python scripts/audit_database.py` genera
`auditoria_local.json`. El archivo declara `audit_type=local_non_official` para
evitar confundirlo con el manifest del evaluador.
