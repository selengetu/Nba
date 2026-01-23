from warehouse.snowflake_client import get_snowflake_conn
from datetime import datetime

def log_ingestion(
    table_name: str,
    row_count: int,
    status: str,
    error: str = None,
):
    conn = get_snowflake_conn()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS INGESTION_METADATA (
            table_name STRING,
            row_count INTEGER,
            status STRING,
            error STRING,
            ingested_at TIMESTAMP
        )
    """)

    cur.execute(
        """
        INSERT INTO INGESTION_METADATA
        VALUES (%s, %s, %s, %s, %s)
        """,
        (table_name, row_count, status, error, datetime.utcnow()),
    )

    cur.close()
    conn.close()
