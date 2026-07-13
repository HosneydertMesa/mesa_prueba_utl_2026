-- Reto 3.2: candidatos individuales con dominancia estrictamente mayor a 60%
-- dentro de los votos de su partido en una mesa. Incluye CA y SE.
SELECT
    mu.nombre AS municipio,
    pu.codigo AS puesto_codigo,
    pu.nombre AS puesto,
    me.numero AS mesa_numero,
    me.codigo AS mesa_codigo,
    pa.corporacion,
    pa.codpar,
    pa.nombre AS partido,
    ca.codcan,
    ca.nombre_fuente AS candidato,
    rc.votos AS votos_candidato,
    rp.votos AS votos_partido,
    ROUND(
        CAST(rc.votos AS REAL) / NULLIF(rp.votos, 0),
        6
    ) AS concentracion
FROM resultados_candidato AS rc
JOIN candidatos AS ca
    ON ca.id = rc.candidato_id
JOIN partidos AS pa
    ON pa.id = ca.partido_id
JOIN resultados_partido AS rp
    ON rp.mesa_id = rc.mesa_id
   AND rp.partido_id = ca.partido_id
JOIN mesas AS me
    ON me.id = rc.mesa_id
JOIN puestos AS pu
    ON pu.id = me.puesto_id
JOIN municipios AS mu
    ON mu.id = pu.municipio_id
WHERE ca.es_lista = 0
  AND CAST(rc.votos AS REAL) / NULLIF(rp.votos, 0) > 0.60
ORDER BY
    concentracion DESC,
    municipio,
    puesto_codigo,
    mesa_numero,
    pa.corporacion,
    pa.codpar,
    ca.codcan;
