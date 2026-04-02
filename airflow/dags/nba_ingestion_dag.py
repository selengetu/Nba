import os
import runpy
import sys
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator, ShortCircuitOperator
from airflow.utils.task_group import TaskGroup

PROJECT_DIR = "/opt/airflow/nba_project"


def run_python_module(module_name: str, **context):
    """Run a project module as __main__ (same as python -m module_name)."""
    if PROJECT_DIR not in sys.path:
        sys.path.insert(0, PROJECT_DIR)
    os.chdir(PROJECT_DIR)
    runpy.run_module(module_name, run_name="__main__")


def idempotency_guard(**context):
    """
    Skip this run if the same logical date already completed successfully (prevents duplicate work on re-triggers).
    Returns False to short-circuit downstream tasks, True to proceed.
    """
    from airflow.models import DagRun
    from airflow.utils.session import provide_session

    logical_date = context["logical_date"]
    dag_id = context["dag"].dag_id

    @provide_session
    def _already_succeeded(session=None):
        run = (
            session.query(DagRun)
            .filter(
                DagRun.dag_id == dag_id,
                DagRun.execution_date == logical_date,
                DagRun.state == "success",
            )
            .first()
        )
        return run is not None

    if _already_succeeded():
        return False  # Skip: already succeeded for this date
    return True  # Proceed


default_args = {
    "owner": "selengetulga",
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="nba_ingestion_pipeline",
    default_args=default_args,
    schedule="0 6 * * *",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    max_active_runs=1,  # Idempotency: only one run at a time, no overlapping execution
    tags=["nba", "data-engineering"],
) as dag:

    # Idempotency guard: skip ingestion/load/transform if this logical date already succeeded
    guard = ShortCircuitOperator(
        task_id="idempotency_guard",
        python_callable=idempotency_guard,
    )

    with TaskGroup("ingestion", tooltip="Fetch from NBA API to raw parquet") as ingestion:
        fetch_players = PythonOperator(
            task_id="fetch_dim_players",
            python_callable=run_python_module,
            op_kwargs={"module_name": "ingestion.fetch_players"},
            sla=timedelta(minutes=10),
        )
        fetch_teams = PythonOperator(
            task_id="fetch_dim_teams",
            python_callable=run_python_module,
            op_kwargs={"module_name": "ingestion.fetch_teams"},
            sla=timedelta(minutes=10),
        )
        fetch_player_season_stats = PythonOperator(
            task_id="fetch_fact_player_season_stats",
            python_callable=run_python_module,
            op_kwargs={"module_name": "ingestion.fetch_player_season_stats"},
            sla=timedelta(minutes=15),  # Larger dataset, longer SLA
        )
        fetch_seasons = PythonOperator(
            task_id="fetch_dim_seasons",
            python_callable=run_python_module,
            op_kwargs={"module_name": "ingestion.fetch_seasons"},
            sla=timedelta(minutes=5),  # Small dataset
        )
        [fetch_players, fetch_teams] >> fetch_player_season_stats >> fetch_seasons

    guard >> [fetch_players, fetch_teams]  # Guard must pass before any ingestion

    with TaskGroup("load", tooltip="Load raw parquet into Snowflake") as load:
        load_dim_players = PythonOperator(
            task_id="load_dim_players",
            python_callable=run_python_module,
            op_kwargs={"module_name": "warehouse.load_dim_players"},
            sla=timedelta(minutes=15),
        )
        load_dim_teams = PythonOperator(
            task_id="load_dim_teams",
            python_callable=run_python_module,
            op_kwargs={"module_name": "warehouse.load_dim_teams"},
            sla=timedelta(minutes=10),
        )
        load_dim_seasons = PythonOperator(
            task_id="load_dim_seasons",
            python_callable=run_python_module,
            op_kwargs={"module_name": "warehouse.load_dim_seasons"},
            sla=timedelta(minutes=10),
        )
        load_fact_player_season_stats = PythonOperator(
            task_id="load_fact_player_season_stats",
            python_callable=run_python_module,
            op_kwargs={"module_name": "warehouse.load_fact_player_season_stats"},
            sla=timedelta(minutes=20),  # Largest fact table
        )

    with TaskGroup("transform", tooltip="dbt models (staging + marts)") as transform:
        # Note: fact_player_season_stats is incremental (MERGE strategy).
        # Since raw is truncated+reloaded, incremental will process all rows each run (merge/update).
        # To force full refresh: add --full-refresh flag to dbt run command.
        dbt_run = BashOperator(
            task_id="dbt_run",
            bash_command=f"""
            cd {PROJECT_DIR}/dbt_nba &&
            dbt deps 2>/dev/null || true &&
            dbt run --profiles-dir . --no-partial-parse
            """,
            sla=timedelta(minutes=30),  # dbt can take time with multiple models
        )

    # ---------- CROSS-GROUP DEPENDENCIES ----------
    fetch_players >> load_dim_players
    fetch_teams >> load_dim_teams
    fetch_seasons >> load_dim_seasons
    fetch_player_season_stats >> load_fact_player_season_stats

    [load_dim_players, load_dim_teams, load_dim_seasons, load_fact_player_season_stats] >> dbt_run
