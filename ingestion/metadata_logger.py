from datetime import datetime
import os
from typing import Optional

import pandas as pd

METADATA_PATH = "data/metadata/ingestion_metadata.parquet"


def log_ingestion_run(
    pipeline_name: str,
    entity_name: str,
    row_count: int,
    status: str,
    error_message: Optional[str] = None,
):
    record = {
        "pipeline_name": pipeline_name,
        "entity_name": entity_name,
        "row_count": row_count,
        "status": status,
        "error_message": error_message,
        "run_at": datetime.utcnow(),
    }

    df_new = pd.DataFrame([record])

    os.makedirs("data/metadata", exist_ok=True)

    if os.path.exists(METADATA_PATH):
        df_existing = pd.read_parquet(METADATA_PATH)
        # Normalize run_at to the same precision to avoid dtype mismatch across pandas versions
        df_existing["run_at"] = df_existing["run_at"].astype("datetime64[us]")
        df_new["run_at"] = df_new["run_at"].astype("datetime64[us]")
        df_all = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_all = df_new

    # ✅ FIXED typo here
    df_all.to_parquet(METADATA_PATH, index=False)
