import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_CANDIDATES = [
    Path(__file__).resolve().parent / ".env",
    BASE_DIR / ".env",
    BASE_DIR / ".env.local",
]

for env_path in ENV_CANDIDATES:
    if env_path.exists():
        load_dotenv(env_path)
        break


class Settings:
    MYSQL_HOST: str = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT: int = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER: str = os.getenv("MYSQL_USER", "")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DATABASE: str = os.getenv("MYSQL_DATABASE", "")

    SQLSERVER_HOST: str = os.getenv("SQLSERVER_HOST", "")
    SQLSERVER_USER: str = os.getenv("SQLSERVER_USER", "")
    SQLSERVER_PASSWORD: str = os.getenv("SQLSERVER_PASSWORD", "")
    SQLSERVER_DATABASE: str = os.getenv("SQLSERVER_DATABASE", "")
    SQLSERVER_DRIVER: str = os.getenv(
        "SQLSERVER_DRIVER", "{ODBC Driver 18 for SQL Server}"
    )
    SQLSERVER_SCHEMA: str = os.getenv("SQLSERVER_SCHEMA", "dbo")
    SQLSERVER_TRUST_SERVER_CERTIFICATE: bool = os.getenv(
        "SQLSERVER_TRUST_SERVER_CERTIFICATE", "yes"
    ).lower() in ("yes", "true", "1", "y")

    MYSQL_SSL_ENABLED: bool = os.getenv("MYSQL_SSL_ENABLED", "no").lower() in (
        "yes", "true", "1", "y"
    )
    MYSQL_SSL_CA: str = os.getenv("MYSQL_SSL_CA", "")
    MYSQL_SSL_CERT: str = os.getenv("MYSQL_SSL_CERT", "")
    MYSQL_SSL_KEY: str = os.getenv("MYSQL_SSL_KEY", "")

    EXTRACT_START_DATE: str = os.getenv("EXTRACT_START_DATE", "").strip()
    EXTRACT_END_DATE: str = os.getenv("EXTRACT_END_DATE", "").strip()
    EXTRACT_OVERLAP_MINUTES: int = int(os.getenv("EXTRACT_OVERLAP_MINUTES", "60"))

    TABLE_NAME_DESTINO: str = os.getenv("TABLE_NAME_DESTINO", "tbl_dash_calls_etl")
    BATCH_SIZE: int = int(os.getenv("BATCH_SIZE", "1000"))

    LOG_DIR: str = os.getenv("LOG_DIR", str(Path(__file__).parent.parent / "logs"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()
