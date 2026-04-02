from nba_api.stats.endpoints import playercareerstats
from datetime import datetime
import pandas as pd
import time
import os

from ingestion.data_quality import (
    check_not_null,
    check_row_count,
)
from ingestion.metadata_logger import log_ingestion_run

SLEEP_SECONDS = 1.0


def fetch_player_season_stats(player_ids):
    all_stats = []

    for idx, player_id in enumerate(player_ids, start=1):
        print(f"Fetching player {idx}/{len(player_ids)}: {player_id}")

        retries = 3
        df = None
        for attempt in range(retries):
            try:
                career = playercareerstats.PlayerCareerStats(player_id=player_id)
                df = career.season_totals_regular_season.get_data_frame()
                break
            except (KeyError, Exception) as e:
                if attempt < retries - 1:
                    wait = 10 * (attempt + 1)
                    print(f"  Rate limited on player {player_id}, retrying in {wait}s... ({e})")
                    time.sleep(wait)
                else:
                    print(f"  Skipping player {player_id} after {retries} failed attempts: {e}")

        if df is None or df.empty:
            continue

        df = df.dropna(axis=1, how="all")
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

        df = df[[
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
        ]]

        df["player_id"] = player_id
        df["ingested_at"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        all_stats.append(df)
        time.sleep(SLEEP_SECONDS)

    if not all_stats:
        return pd.DataFrame()

    return pd.concat(all_stats, ignore_index=True)


if __name__ == "__main__":
    try:
        players_df = pd.read_parquet("data/raw/players.parquet")
        active_df = players_df[players_df["is_active"] == 1]
        player_ids = active_df["player_id"].tolist()

        print(f"Fetching stats for {len(player_ids)} active players...")
        df = fetch_player_season_stats(player_ids)

        check_not_null(df, "player_id")
        check_not_null(df, "season_id")
        check_row_count(df, min_rows=50)

        os.makedirs("data/raw", exist_ok=True)
        df.to_parquet("data/raw/player_season_stats.parquet", index=False)

        log_ingestion_run(
            pipeline_name="nba_ingestion",
            entity_name="fact_player_season_stats",
            row_count=len(df),
            status="SUCCESS",
        )

        print(f"Ingested {len(df)} player-season rows")

    except Exception as e:
        log_ingestion_run(
            pipeline_name="nba_ingestion",
            entity_name="fact_player_season_stats",
            row_count=0,
            status="FAILED",
            error_message=str(e),
        )
        raise
