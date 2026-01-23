from warehouse.snowflake_loader import load_parquet_to_table

def load_fact_player_season_stats():
    load_parquet_to_table(
        parquet_path="data/raw/player_season_stats.parquet",
        table_name="FACT_PLAYER_SEASON_STATS",
        create_table_sql="""
        CREATE TABLE IF NOT EXISTS FACT_PLAYER_SEASON_STATS (
            player_id INTEGER,
            season_id STRING,
            team_id INTEGER,
            games_played INTEGER,
            minutes FLOAT,
            points FLOAT,
            rebounds FLOAT,
            assists FLOAT,
            steals FLOAT,
            blocks FLOAT,
            turnovers FLOAT,
            fg_pct FLOAT,
            fg3_pct FLOAT,
            ft_pct FLOAT,
            ingested_at TIMESTAMP
        )
        """
    )

if __name__ == "__main__":
    load_fact_player_season_stats()
