from warehouse.snowflake_loader import load_parquet_to_table


def load_players():
    load_parquet_to_table(
        parquet_path="data/raw/players.parquet",
        table_name="DIM_PLAYERS",
        create_table_sql="""
        CREATE TABLE IF NOT EXISTS DIM_PLAYERS (
            player_id INTEGER,
            full_name VARCHAR,
            player_slug VARCHAR,
            from_year INTEGER,
            to_year INTEGER,
            is_active VARCHAR,
            ingested_at TIMESTAMP
        )
        """,
        truncate_before_load=True,
    )


if __name__ == "__main__":
    load_players()
    print("DIM_PLAYERS loaded")
