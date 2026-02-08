import os
import snowflake.connector
from dotenv import load_dotenv

# Load .env from project root (so it works when Airflow runs from any cwd)
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(_project_root, ".env"))

def get_snowflake_conn():
    required_env_vars = ["SNOWFLAKE_USER", "SNOWFLAKE_PASSWORD", "SNOWFLAKE_ACCOUNT"]
    missing = [v for v in required_env_vars if not os.getenv(v)]
    if missing:
        raise RuntimeError(f"Missing Snowflake env vars: {missing}")

    return snowflake.connector.connect(
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH"),
        database=os.getenv("SNOWFLAKE_DATABASE", "NBA"),
        schema=os.getenv("SNOWFLAKE_SCHEMA", "RAW"),
        role=os.getenv("SNOWFLAKE_ROLE", "ACCOUNTADMIN"),
        session_parameters={"QUERY_TAG": "nba_pipeline_local"},
    )
