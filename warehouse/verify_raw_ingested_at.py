"""
Quick check that tables have ingested_at populated after load.
Run from project root (so .env is available).
"""
from warehouse.snowflake_client import get_conn

TABLES = ["DIM_PLAYERS", "DIM_TEAMS", "DIM_SEASONS", "FACT_PLAYER_SEASON_STATS"]


def verify():
    conn = get_conn()
    try:
        for table in TABLES:
            try:
                rows = conn.execute(
                    f"SELECT ingested_at FROM {table} LIMIT 3"
                ).fetchall()
                print(f"{table}: ingested_at sample = {rows}")
            except Exception as e:
                print(f"{table}: error - {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    verify()
