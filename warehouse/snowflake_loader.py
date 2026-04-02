import os
from warehouse.snowflake_client import get_conn


def load_parquet_to_table(
    parquet_path: str,
    table_name: str,
    create_table_sql: str,
    truncate_before_load: bool = False,
):
    """
    Load a parquet file into a MotherDuck table. Idempotent when truncate_before_load=True.
    """
    conn = get_conn()
    try:
        conn.execute(create_table_sql)
        if truncate_before_load:
            conn.execute(f"DELETE FROM {table_name}")
        abs_path = os.path.abspath(parquet_path)
        conn.execute(
            f"INSERT INTO {table_name} SELECT * FROM read_parquet(?)", [abs_path]
        )
    finally:
        conn.close()
