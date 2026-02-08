# dbt NBA – Transform layer

Runs **after** Airflow loads raw data into Snowflake (`RAW` schema). Builds staging views and mart tables in the target schema (default: `ANALYTICS`).

## Setup

- Uses same env vars as the rest of the project: `SNOWFLAKE_USER`, `SNOWFLAKE_PASSWORD`, `SNOWFLAKE_ACCOUNT`, `SNOWFLAKE_WAREHOUSE`, `SNOWFLAKE_DATABASE`, `SNOWFLAKE_SCHEMA` (for **sources** = raw tables), `SNOWFLAKE_ROLE`.
- Optional: `DBT_TARGET_SCHEMA` (default `ANALYTICS`) – schema where dbt writes models.

## Run locally

```bash
cd dbt_nba
export DBT_PROFILES_DIR=.
dbt deps
dbt run
dbt test   # optional
```

## In the pipeline

The Airflow DAG runs `dbt run` after all four load tasks complete. Staging models are views; marts are tables.
