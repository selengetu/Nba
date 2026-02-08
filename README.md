# 🏀 NBA Data Pipeline – End-to-End Data Engineering Project

This project is a **production-style end-to-end data pipeline** that ingests NBA data from public APIs, applies data quality checks, orchestrates workflows with Apache Airflow, loads data into Snowflake, and transforms it for analytics using dbt.

The focus is on **real-world Data Engineering practices**, not a toy demo.

---

## 🏗 Architecture Overview

```
NBA API
↓
Python Ingestion Layer
• API ingestion, rate limiting, error handling
• Data quality checks, ingestion metadata logging
↓
Parquet (Raw Zone)
↓
Snowflake (RAW schema) — truncate + reload (idempotent)
↓
dbt (staging → marts) — incremental fact supported
↓
Analytics / BI
```

---

## 🔧 Tech Stack

- Python 3
- nba_api
- Pandas / PyArrow
- Apache Airflow (Dockerized)
- Snowflake
- Docker & Docker Compose
- Git
- dbt
- Streamlit
---


## 📥 Data Sources

NBA data is ingested using the official `nba_api` Python package.

### Endpoints Used
- `CommonAllPlayers` → Players dimension
- `teams.get_teams()` → Teams dimension
- `PlayerCareerStats` → Player season statistics (fact table)

---

## 🧱 Data Models

### Dimensions
- `dim_players`
- `dim_teams`
- `dim_seasons`

### Fact Table
- `fact_player_season_stats`

**Grain:** one row per `(player_id, season_id)`

---

## ✅ Data Quality Checks

Data quality is enforced during ingestion:
- Primary key uniqueness
- Not-null constraints
- Minimum row count thresholds
- Graceful handling of partial API failures

Pipelines continue even if individual API calls fail.

---

## 📊 Ingestion Metadata & Observability

Each ingestion run logs metadata including:
- Pipeline name
- Entity name
- Row count
- Status (`SUCCESS` / `FAILED`)
- Error message (if any)
- Run timestamp

Stored as: data/metadata/ingestion_metadata.parquet


This enables monitoring, debugging, and auditing.

---

## ⏱ Workflow Orchestration (Airflow)

Apache Airflow is fully **Dockerized**.

### Idempotency Guard

The DAG includes an **idempotency guard** so reruns don’t duplicate work:

- **Task**: `idempotency_guard` (ShortCircuitOperator) runs first.
- **Logic**: If a **successful** run already exists for the same logical date (execution date), the guard returns `False` and **all downstream tasks are skipped** (ingestion, load, transform).
- **DAG setting**: `max_active_runs=1` so only one run executes at a time.

To force a full re-run for the same date, clear or mark the existing successful run before triggering again.

### DAG Responsibilities

- Run dimension and fact ingestions (PythonOperator)
- Load parquet into Snowflake (truncate + reload)
- Run dbt transform (staging + marts)
- Enforce task dependencies, retries, SLAs

### DAG Flow (TaskGroups)

```
idempotency_guard
       ↓
ingestion: fetch_dim_players, fetch_dim_teams → fetch_fact_player_season_stats → fetch_dim_seasons
       ↓
load: load_dim_players, load_dim_teams, load_dim_seasons, load_fact_player_season_stats
       ↓
transform: dbt_run
```


---

## ❄️ Snowflake Integration

- Raw data is loaded into Snowflake `RAW` schema.
- Tables are created if they do not exist.
- **Idempotent loads**: Each load runs `TRUNCATE TABLE` before `COPY INTO`, so reruns do not create duplicate rows (full refresh per run).
- Snowflake connection is managed via environment variables (`.env`).

---

## 📐 dbt (Transform Layer)

**dbt** runs after the load step and builds the analytics layer in Snowflake.

- **Role**: Transform raw tables in `RAW` into staging views and mart tables (default schema: `ANALYTICS`).
- **Staging**: Views on `RAW` (e.g. `stg_players`, `stg_teams`, `stg_player_season_stats`).
- **Marts**: Tables such as `fact_player_season_stats` (incremental MERGE), `player_season_performance`, `active_players`.
- **Incremental**: `fact_player_season_stats` uses MERGE on `(player_id, season_id, team_id)` and only processes new rows when `ingested_at` is newer than the existing max.

dbt is invoked from the Airflow DAG task `transform.dbt_run`. See `dbt_nba/README.md` for setup, models, and running dbt locally or in Docker.

---


