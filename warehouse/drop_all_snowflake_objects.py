"""
Drop all NBA pipeline tables in MotherDuck.
After running, re-run ingestion + load to repopulate.
"""
print("drop_all_objects: starting", flush=True)

from warehouse.snowflake_client import get_conn

TABLES = ["DIM_PLAYERS", "DIM_TEAMS", "DIM_SEASONS", "FACT_PLAYER_SEASON_STATS", "INGESTION_METADATA"]


def drop_all():
    print("Connecting to MotherDuck...", flush=True)
    conn = get_conn()
    try:
        for table in TABLES:
            conn.execute(f"DROP TABLE IF EXISTS {table}")
            print(f"Dropped table (if existed): {table}", flush=True)
    finally:
        conn.close()
    print("Done. Re-run ingestion + load to repopulate.", flush=True)


if __name__ == "__main__":
    drop_all()
