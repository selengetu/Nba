"""
Drop all NBA pipeline objects in Snowflake: RAW tables and dbt schemas (ANALYTICS_STAGING, ANALYTICS_MARTS).
Uses same .env as other warehouse scripts (SNOWFLAKE_*, DBT_TARGET_SCHEMA).
After running, re-run ingestion + load to repopulate RAW only; then you can verify ingested_at in raw tables.
"""
import os
import sys

print("drop_all_snowflake_objects: starting", flush=True)
sys.stdout.flush()

from warehouse.snowflake_client import get_snowflake_conn

# Same env as profiles.yml / snowflake_client
DATABASE = os.getenv("SNOWFLAKE_DATABASE", "NBA")
RAW_SCHEMA = os.getenv("SNOWFLAKE_SCHEMA", "RAW")
TARGET_SCHEMA = os.getenv("DBT_TARGET_SCHEMA", "ANALYTICS")
STAGING_SCHEMA = f"{TARGET_SCHEMA}_STAGING"
MARTS_SCHEMA = f"{TARGET_SCHEMA}_MARTS"

RAW_TABLES = ["DIM_PLAYERS", "DIM_TEAMS", "DIM_SEASONS", "FACT_PLAYER_SEASON_STATS"]


def drop_all():
    print("Connecting to Snowflake...", flush=True)
    conn = get_snowflake_conn()
    cur = conn.cursor()

    # 1. Drop dbt schemas (views + tables)
    for schema in (MARTS_SCHEMA, STAGING_SCHEMA):
        cur.execute(f"DROP SCHEMA IF EXISTS {DATABASE}.{schema} CASCADE")
        print(f"Dropped schema (if existed): {DATABASE}.{schema}", flush=True)

    # 2. Drop raw tables
    for table in RAW_TABLES:
        cur.execute(f"DROP TABLE IF EXISTS {DATABASE}.{RAW_SCHEMA}.{table}")
        print(f"Dropped table (if existed): {DATABASE}.{RAW_SCHEMA}.{table}", flush=True)

    cur.close()
    conn.close()
    print("Done. Re-run ingestion + load to repopulate RAW; then query raw tables to verify ingested_at.", flush=True)


if __name__ == "__main__":
    drop_all()
