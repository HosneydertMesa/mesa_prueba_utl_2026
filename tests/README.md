# Estrategia de pruebas

- `unit/`: parser, normalización, ratios, atribución y stdout.
- `integration/`: fixtures -> SQLite -> SQL -> JSON/PNG.
- `contract/`: rutas, headings, colores y contrato del manifest de entrega.
- `integration/test_sample_data.py`: procedencia, hashes y carga ETL de las
  capturas reales incluidas como fallback reproducible.

No se agregan pruebas vacías que den una falsa señal verde.
