from nba_api.stats.endpoints import drafthistory
from datetime import datetime
import os

from ingestion.metadata_logger import log_ingestion_run
from ingestion.data_quality import check_not_null, check_unique, check_row_count

DAG_ID = "nba_ingestion_pipeline"
TASK_ID = "fetch_dim_draft"


def fetch_draft():
    draft = drafthistory.DraftHistory()
    df = draft.get_data_frames()[0]

    df = df.rename(columns={
        "PERSON_ID": "player_id",
        "PLAYER_NAME": "player_name",
        "SEASON": "draft_year",
        "ROUND_NUMBER": "round_number",
        "ROUND_PICK": "round_pick",
        "OVERALL_PICK": "overall_pick",
        "DRAFT_TYPE": "draft_type",
        "TEAM_ID": "team_id",
        "TEAM_CITY": "team_city",
        "TEAM_NAME": "team_name",
        "TEAM_ABBREVIATION": "team_abbreviation",
        "ORGANIZATION": "organization",
        "ORGANIZATION_TYPE": "organization_type",
        "PLAYER_PROFILE_FLAG": "has_profile",
    })

    df = df[[
        "player_id",
        "player_name",
        "draft_year",
        "round_number",
        "round_pick",
        "overall_pick",
        "draft_type",
        "team_id",
        "team_city",
        "team_name",
        "team_abbreviation",
        "organization",
        "organization_type",
        "has_profile",
    ]]

    df["ingested_at"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    return df


if __name__ == "__main__":
    started_at = datetime.utcnow()

    try:
        df = fetch_draft()

        check_not_null(df, "player_id")
        check_unique(df, "player_id")
        check_row_count(df, min_rows=1000)

        os.makedirs("data/raw", exist_ok=True)
        df.to_parquet("data/raw/draft.parquet", index=False)

        log_ingestion_run(
            pipeline_name=DAG_ID,
            entity_name=TASK_ID,
            row_count=len(df),
            status="SUCCESS",
        )

        print(f"Ingested {len(df)} draft picks")

    except Exception as e:
        log_ingestion_run(
            pipeline_name=DAG_ID,
            entity_name=TASK_ID,
            row_count=0,
            status="FAILED",
            error_message=str(e),
        )
        raise
