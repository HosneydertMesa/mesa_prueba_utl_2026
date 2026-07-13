-- Reto 3.3: top 5 candidatos CA por atribución SE consolidada.
-- Fórmula por mesa: A_ij = (votos_cand / votos_partido_CA) * votos_SE_partido.
-- Los pesos 0.5 evitan atribuir dos veces el total de coaliciones CA partidas.
WITH homologacion(codpar_ca, codpar_se, peso) AS (
    VALUES
        (5,   57, 1.0),
        (87,  92, 1.0),
        (10,  10, 1.0),
        (2,    2, 1.0),
        (121,  3, 0.5),
        (121, 17, 0.5),
        (122, 44, 1.0),
        (137, 44, 1.0),
        (120,  9, 1.0)
),
candidatos_ca AS (
    SELECT
        rc.mesa_id,
        ca.id AS candidato_id,
        ca.codcan,
        ca.nombre_fuente AS candidato,
        pa.codpar AS codpar_ca,
        pa.nombre AS partido_ca,
        rc.votos AS votos_candidato_ca,
        rp.votos AS votos_partido_ca
    FROM resultados_candidato AS rc
    JOIN candidatos AS ca
        ON ca.id = rc.candidato_id
    JOIN partidos AS pa
        ON pa.id = ca.partido_id
       AND pa.corporacion = 'CA'
    JOIN resultados_partido AS rp
        ON rp.mesa_id = rc.mesa_id
       AND rp.partido_id = ca.partido_id
    WHERE ca.es_lista = 0
),
senado_homologado AS (
    SELECT
        rp.mesa_id,
        ho.codpar_ca,
        SUM(rp.votos * ho.peso) AS votos_se_partido
    FROM homologacion AS ho
    JOIN partidos AS pa
        ON pa.corporacion = 'SE'
       AND pa.codpar = ho.codpar_se
    JOIN resultados_partido AS rp
        ON rp.partido_id = pa.id
    GROUP BY rp.mesa_id, ho.codpar_ca
),
atribucion_por_mesa AS (
    SELECT
        cc.candidato_id,
        cc.codpar_ca,
        cc.partido_ca,
        cc.codcan,
        cc.candidato,
        cc.mesa_id,
        cc.votos_candidato_ca,
        cc.votos_partido_ca,
        sh.votos_se_partido,
        (
            CAST(cc.votos_candidato_ca AS REAL)
            / NULLIF(cc.votos_partido_ca, 0)
        ) * sh.votos_se_partido AS atribucion_se
    FROM candidatos_ca AS cc
    JOIN senado_homologado AS sh
        ON sh.mesa_id = cc.mesa_id
       AND sh.codpar_ca = cc.codpar_ca
)
SELECT
    codpar_ca,
    partido_ca,
    codcan,
    candidato,
    SUM(votos_candidato_ca) AS votos_candidato_ca,
    COUNT(atribucion_se) AS mesas_calculadas,
    ROUND(SUM(atribucion_se), 6) AS atribucion_se_consolidada
FROM atribucion_por_mesa
GROUP BY candidato_id, codpar_ca, partido_ca, codcan, candidato
ORDER BY
    atribucion_se_consolidada DESC,
    codpar_ca,
    codcan
LIMIT 5;
