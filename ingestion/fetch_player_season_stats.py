from nba_api.stats.endpoints import playercareerstats
from datetime import datetime
import pandas as pd
import time
import os

from ingestion.data_quality import (
    check_not_null,
    check_unique,
    check_row_count,
)
from ingestion.metadata_logger import log_ingestion_run

# TEMP LIMIT for safety
MAX_PLAYERS = 20
SLEEP_SECONDS = 0.7


def fetch_player_season_stats(player_ids):
    all_stats = []

    for idx, player_id in enumerate(player_ids[:MAX_PLAYERS], start=1):
        print(f"Fetching player {idx}/{len(player_ids[:MAX_PLAYERS])}: {player_id}")

        career = playercareerstats.PlayerCareerStats(player_id=player_id)

        # Regular season totals
        df = career.season_totals_regular_season.get_data_frame()

        if df.empty:
            continue

        df = df.dropna(axis=1, how="all")  # prevent future concat issues
        df["player_id"] = player_id
        df["ingested_at"] = datetime.utcnow()

        all_stats.append(df)

        time.sleep(SLEEP_SECONDS)

    if not all_stats:
        return pd.DataFrame()

    return pd.concat(all_stats, ignore_index=True)


if __name__ == "__main__":
    try:
        # Load players dimension
        players_df = pd.read_parquet("data/raw/players.parquet")
        player_ids = players_df["player_id"].tolist()

        df = fetch_player_season_stats(player_ids)

        # Rename & select columns
        df = df.rename(columns={
            "SEASON_ID": "season_id",
            "TEAM_ID": "team_id",
            "GP": "games_played",
            "MIN": "minutes",
            "PTS": "points",
            "REB": "rebounds",
            "AST": "assists",
            "STL": "steals",
            "BLK": "blocks",
            "TOV": "turnovers",
            "FG_PCT": "fg_pct",
            "FG3_PCT": "fg3_pct",
            "FT_PCT": "ft_pct",
        })

        df = df[
            [
                "player_id",
                "season_id",
                "team_id",
                "games_played",
                "minutes",
                "points",
                "rebounds",
                "assists",
                "steals",
                "blocks",
                "turnovers",
                "fg_pct",
                "fg3_pct",
                "ft_pct",
                "ingested_at",
            ]
        ]

        # ✅ Data quality checks
        check_not_null(df, "player_id")
        check_not_null(df, "season_id")
        check_row_count(df, min_rows=50)

        os.makedirs("data/raw", exist_ok=True)
        df.to_parquet("data/raw/player_season_stats.parquet", index=False)

        # ✅ Log SUCCESS
        log_ingestion_run(
            pipeline_name="nba_ingestion",
            entity_name="fact_player_season_stats",
            row_count=len(df),
            status="SUCCESS",
        )

        print(f"Ingested {len(df)} player-season rows")

    except Exception as e:
        # ❌ Log FAILURE
        log_ingestion_run(
            pipeline_name="nba_ingestion",
            entity_name="fact_player_season_stats",
            row_count=0,
            status="FAILED",
            error_message=str(e),
        )
        raise
