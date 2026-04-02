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
        abs_path = os.path.abspath(parquet_path)
        schema = table_name.split(".")[0] if "." in table_name else None
        if schema:
            conn.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")
        if truncate_before_load:
            # Drop and recreate to ensure schema is always up to date
            conn.execute(f"DROP TABLE IF EXISTS {table_name}")
        conn.execute(create_table_sql)
        # Use explicit column list from parquet for name-based (not positional) mapping
        cols = conn.execute(
            f"SELECT * FROM read_parquet(?) LIMIT 0", [abs_path]
        ).description
        col_list = ", ".join(f'"{c[0]}"' for c in cols)
        conn.execute(
            f"INSERT INTO {table_name} ({col_list}) SELECT {col_list} FROM read_parquet(?)",
            [abs_path],
        )
    finally:
        conn.close()
