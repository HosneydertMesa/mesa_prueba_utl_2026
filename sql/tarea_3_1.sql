-- Reto 3.1: arrastre Alianza Verde Cámara -> Senado por puesto y municipio.
-- Homologación obligatoria: codpar_CA=5 -> codpar_SE=57.
-- Si no existen votos CA Verde, el ratio es NULL y no un cero inventado.
WITH verde_por_puesto AS (
    SELECT
        mu.nombre AS municipio,
        pu.codigo AS puesto_codigo,
        pu.nombre AS puesto,
        SUM(
            CASE
                WHEN pa.corporacion = 'CA' AND pa.codpar = 5 THEN rp.votos
                ELSE 0
            END
        ) AS votos_ca_verde,
        SUM(
            CASE
                WHEN pa.corporacion = 'SE' AND pa.codpar = 57 THEN rp.votos
                ELSE 0
            END
        ) AS votos_se_verde
    FROM municipios AS mu
    JOIN puestos AS pu
        ON pu.municipio_id = mu.id
    JOIN mesas AS me
        ON me.puesto_id = pu.id
    LEFT JOIN resultados_partido AS rp
        ON rp.mesa_id = me.id
    LEFT JOIN partidos AS pa
        ON pa.id = rp.partido_id
    GROUP BY mu.id, mu.nombre, pu.id, pu.codigo, pu.nombre
)
SELECT
    municipio,
    puesto_codigo,
    puesto,
    votos_ca_verde,
    votos_se_verde,
    ROUND(
        CAST(votos_se_verde AS REAL) / NULLIF(votos_ca_verde, 0),
        6
    ) AS ratio_arrastre
FROM verde_por_puesto
ORDER BY municipio, puesto_codigo;
