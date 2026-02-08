import pandas as pd
from warehouse.snowflake_client import get_snowflake_conn
import os
import tempfile


def load_players_copy():
    df = pd.read_parquet("data/raw/players.parquet")

    conn = get_snowflake_conn()
    cursor = conn.cursor()

    # Create table (idempotent)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS DIM_PLAYERS (
            player_id INTEGER,
            full_name STRING,
            player_slug STRING,
            from_year INTEGER,
            to_year INTEGER,
            is_active STRING,
            ingested_at TIMESTAMP
        )
    """)

    # Idempotency: truncate so reruns do not duplicate rows
    cursor.execute("TRUNCATE TABLE IF EXISTS DIM_PLAYERS")

    # Write parquet to temp file
    with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as tmp:
        df.to_parquet(tmp.name, index=False)
        parquet_path = tmp.name

    # Upload to Snowflake stage
    cursor.execute(f"PUT file://{parquet_path} @NBA_STAGE AUTO_COMPRESS=TRUE")

    # Load into table
    cursor.execute("""
        COPY INTO DIM_PLAYERS
        FROM @NBA_STAGE
        FILE_FORMAT = (TYPE = PARQUET)
        MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE
    """)

    os.remove(parquet_path)

    cursor.close()
    conn.close()


if __name__ == "__main__":
    load_players_copy()
    print("DIM_PLAYERS loaded via COPY INTO")
