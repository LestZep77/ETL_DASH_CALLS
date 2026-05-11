from datetime import datetime

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

QUERY_MYSQL = """
        SELECT
        a.call_date AS CALL_DATE,
                a.`user` AS USUARIO,
                UPPER(u.full_name) AS NOMBRE_AGENTE,
        a.status AS STATUS,
                a.campaign_id AS `CAMPAÑA`,
        a.list_id AS LIST_ID,
                IFNULL(b.talk_sec, 0) AS SEGUNDOS,
        a.alt_dial AS ALT_DIAL,
                IF(h.called_since_last_reset = 'Y1', 'SI', 'NO') AS MANUAL,
                cm.canal AS CANAL,
        a.lead_id AS LEAD_ID,
                h.email AS CODIGO,
                UPPER(h.first_name) AS NOMBRE_CLIENTE,
                1 AS ORDEN,
                HOUR(a.call_date) AS INTERVALO,
                COALESCE(e.status_name, a.status_fallback) AS TIP_1,
                COALESCE(f.status_name, a.status_fallback) AS TIP_2,
                COALESCE(g.status_name, a.status_fallback) AS TIP_3
        FROM (
                SELECT
                        call_date,
                        `user`,
                        status,
                        campaign_id,
                        list_id,
                        lead_id,
                        uniqueid,
                        alt_dial,
                        LEFT(status, 2) AS status2,
                        LEFT(status, 4) AS status4,
                        LEFT(status, 6) AS status6,
                        CASE
                                WHEN status = 'DISMX' THEN 'Sin Tipificar'
                                WHEN status = 'DONEM' THEN 'NO CONTESTA'
                                WHEN status = 'XFER' THEN 'Transferencia'
                                WHEN status = 'ALTNUM' THEN 'NUMERO ALTERNO'
                                WHEN status = 'DISPO' THEN 'Error de Conexion'
                                WHEN status IN ('B','AB') THEN 'Busy'
                                WHEN status = 'TRANS' THEN 'Transferencia'
                                WHEN status IN ('ADC','DROP') THEN 'NO CONTESTA'
                                WHEN status = 'TIMEOT' THEN 'Tiempo Agotado'
                                WHEN status = 'CANALT' THEN 'Canales Alternativos'
                                WHEN status = 'CLIVIS' THEN 'Cliente Visita Oficina'
                                WHEN status = 'COMPLE' THEN 'Complemento'
                                WHEN status = 'GESASE' THEN 'Gestion Asesoria Bancaria'
                                WHEN status = 'GESTAD' THEN 'Gestion Administrativa'
                                WHEN status = 'LLACAS' THEN 'Llamada a Casa'
                                WHEN status = 'LLAENT' THEN 'Llamada Entrante'
                                WHEN status IN ('LLAMAV','LLAMOV') THEN 'Llamada Movil'
                                WHEN status = 'LLATRA' THEN 'Llamada a Trabajo'
                                WHEN status = 'MOTATR' THEN 'Motivo de Atraso'
                                WHEN status = 'TELREF' THEN 'Telefonos de Referencia'
                                WHEN status = 'TIPING' THEN 'Tipo de Ingreso'
                                WHEN status = 'AFTHRS' THEN 'FUERA DE HORARIO'
                                WHEN status = 'QUEUE' THEN 'NO LOGRO CONECTAR'
                                ELSE NULL
                        END AS status_fallback
                FROM asterisk.vicidial_log
                WHERE status <> 'INCALL'
                    AND call_date >= %s
                    AND call_date < %s
        ) a
        JOIN (
                SELECT 'TLVCROSS' AS campaign_id, 'CROSS' AS canal UNION ALL
                SELECT 'VEHCROSS', 'CROSS2' UNION ALL
                SELECT 'CROSSELL', 'CROSSELLING' UNION ALL
                SELECT 'CROSSEL2', 'CROSSELLING 2' UNION ALL
                SELECT 'CROSSEL3', 'CROSSELLING 3' UNION ALL
                SELECT 'CROSSEL4', 'CROSSELLING 4' UNION ALL
                SELECT 'CROSSEL5', 'CROSSELLING 5' UNION ALL
                SELECT 'CROSSEL6', 'CROSSELLING 6' UNION ALL
                SELECT 'CROSSEL7', 'CROSSELLING 7' UNION ALL
                SELECT 'CROSSEL8', 'CROSSELLING 8' UNION ALL
                SELECT 'CROSSEL9', 'CROSSELLING 9' UNION ALL
                SELECT 'CROSSE10', 'CROSSELLING 10'
        ) cm
            ON a.campaign_id = cm.campaign_id
        LEFT JOIN asterisk.vicidial_agent_log b
            ON a.lead_id = b.lead_id AND a.uniqueid = b.uniqueid
        LEFT JOIN asterisk.vicidial_users u
            ON a.`user` = u.`user`
        LEFT JOIN asterisk.vicidial_list h
            ON a.lead_id = h.lead_id
        LEFT JOIN asterisk.vicidial_campaign_statuses e
            ON a.campaign_id = e.campaign_id AND a.status2 = e.status
        LEFT JOIN asterisk.vicidial_campaign_statuses f
            ON a.campaign_id = f.campaign_id AND a.status4 = f.status
        LEFT JOIN asterisk.vicidial_campaign_statuses g
            ON a.campaign_id = g.campaign_id AND a.status6 = g.status;
"""


def _format_window_value(value):
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    if value is None:
        return None
    return str(value)


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


def extract(start_date=None, end_date=None):
    start_date = _format_window_value(start_date or settings.EXTRACT_START_DATE)
    end_date = _format_window_value(end_date or settings.EXTRACT_END_DATE)

    if not start_date or not end_date:
        raise ValueError(
            "No se definio una ventana de extraccion valida. "
            "Define EXTRACT_START_DATE y EXTRACT_END_DATE o deja que el pipeline "
            "resuelva automaticamente la ventana."
        )

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
            cursor.execute(
                QUERY_MYSQL,
                (start_date, end_date),
            )
            rows = cursor.fetchall()
            metadata = get_column_metadata(cursor)
            return rows, metadata
    finally:
        conn.close()
