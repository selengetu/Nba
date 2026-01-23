from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

PROJECT_DIR = "/opt/airflow/nba_project"
VENV_ACTIVATE = f"{PROJECT_DIR}/.venv/bin/activate"

default_args = {
    "owner": "selengetulga",
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="nba_ingestion_pipeline",
    default_args=default_args,
    schedule_interval="0 6 * * *",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["nba", "data-engineering"],
) as dag:

    # ---------- INGESTION ----------
    fetch_players = BashOperator(
        task_id="fetch_dim_players",
        bash_command=f"""
        cd {PROJECT_DIR} &&
        source {VENV_ACTIVATE} &&
        python -m ingestion.fetch_players
        """,
    )

    fetch_teams = BashOperator(
        task_id="fetch_dim_teams",
        bash_command=f"""
        cd {PROJECT_DIR} &&
        source {VENV_ACTIVATE} &&
        python -m ingestion.fetch_teams
        """,
    )

    fetch_player_season_stats = BashOperator(
        task_id="fetch_fact_player_season_stats",
        bash_command=f"""
        cd {PROJECT_DIR} &&
        source {VENV_ACTIVATE} &&
        python -m ingestion.fetch_player_season_stats
        """,
    )

    fetch_seasons = BashOperator(
        task_id="fetch_dim_seasons",
        bash_command=f"""
        cd {PROJECT_DIR} &&
        source {VENV_ACTIVATE} &&
        python -m ingestion.fetch_seasons
        """,
    )

    # ---------- SNOWFLAKE LOAD ----------
    load_dim_players = BashOperator(
        task_id="load_dim_players",
        bash_command=f"""
        cd {PROJECT_DIR} &&
        source {VENV_ACTIVATE} &&
        python -m warehouse.load_dim_players_copy
        """,
    )

    load_dim_teams = BashOperator(
        task_id="load_dim_teams",
        bash_command=f"""
        cd {PROJECT_DIR} &&
        source {VENV_ACTIVATE} &&
        python -m warehouse.load_dim_teams_copy
        """,
    )

    load_dim_seasons = BashOperator(
        task_id="load_dim_seasons",
        bash_command=f"""
        cd {PROJECT_DIR} &&
        source {VENV_ACTIVATE} &&
        python -m warehouse.load_dim_seasons_copy
        """,
    )

    load_fact_player_season_stats = BashOperator(
        task_id="load_fact_player_season_stats",
        bash_command=f"""
        cd {PROJECT_DIR} &&
        source {VENV_ACTIVATE} &&
        python -m warehouse.load_fact_player_season_stats_copy
        """,
    )

    # ---------- DEPENDENCIES ----------
    [fetch_players, fetch_teams] >> fetch_player_season_stats >> fetch_seasons

    fetch_players >> load_dim_players
    fetch_teams >> load_dim_teams
    fetch_seasons >> load_dim_seasons
    fetch_player_season_stats >> load_fact_player_season_stats
