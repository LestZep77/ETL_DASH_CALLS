import time
import logging
from datetime import datetime, timedelta

from config.settings import settings
from src.extractor import extract
from src.loader import get_last_loaded_call_date, load
from src.transformer import transform

logger = logging.getLogger("etl_pipeline")


def _resolve_extract_window():
    manual_start = settings.EXTRACT_START_DATE
    manual_end = settings.EXTRACT_END_DATE

    if manual_start and manual_end:
        return manual_start, manual_end, "manual"

    if manual_start or manual_end:
        raise ValueError(
            "EXTRACT_START_DATE y EXTRACT_END_DATE deben definirse juntos o dejarse vacios para usar el watermark."
        )

    last_loaded_call_date = get_last_loaded_call_date()
    if last_loaded_call_date is None:
        raise ValueError(
            "La tabla destino no tiene watermark en CALL_DATE. "
            "Define EXTRACT_START_DATE y EXTRACT_END_DATE para la primera carga."
        )

    start_dt = last_loaded_call_date - timedelta(minutes=settings.EXTRACT_OVERLAP_MINUTES)
    end_dt = datetime.now()
    return start_dt.replace(microsecond=0), end_dt.replace(microsecond=0), "watermark"


def run():
    start = time.time()
    logger.info("E T L   I N I C I A D O")
    logger.info("Origen:  MySQL/MariaDB  →  %s:%s/%s",
                 settings.MYSQL_HOST, settings.MYSQL_PORT, settings.MYSQL_DATABASE)
    logger.info("Destino: SQL Server     →  %s/%s [%s]",
                 settings.SQLSERVER_HOST, settings.SQLSERVER_DATABASE, settings.SQLSERVER_SCHEMA)

    extract_start, extract_end, window_source = _resolve_extract_window()
    logger.info("Ventana extracción (%s): %s → %s",
                window_source, extract_start, extract_end)

    logger.info("[EXTRACT] Conectando a MySQL/MariaDB...")
    try:
        data, metadata = extract(extract_start, extract_end)
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
