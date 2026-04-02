from warehouse.snowflake_loader import load_parquet_to_table


def load_dim_teams():
    load_parquet_to_table(
        parquet_path="data/raw/teams.parquet",
        table_name="RAW.DIM_TEAMS",
        create_table_sql="""
        CREATE TABLE IF NOT EXISTS RAW.DIM_TEAMS (
            team_id INTEGER,
            team_name VARCHAR,
            city VARCHAR,
            abbreviation VARCHAR,
            nickname VARCHAR,
            year_founded INTEGER,
            ingested_at TIMESTAMP
        )
        """,
        truncate_before_load=True,  # Idempotent: full refresh, no duplicates on rerun
    )

if __name__ == "__main__":
    load_dim_teams()
