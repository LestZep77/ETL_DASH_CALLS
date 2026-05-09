import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")


class Settings:
    MYSQL_HOST: str = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT: int = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER: str = os.getenv("MYSQL_USER", "")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DATABASE: str = os.getenv("MYSQL_DATABASE", "")

    SQLSERVER_HOST: str = os.getenv("SQLSERVER_HOST", "")
    SQLSERVER_PORT: int = int(os.getenv("SQLSERVER_PORT", "1433"))
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

    TABLE_NAME_DESTINO: str = os.getenv("TABLE_NAME_DESTINO", "tbl_dash_calls_etl")
    BATCH_SIZE: int = int(os.getenv("BATCH_SIZE", "1000"))

    LOG_DIR: str = os.getenv("LOG_DIR", str(Path(__file__).parent.parent / "logs"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()
