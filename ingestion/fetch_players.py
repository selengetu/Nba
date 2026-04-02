from nba_api.stats.endpoints import commonallplayers
from datetime import datetime
import os

from ingestion.metadata_logger import log_ingestion_run
from ingestion.data_quality import (
    check_not_null,
    check_unique,
    check_row_count,
)

DAG_ID = "nba_ingestion_pipeline"
TASK_ID = "fetch_dim_players"


def fetch_players():
    players = commonallplayers.CommonAllPlayers(is_only_current_season=0)
    df = players.get_data_frames()[0]

    df = df.rename(columns={
        "PERSON_ID": "player_id",
        "DISPLAY_FIRST_LAST": "full_name",
        "FROM_YEAR": "from_year",
        "TO_YEAR": "to_year",
        "ROSTERSTATUS": "is_active",
        "PLAYER_SLUG": "player_slug"
    })

    df = df[
        [
            "player_id",
            "full_name",
            "player_slug",
            "from_year",
            "to_year",
            "is_active"
        ]
    ]

    df["ingested_at"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    return df


if __name__ == "__main__":
    started_at = datetime.utcnow()

    try:
        df = fetch_players()

        # Data quality
        check_not_null(df, "player_id")
        check_unique(df, "player_id")
        check_row_count(df, min_rows=4000)

        os.makedirs("data/raw", exist_ok=True)
        df.to_parquet("data/raw/players.parquet", index=False)

        log_ingestion_run(
            pipeline_name=DAG_ID,
            entity_name=TASK_ID,
            row_count=len(df),
            status="SUCCESS",
        )

        print(f"Ingested {len(df)} players")

    except Exception as e:
        log_ingestion_run(
            pipeline_name=DAG_ID,
            entity_name=TASK_ID,
            row_count=0,
            status="FAILED",
            error_message=str(e),
        )
        raise

