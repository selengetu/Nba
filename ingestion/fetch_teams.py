from nba_api.stats.static import teams
from ingestion.metadata_logger import log_ingestion_run
from ingestion.data_quality import (
    check_not_null,
    check_unique,
    check_row_count,
)
from datetime import datetime
import pandas as pd
import os


def fetch_teams():
    team_data = teams.get_teams()
    df = pd.DataFrame(team_data)

    df = df.rename(columns={
        "id": "team_id",
        "full_name": "team_name"
    })

    df = df[
        [
            "team_id",
            "team_name",
            "city",
            "abbreviation",
            "nickname",
            "year_founded"
        ]
    ]

    df["ingested_at"] = datetime.utcnow()
    return df


if __name__ == "__main__":
    try:
        df = fetch_teams()

        # ✅ Data quality checks
        check_not_null(df, "team_id")
        check_unique(df, "team_id")
        check_row_count(df, min_rows=30)

        os.makedirs("data/raw", exist_ok=True)
        df.to_parquet("data/raw/teams.parquet", index=False)

        # ✅ Log SUCCESS
        log_ingestion_run(
            pipeline_name="nba_ingestion",
            entity_name="dim_teams",
            row_count=len(df),
            status="SUCCESS",
        )

        print(f"Ingested {len(df)} teams")

    except Exception as e:
        # ❌ Log FAILURE
        log_ingestion_run(
            pipeline_name="nba_ingestion",
            entity_name="dim_teams",
            row_count=0,
            status="FAILED",
            error_message=str(e),
        )
        raise
