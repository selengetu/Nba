FROM apache/airflow:2.8.4

# Switch to airflow user (IMPORTANT)
USER airflow

# Install Python dependencies required by your DAGs
RUN pip install --no-cache-dir \
    nba_api \
    pandas \
    pyarrow \
    snowflake-connector-python


