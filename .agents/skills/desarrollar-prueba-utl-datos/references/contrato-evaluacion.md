# Contrato de evaluación resumido

## Base (100)

- Reto 1 (25): API documentada; scraper con municipios, retry/backoff, idempotencia y progreso; manifest valida conteos.
- Reto 2 (25): SQLite con UNIQUE/FK/NOT NULL/carga_log; ETL normaliza y deduplica; manifest verifica tablas y líder SE.
- Reto 3 (25): Verde CA=5 a SE=57; dominancia >60%; top 5 por `A_ij=(votos_cand/votos_partido)*votos_SE_partido`.
- Reto 4 (15): un `index.html`, sin servidor, cuatro municipios, top 10 CA, líder SE, arrastre y colores exactos.
- Reto 5 (10): heatmap 8x4 y scatter por mesa con OLS/Pearson; stdout `r=X.XXX | pendiente=X.XXX | n_mesas=NNN`.

## Bonus (15)

`--preflight` +3; tres índices +2; explicación CA vs atribución +2; dark mode +3; CSV +2; municipios adicionales +3.

No optimizar bonus si falta un archivo base, municipio, SQL o validación del manifest. Consultar `docs/01-trazabilidad-requisitos.md`.

