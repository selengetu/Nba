"""
Quick check that raw tables have ingested_at populated after load.
Run from project root (so .env and warehouse are available).
"""
import os
from warehouse.snowflake_client import get_snowflake_conn

DATABASE = os.getenv("SNOWFLAKE_DATABASE", "NBA")
RAW_SCHEMA = os.getenv("SNOWFLAKE_SCHEMA", "RAW")


def verify():
    conn = get_snowflake_conn()
    cur = conn.cursor()
    for table in ["DIM_PLAYERS", "DIM_TEAMS", "DIM_SEASONS", "FACT_PLAYER_SEASON_STATS"]:
        try:
            cur.execute(
                f"SELECT ingested_at FROM {DATABASE}.{RAW_SCHEMA}.{table} LIMIT 3"
            )
            rows = cur.fetchall()
            print(f"{table}: ingested_at sample = {rows}")
        except Exception as e:
            print(f"{table}: error - {e}")
    cur.close()
    conn.close()


if __name__ == "__main__":
    verify()
