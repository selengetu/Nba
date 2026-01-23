from datetime import datetime
import pandas as pd
import os

from ingestion.data_quality import (
    check_not_null,
    check_unique,
    check_row_count,
)
from ingestion.metadata_logger import log_ingestion_run


def derive_seasons(player_season_stats_path: str) -> pd.DataFrame:
    df = pd.read_parquet(player_season_stats_path)

    seasons = (
        df[["season_id"]]
        .drop_duplicates()
        .dropna()
        .sort_values("season_id")
        .reset_index(drop=True)
    )

    # Split season_id like "2023-24"
    seasons["season_start_year"] = seasons["season_id"].str[:4].astype(int)
    seasons["season_end_year"] = seasons["season_start_year"] + 1

    seasons["season_label"] = (
        seasons["season_start_year"].astype(str)
        + "–"
        + seasons["season_end_year"].astype(str)
    )

    seasons["ingested_at"] = datetime.utcnow()
    return seasons


if __name__ == "__main__":
    try:
        df = derive_seasons("data/raw/player_season_stats.parquet")

        # ✅ Data quality checks
        check_not_null(df, "season_id")
        check_unique(df, "season_id")
        check_row_count(df, min_rows=5)

        os.makedirs("data/raw", exist_ok=True)
        df.to_parquet("data/raw/seasons.parquet", index=False)

        # ✅ Log SUCCESS
        log_ingestion_run(
            pipeline_name="nba_ingestion",
            entity_name="dim_seasons",
            row_count=len(df),
            status="SUCCESS",
        )

        print(f"Ingested {len(df)} seasons")

    except Exception as e:
        # ❌ Log FAILURE
        log_ingestion_run(
            pipeline_name="nba_ingestion",
            entity_name="dim_seasons",
            row_count=0,
            status="FAILED",
            error_message=str(e),
        )
        raise
