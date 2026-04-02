from warehouse.snowflake_loader import load_parquet_to_table


def load_dim_seasons():
    load_parquet_to_table(
        parquet_path="data/raw/seasons.parquet",
        table_name="DIM_SEASONS",
        create_table_sql="""
        CREATE TABLE IF NOT EXISTS DIM_SEASONS (
            season_id VARCHAR,
            season_start_year INTEGER,
            season_end_year INTEGER,
            season_label VARCHAR,
            ingested_at TIMESTAMP
        )
        """,
        truncate_before_load=True,  # Idempotent: full refresh, no duplicates on rerun
    )

if __name__ == "__main__":
    load_dim_seasons()
