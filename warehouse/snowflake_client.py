import os
import duckdb
from dotenv import load_dotenv

_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(_project_root, ".env"))


def get_conn():
    token = os.getenv("MOTHERDUCK_TOKEN")
    if not token:
        raise RuntimeError("Missing env var: MOTHERDUCK_TOKEN")
    database = os.getenv("MOTHERDUCK_DATABASE", "nba")
    return duckdb.connect(f"md:{database}?motherduck_token={token}")


# Backward-compat alias
get_snowflake_conn = get_conn
