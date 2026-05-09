import pypyodbc as odbc
from config.settings import settings

CONTROL_COLUMNS = [
    ("id_etl", "BIGINT IDENTITY(1,1) PRIMARY KEY"),
    ("hash_registro", "VARCHAR(64) NOT NULL"),
    ("codigo_registro", "VARCHAR(30) NOT NULL"),
    ("fecha_ejecucion", "DATETIME2 DEFAULT GETDATE()"),
]


def _connection_string():
    tscc = "yes" if settings.SQLSERVER_TRUST_SERVER_CERTIFICATE else "no"
    return (
        f"DRIVER={settings.SQLSERVER_DRIVER};"
        f"SERVER={settings.SQLSERVER_HOST},{settings.SQLSERVER_PORT};"
        f"DATABASE={settings.SQLSERVER_DATABASE};"
        f"UID={settings.SQLSERVER_USER};"
        f"PWD={settings.SQLSERVER_PASSWORD};"
        f"TrustServerCertificate={tscc};"
    )


def _get_connection():
    return odbc.connect(_connection_string(), autocommit=False)


def _table_exists(cursor):
    schema = settings.SQLSERVER_SCHEMA
    cursor.execute(
        "SELECT OBJECT_ID(?, 'U')",
        f"{schema}.{settings.TABLE_NAME_DESTINO}",
    )
    return cursor.fetchone()[0] is not None


def create_table_if_not_exists(column_metadata):
    conn = _get_connection()
    try:
        cursor = conn.cursor()

        if _table_exists(cursor):
            return False

        col_defs = []
        for col_name, sql_type in CONTROL_COLUMNS:
            col_defs.append(f"    [{col_name}] {sql_type}")

        control_names = {c[0].lower() for c in CONTROL_COLUMNS}
        seen = set()
        for col in column_metadata:
            safe_name = col["name"]
            if safe_name.lower() in seen or safe_name.lower() in control_names:
                continue
            seen.add(safe_name.lower())
            col_defs.append(f"    [{safe_name}] {col['sql_type']} NULL")

        schema = settings.SQLSERVER_SCHEMA
        ddl_table = f"""
CREATE TABLE [{schema}].[{settings.TABLE_NAME_DESTINO}] (
{',\n'.join(col_defs)}
);"""
        ddl_index = f"""
CREATE UNIQUE INDEX [UQ_{settings.TABLE_NAME_DESTINO}_hash]
    ON [{schema}].[{settings.TABLE_NAME_DESTINO}] ([hash_registro]);
"""
        cursor.execute(ddl_table)
        cursor.execute(ddl_index)
        return True
    finally:
        conn.close()


def load(data):
    if not data:
        return 0

    schema = settings.SQLSERVER_SCHEMA
    table_full = f"[{schema}].[{settings.TABLE_NAME_DESTINO}]"

    conn = _get_connection()
    try:
        cursor = conn.cursor()

        existing = set()
        cursor.execute(
            f"SELECT [hash_registro] FROM {table_full}"
        )
        for row in cursor.fetchall():
            existing.add(row[0])

        col_names = list(data[0].keys())
        safe_cols = ", ".join(f"[{c}]" for c in col_names)
        placeholders = ", ".join("?" for _ in col_names)

        insert_stmt = (
            f"INSERT INTO {table_full} ({safe_cols}) "
            f"VALUES ({placeholders})"
        )

        new_rows = [row for row in data if row["hash_registro"] not in existing]
        inserted = 0

        for i in range(0, len(new_rows), settings.BATCH_SIZE):
            batch = new_rows[i : i + settings.BATCH_SIZE]
            params = []
            for row in batch:
                param_row = []
                for col in col_names:
                    val = row[col]
                    if isinstance(val, (dict, list)):
                        val = str(val)
                    param_row.append(val)
                params.append(param_row)

            cursor.executemany(insert_stmt, params)
            inserted += len(batch)

        conn.commit()
        return inserted
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
