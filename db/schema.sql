PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

CREATE TABLE IF NOT EXISTS carga_log (
    id INTEGER PRIMARY KEY,
    iniciado_en TEXT NOT NULL,
    finalizado_en TEXT,
    estado TEXT NOT NULL CHECK (estado IN ('INICIADA', 'COMPLETADA', 'FALLIDA')),
    corporacion TEXT CHECK (corporacion IN ('CA', 'SE') OR corporacion IS NULL),
    ambito_codigo TEXT,
    fuente_url TEXT NOT NULL,
    fuente_etag TEXT,
    fuente_sha256 TEXT CHECK (fuente_sha256 IS NULL OR length(fuente_sha256) = 64),
    filas_leidas INTEGER NOT NULL DEFAULT 0 CHECK (filas_leidas >= 0),
    filas_insertadas INTEGER NOT NULL DEFAULT 0 CHECK (filas_insertadas >= 0),
    filas_omitidas INTEGER NOT NULL DEFAULT 0 CHECK (filas_omitidas >= 0),
    error TEXT
);

CREATE TABLE IF NOT EXISTS municipios (
    id INTEGER PRIMARY KEY,
    codigo TEXT NOT NULL UNIQUE CHECK (length(codigo) = 7),
    nombre TEXT NOT NULL,
    departamento_codigo TEXT NOT NULL DEFAULT '07' CHECK (length(departamento_codigo) = 2),
    UNIQUE (departamento_codigo, nombre)
);

CREATE TABLE IF NOT EXISTS puestos (
    id INTEGER PRIMARY KEY,
    municipio_id INTEGER NOT NULL REFERENCES municipios(id),
    codigo TEXT NOT NULL UNIQUE CHECK (length(codigo) = 13),
    nombre TEXT NOT NULL,
    mesas_esperadas INTEGER NOT NULL CHECK (mesas_esperadas >= 0)
);

CREATE TABLE IF NOT EXISTS mesas (
    id INTEGER PRIMARY KEY,
    puesto_id INTEGER NOT NULL REFERENCES puestos(id),
    numero INTEGER NOT NULL CHECK (numero >= 1),
    codigo TEXT NOT NULL UNIQUE CHECK (length(codigo) = 19),
    UNIQUE (puesto_id, numero)
);

CREATE TABLE IF NOT EXISTS partidos (
    id INTEGER PRIMARY KEY,
    corporacion TEXT NOT NULL CHECK (corporacion IN ('CA', 'SE')),
    codpar INTEGER NOT NULL CHECK (codpar >= 0),
    nombre TEXT NOT NULL,
    UNIQUE (corporacion, codpar)
);

CREATE TABLE IF NOT EXISTS candidatos (
    id INTEGER PRIMARY KEY,
    partido_id INTEGER NOT NULL REFERENCES partidos(id),
    codcan TEXT NOT NULL,
    nombre_fuente TEXT NOT NULL,
    nombre_normalizado TEXT NOT NULL,
    es_lista INTEGER NOT NULL DEFAULT 0 CHECK (es_lista IN (0, 1)),
    UNIQUE (partido_id, codcan)
);

CREATE TABLE IF NOT EXISTS resumen_mesa (
    id INTEGER PRIMARY KEY,
    mesa_id INTEGER NOT NULL REFERENCES mesas(id),
    corporacion TEXT NOT NULL CHECK (corporacion IN ('CA', 'SE')),
    carga_id INTEGER NOT NULL REFERENCES carga_log(id),
    censo INTEGER NOT NULL CHECK (censo >= 0),
    votantes INTEGER NOT NULL CHECK (votantes >= 0),
    votos_nulos INTEGER NOT NULL CHECK (votos_nulos >= 0),
    votos_no_marcados INTEGER NOT NULL CHECK (votos_no_marcados >= 0),
    votos_blancos INTEGER NOT NULL CHECK (votos_blancos >= 0),
    votos_validos INTEGER NOT NULL CHECK (votos_validos >= 0),
    UNIQUE (mesa_id, corporacion)
);

CREATE TABLE IF NOT EXISTS resultados_partido (
    id INTEGER PRIMARY KEY,
    mesa_id INTEGER NOT NULL REFERENCES mesas(id),
    partido_id INTEGER NOT NULL REFERENCES partidos(id),
    carga_id INTEGER NOT NULL REFERENCES carga_log(id),
    votos INTEGER NOT NULL CHECK (votos >= 0),
    UNIQUE (mesa_id, partido_id)
);

CREATE TABLE IF NOT EXISTS resultados_candidato (
    id INTEGER PRIMARY KEY,
    mesa_id INTEGER NOT NULL REFERENCES mesas(id),
    candidato_id INTEGER NOT NULL REFERENCES candidatos(id),
    carga_id INTEGER NOT NULL REFERENCES carga_log(id),
    votos INTEGER NOT NULL CHECK (votos >= 0),
    UNIQUE (mesa_id, candidato_id)
);

-- Bonus 2.1: índices orientados a consultas reales, no duplicados de UNIQUE.
CREATE INDEX IF NOT EXISTS idx_puestos_municipio
    ON puestos (municipio_id, id);

CREATE INDEX IF NOT EXISTS idx_partidos_codpar_corporacion
    ON partidos (codpar, corporacion, id);

CREATE INDEX IF NOT EXISTS idx_resultados_partido_partido_mesa
    ON resultados_partido (partido_id, mesa_id, votos);

CREATE INDEX IF NOT EXISTS idx_resultados_candidato_candidato_mesa
    ON resultados_candidato (candidato_id, mesa_id, votos);

CREATE INDEX IF NOT EXISTS idx_carga_log_estado_inicio
    ON carga_log (estado, iniciado_en);

