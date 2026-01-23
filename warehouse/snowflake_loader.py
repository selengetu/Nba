import pandas as pd
from warehouse.snowflake_client import get_snowflake_conn

def load_parquet_to_table(
    parquet_path: str,
    table_name: str,
    create_table_sql: str,
):
    conn = get_snowflake_conn()
    cur = conn.cursor()

    # 1. Create table
    cur.execute(create_table_sql)

    # 2. Create temp stage
    cur.execute("CREATE OR REPLACE TEMP STAGE parquet_stage")

    # 3. Upload parquet
    cur.execute(f"PUT file://{parquet_path} @parquet_stage AUTO_COMPRESS=FALSE")

    # 4. Copy into table
    copy_sql = f"""
        COPY INTO {table_name}
        FROM @parquet_stage
        FILE_FORMAT = (TYPE = PARQUET)
        MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE
    """
    cur.execute(copy_sql)

    cur.close()
    conn.close()
