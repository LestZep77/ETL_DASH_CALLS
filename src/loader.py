import pypyodbc as odbc
from config.settings import settings


def _connection_string():
    tscc = "yes" if settings.SQLSERVER_TRUST_SERVER_CERTIFICATE else "no"
    return (
        f"DRIVER={settings.SQLSERVER_DRIVER};"
        f"SERVER={settings.SQLSERVER_HOST};"
        f"DATABASE={settings.SQLSERVER_DATABASE};"
        f"UID={settings.SQLSERVER_USER};"
        f"PWD={settings.SQLSERVER_PASSWORD};"
        f"TrustServerCertificate={tscc};"
    )


def _get_connection():
    return odbc.connect(_connection_string(), autocommit=False)


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
            f"SELECT [HASH_REGISTRO] FROM {table_full}"
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

        new_rows = [row for row in data if row["HASH_REGISTRO"] not in existing]
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
