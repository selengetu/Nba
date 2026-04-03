from warehouse.snowflake_loader import load_parquet_to_table


def load_arenas():
    load_parquet_to_table(
        parquet_path="data/raw/arenas.parquet",
        table_name="RAW.DIM_ARENAS",
        create_table_sql="""
        CREATE TABLE IF NOT EXISTS RAW.DIM_ARENAS (
            team_id INTEGER,
            arena_name VARCHAR,
            arena_capacity VARCHAR,
            owner VARCHAR,
            general_manager VARCHAR,
            head_coach VARCHAR,
            dleague_affiliation VARCHAR,
            ingested_at TIMESTAMP
        )
        """,
        truncate_before_load=True,
    )


if __name__ == "__main__":
    load_arenas()
    print("DIM_ARENAS loaded")
