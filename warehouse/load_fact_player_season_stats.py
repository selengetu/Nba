from warehouse.snowflake_loader import load_parquet_to_table


def load_fact_player_season_stats():
    load_parquet_to_table(
        parquet_path="data/raw/player_season_stats.parquet",
        table_name="FACT_PLAYER_SEASON_STATS",
        create_table_sql="""
        CREATE TABLE IF NOT EXISTS FACT_PLAYER_SEASON_STATS (
            player_id INTEGER,
            season_id VARCHAR,
            team_id INTEGER,
            games_played INTEGER,
            minutes DOUBLE,
            points DOUBLE,
            rebounds DOUBLE,
            assists DOUBLE,
            steals DOUBLE,
            blocks DOUBLE,
            turnovers DOUBLE,
            fg_pct DOUBLE,
            fg3_pct DOUBLE,
            ft_pct DOUBLE,
            ingested_at TIMESTAMP
        )
        """,
        truncate_before_load=True,  # Idempotent: full refresh, no duplicates on rerun
    )

if __name__ == "__main__":
    load_fact_player_season_stats()
