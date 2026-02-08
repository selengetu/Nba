import pandas as pd
from warehouse.snowflake_client import get_snowflake_conn


def load_parquet_to_table(
    parquet_path: str,
    table_name: str,
    create_table_sql: str,
    truncate_before_load: bool = False,
):
    """
    Load parquet into a Snowflake table. Idempotent when truncate_before_load=True (full refresh).
    """
    conn = get_snowflake_conn()
    cur = conn.cursor()

    # 1. Create table
    cur.execute(create_table_sql)

    # 2. Idempotency: truncate so reruns do not duplicate rows
    if truncate_before_load:
        cur.execute(f"TRUNCATE TABLE IF EXISTS {table_name}")

    # 3. Create temp stage
    cur.execute("CREATE OR REPLACE TEMP STAGE parquet_stage")

    # 4. Upload parquet
    cur.execute(f"PUT file://{parquet_path} @parquet_stage AUTO_COMPRESS=FALSE")

    # 5. Copy into table
    copy_sql = f"""
        COPY INTO {table_name}
        FROM @parquet_stage
        FILE_FORMAT = (TYPE = PARQUET)
        MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE
    """
    cur.execute(copy_sql)

    cur.close()
    conn.close()
