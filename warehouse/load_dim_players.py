import pandas as pd
from warehouse.snowflake_client import get_snowflake_conn


def load_players():
    df = pd.read_parquet("data/raw/players.parquet")

    conn = get_snowflake_conn()
    cursor = conn.cursor()

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

    for _, row in df.iterrows():
        cursor.execute(
            """
            INSERT INTO DIM_PLAYERS VALUES (%s,%s,%s,%s,%s,%s,%s)
            """,
            tuple(row),
        )

    cursor.close()
    conn.close()
