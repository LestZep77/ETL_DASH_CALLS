import time
import logging

from config.settings import settings
from src.extractor import extract
from src.transformer import transform
from src.loader import create_table_if_not_exists, load

logger = logging.getLogger("etl_pipeline")


def run():
    start = time.time()
    logger.info("E T L   I N I C I A D O")
    logger.info("Origen:  MySQL/MariaDB  →  %s:%s/%s",
                 settings.MYSQL_HOST, settings.MYSQL_PORT, settings.MYSQL_DATABASE)
    logger.info("Destino: SQL Server     →  %s/%s [%s]",
                 settings.SQLSERVER_HOST, settings.SQLSERVER_DATABASE, settings.SQLSERVER_SCHEMA)

    logger.info("[EXTRACT] Conectando a MySQL/MariaDB...")
    try:
        data, metadata = extract()
    except Exception as e:
        logger.error("[EXTRACT] FALLO: %s", e)
        raise
    logger.info("[EXTRACT] %d filas extraídas, %d columnas",
                len(data), len(metadata))
    for col in metadata:
        logger.debug("  Columna: %s (%s)", col["name"], col["sql_type"])

    if not data:
        logger.warning("[EXTRACT] 0 filas extraídas. No hay datos para procesar.")
        elapsed = time.time() - start
        logger.info("ETL FINALIZADO en %.2fs — Sin datos", elapsed)
        return {"status": "sin_datos", "extracted": 0, "inserted": 0, "elapsed": elapsed}

    logger.info("[TRANSFORM] Calculando hashes y códigos...")
    enriched = transform(data, metadata)
    logger.info("[TRANSFORM] %d registros enriquecidos", len(enriched))

    logger.info("[LOAD] Conectando a SQL Server...")
    try:
        created = create_table_if_not_exists(metadata)
        if created:
            logger.info("[LOAD] Tabla '%s' creada exitosamente",
                        settings.TABLE_NAME_DESTINO)
        else:
            logger.info("[LOAD] Tabla '%s' ya existe, omitiendo creación",
                        settings.TABLE_NAME_DESTINO)
    except Exception as e:
        logger.error("[LOAD] FALLO al crear/verificar tabla: %s", e)
        raise

    logger.info("[LOAD] Insertando datos (control incremental por hash)...")
    try:
        inserted = load(enriched)
    except Exception as e:
        logger.error("[LOAD] FALLO al insertar datos: %s", e)
        raise
    logger.info("[LOAD] %d registros nuevos insertados", inserted)

    elapsed = time.time() - start
    logger.info("E T L   C O M P L E T A D O")
    logger.info("Resumen: %d extraídos → %d insertados (%.2fs)",
                len(data), inserted, elapsed)

    return {
        "status": "exitoso",
        "extracted": len(data),
        "inserted": inserted,
        "elapsed": elapsed,
    }
