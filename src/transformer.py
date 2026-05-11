import base64
import hashlib
import json
import unicodedata
from datetime import datetime


def _bytes_repr(obj):
    if isinstance(obj, bytes):
        return base64.b64encode(obj).decode("ascii")
    return str(obj)


def _compute_hash(row):
    raw = json.dumps(row, sort_keys=True, default=_bytes_repr, ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _normalize_text(value, remove_accents=False):
    if value is None or not isinstance(value, str):
        return value

    normalized = " ".join(value.split())
    if remove_accents:
        normalized = unicodedata.normalize("NFKD", normalized)
        normalized = "".join(
            char for char in normalized if not unicodedata.combining(char)
        )

    return normalized


def _clean_row(row):
    cleaned = dict(row)
    if "NOMBRE_CLIENTE" in cleaned:
        cleaned["NOMBRE_CLIENTE"] = _normalize_text(
            cleaned["NOMBRE_CLIENTE"], remove_accents=True
        )
    if "CODIGO" in cleaned:
        cleaned["CODIGO"] = _normalize_text(cleaned["CODIGO"])
    return cleaned


def transform(data, column_metadata):
    ejecucion = datetime.now()
    fecha_id = ejecucion.strftime("%Y%m%d%H%M%S")

    enriched = []
    for idx, row in enumerate(data):
        cleaned_row = _clean_row(row)
        hash_val = _compute_hash(cleaned_row)
        codigo = f"ETL-{fecha_id}-{idx + 1:05d}"
        enriched.append({
            "HASH_REGISTRO": hash_val,
            "CODIGO_REGISTRO": codigo,
            "FECHA_EJECUCION": ejecucion,
            **cleaned_row,
        })

    return enriched
