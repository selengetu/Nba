from nba_api.stats.endpoints import teamdetails
from nba_api.stats.static import teams as nba_teams
from datetime import datetime
import pandas as pd
import os
import time

from ingestion.metadata_logger import log_ingestion_run
from ingestion.data_quality import check_not_null, check_unique, check_row_count

DAG_ID = "nba_ingestion_pipeline"
TASK_ID = "fetch_dim_arenas"


def fetch_arenas():
    all_teams = nba_teams.get_teams()
    records = []

    for team in all_teams:
        try:
            details = teamdetails.TeamDetails(team_id=team["id"])
            background = details.team_background.get_data_frame()
            if not background.empty:
                row = background.iloc[0]
                records.append({
                    "team_id": int(team["id"]),
                    "arena_name": row.get("ARENA"),
                    "arena_capacity": row.get("ARENACAPACITY"),
                    "owner": row.get("OWNER"),
                    "general_manager": row.get("GENERALMANAGER"),
                    "head_coach": row.get("HEADCOACH"),
                    "dleague_affiliation": row.get("DLEAGUEAFFILIATION"),
                })
            time.sleep(0.6)  # respect rate limit
        except Exception:
            time.sleep(1)
            continue

    df = pd.DataFrame(records)
    df["ingested_at"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    return df


if __name__ == "__main__":
    started_at = datetime.utcnow()

    try:
        df = fetch_arenas()

        check_not_null(df, "team_id")
        check_unique(df, "team_id")
        check_row_count(df, min_rows=28)

        os.makedirs("data/raw", exist_ok=True)
        df.to_parquet("data/raw/arenas.parquet", index=False)

        log_ingestion_run(
            pipeline_name=DAG_ID,
            entity_name=TASK_ID,
            row_count=len(df),
            status="SUCCESS",
        )

        print(f"Ingested {len(df)} arenas")

    except Exception as e:
        log_ingestion_run(
            pipeline_name=DAG_ID,
            entity_name=TASK_ID,
            row_count=0,
            status="FAILED",
            error_message=str(e),
        )
        raise
