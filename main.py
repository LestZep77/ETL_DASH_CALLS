import sys
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime
from config.settings import settings

LOG_DIR = Path(settings.LOG_DIR)
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / f"etl_{datetime.now().strftime('%Y-%m-%d')}.log"

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)-7s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        RotatingFileHandler(
            LOG_FILE, maxBytes=10 * 1024 * 1024, backupCount=30, encoding="utf-8"
        ),
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger("main")


def main():
    logger.info("=" * 60)
    logger.info("ETL DASH CALLS - Inicio de ejecución")
    logger.info("=" * 60)

    try:
        from src.etl_pipeline import run

        result = run()

        if result["status"] == "error":
            logger.error("ETL finalizó con errores")
            sys.exit(1)

        logger.info("Ejecución exitosa. Resumen: %s", result)
        sys.exit(0)

    except Exception as e:
        logger.exception("Error crítico no manejado: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
