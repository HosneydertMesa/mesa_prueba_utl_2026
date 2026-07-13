# Datos de muestra y procedencia

El paquete recibido el 12 de julio de 2026 contenía únicamente el PDF; no incluía
los datos que el documento describe como «provistos». Para que el parser tenga un
fallback verificable sin afirmar una procedencia inexistente, el directorio
`candidate_captured/` contiene:

- nomenclátor real reducido a los cuatro municipios obligatorios;
- una respuesta ACT real de Tunja para CA y otra para SE;
- URL, ETag, fecha de captura, tamaño y SHA-256 en `provenance.json`.

La marca `official_utl_sample=false` distingue estas capturas de un eventual
archivo entregado por la UTL. Los payloads se extrajeron de la caché del scraper,
se eliminó el campo `cedula` porque no aporta a los retos y se serializaron de
forma compacta y determinista; no se conservan como bytes HTTP originales.

Verificación:

```bash
python -m unittest tests.integration.test_sample_data -v
```

Regeneración opcional cuando exista la caché local correspondiente:

```bash
python scripts/export_sample_data.py
```

Si posteriormente se recibe un paquete oficial, debe conservarse intacto en una
ruta separada, con su propio checksum y sin sobrescribir estas evidencias.
