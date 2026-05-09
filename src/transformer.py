import hashlib
import json
import base64
from datetime import datetime
from config.settings import settings


def _bytes_repr(obj):
    if isinstance(obj, bytes):
        return base64.b64encode(obj).decode("ascii")
    return str(obj)


def _compute_hash(row):
    raw = json.dumps(row, sort_keys=True, default=_bytes_repr, ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def transform(data, column_metadata):
    ejecucion = datetime.now()
    fecha_id = ejecucion.strftime("%Y%m%d%H%M%S")

    enriched = []
    for idx, row in enumerate(data):
        hash_val = _compute_hash(row)
        codigo = f"ETL-{fecha_id}-{idx + 1:05d}"
        enriched.append({
            "hash_registro": hash_val,
            "codigo_registro": codigo,
            "fecha_ejecucion": ejecucion,
            **row,
        })

    return enriched
