from warehouse.snowflake_client import get_conn
from datetime import datetime


def log_ingestion(
    table_name: str,
    row_count: int,
    status: str,
    error: str = None,
):
    conn = get_conn()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS INGESTION_METADATA (
                table_name VARCHAR,
                row_count INTEGER,
                status VARCHAR,
                error VARCHAR,
                ingested_at TIMESTAMP
            )
        """)

        conn.execute(
            """
            INSERT INTO INGESTION_METADATA VALUES (?, ?, ?, ?, ?)
            """,
            (table_name, row_count, status, error, datetime.utcnow()),
        )
    finally:
        conn.close()
