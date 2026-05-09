import pymysql
from pymysql.constants import FIELD_TYPE
from config.settings import settings

TYPE_MAP = {
    FIELD_TYPE.TINY: "TINYINT",
    FIELD_TYPE.SHORT: "SMALLINT",
    FIELD_TYPE.INT24: "INT",
    FIELD_TYPE.LONG: "INT",
    FIELD_TYPE.LONGLONG: "BIGINT",
    FIELD_TYPE.FLOAT: "FLOAT",
    FIELD_TYPE.DOUBLE: "FLOAT",
    FIELD_TYPE.DECIMAL: "DECIMAL(18,6)",
    FIELD_TYPE.NEWDECIMAL: "DECIMAL(18,6)",
    FIELD_TYPE.CHAR: "NVARCHAR(1)",
    FIELD_TYPE.VARCHAR: "NVARCHAR({})",
    FIELD_TYPE.VAR_STRING: "NVARCHAR({})",
    FIELD_TYPE.STRING: "NVARCHAR(255)",
    FIELD_TYPE.BLOB: "VARBINARY(MAX)",
    FIELD_TYPE.TINY_BLOB: "VARBINARY(MAX)",
    FIELD_TYPE.MEDIUM_BLOB: "VARBINARY(MAX)",
    FIELD_TYPE.LONG_BLOB: "VARBINARY(MAX)",
    FIELD_TYPE.DATE: "DATE",
    FIELD_TYPE.DATETIME: "DATETIME2",
    FIELD_TYPE.TIMESTAMP: "DATETIME2",
    FIELD_TYPE.TIME: "TIME",
    FIELD_TYPE.YEAR: "SMALLINT",
    FIELD_TYPE.JSON: "NVARCHAR(MAX)",
    FIELD_TYPE.BIT: "BIT",
    FIELD_TYPE.ENUM: "NVARCHAR(255)",
    FIELD_TYPE.SET: "NVARCHAR(255)",
    FIELD_TYPE.GEOMETRY: "NVARCHAR(MAX)",
}

STRING_TYPES = {
    FIELD_TYPE.CHAR,
    FIELD_TYPE.VARCHAR,
    FIELD_TYPE.VAR_STRING,
    FIELD_TYPE.STRING,
    FIELD_TYPE.ENUM,
    FIELD_TYPE.SET,
    FIELD_TYPE.JSON,
}

# ══════════════════════════════════════════════════════════════
# CONSULTA MYSQL/MARIADB - REEMPLAZA CON TU SELECT REAL
# ══════════════════════════════════════════════════════════════
# Ejemplo:
#   SELECT cui, nombre, telefono, fecha_llamada, duracion
#   FROM llamadas
#   WHERE fecha_llamada >= DATE_SUB(NOW(), INTERVAL 3 HOUR)
QUERY_MYSQL = """
    SELECT 1 AS id, 'ejemplo' AS nombre
"""


def get_column_metadata(cursor):
    cols = []
    for desc in cursor.description:
        name = desc[0]
        type_code = desc[1]
        length = desc[3] or 255
        precision = desc[4] or 0
        scale = desc[5] or 0

        if type_code in STRING_TYPES and length > 0 and length <= 4000:
            sql_type = TYPE_MAP.get(type_code, "NVARCHAR(255)").format(length)
        elif type_code in STRING_TYPES:
            sql_type = "NVARCHAR(MAX)"
        else:
            sql_type = TYPE_MAP.get(type_code, "NVARCHAR(MAX)")
            sql_type = sql_type.split("{")[0].strip()

        cols.append({
            "name": name,
            "type_code": type_code,
            "sql_type": sql_type,
            "length": length,
            "precision": precision,
            "scale": scale,
        })
    return cols


def _mysql_ssl():
    ca = settings.MYSQL_SSL_CA
    cert = settings.MYSQL_SSL_CERT
    key = settings.MYSQL_SSL_KEY
    if ca or cert or key:
        params = {}
        if ca:
            params["ca"] = ca
        if cert:
            params["cert"] = cert
        if key:
            params["key"] = key
        return params
    return None


def extract():
    ssl_params = _mysql_ssl() if settings.MYSQL_SSL_ENABLED else None
    conn = pymysql.connect(
        host=settings.MYSQL_HOST,
        port=settings.MYSQL_PORT,
        user=settings.MYSQL_USER,
        password=settings.MYSQL_PASSWORD,
        database=settings.MYSQL_DATABASE,
        charset="utf8mb4",
        ssl=ssl_params,
    )
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(QUERY_MYSQL)
            rows = cursor.fetchall()
            metadata = get_column_metadata(cursor)
            return rows, metadata
    finally:
        conn.close()
