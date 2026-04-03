# NBA Data Pipeline – End-to-End Data Engineering Project

This project is a **production-style end-to-end data pipeline** that ingests NBA data from public APIs, applies data quality checks, orchestrates workflows with Apache Airflow, loads data into MotherDuck (DuckDB), and transforms it for analytics using dbt.

The focus is on **real-world Data Engineering practices**

---

## Architecture Overview

```
NBA API
↓
Python Ingestion Layer
• API ingestion, rate limiting, error handling
• Data quality checks, ingestion metadata logging
↓
Parquet (Raw Zone)
↓
MotherDuck / DuckDB (RAW schema) — truncate + reload (idempotent)
↓
dbt (staging → marts) — incremental fact supported
↓
Analytics / BI
```

---

## Tech Stack

- Python 3
- nba_api
- Pandas / PyArrow
- Apache Airflow (Dockerized)
- DuckDB + MotherDuck
- Docker & Docker Compose
- Git
- dbt (dbt-duckdb)
- Streamlit

---

## Data Sources

NBA data is ingested using the official `nba_api` Python package.

### Endpoints Used
- `CommonAllPlayers` → Players dimension
- `teams.get_teams()` → Teams dimension
- `PlayerCareerStats` → Player season statistics (fact table)
- `TeamDetails` → Arenas dimension (arena name, capacity, front office)
- `DraftHistory` → Draft dimension (draft year, round, pick, drafting team)

---

## Data Models

### Dimensions
- `dim_players`
- `dim_teams`
- `dim_seasons`
- `dim_arenas` — arena name, capacity, owner, GM, head coach, G-League affiliate (one row per team)
- `dim_draft` — draft year, round, pick number, drafting team, college/org (one row per drafted player)

### Fact Table
- `fact_player_season_stats`

**Grain:** one row per `(player_id, season_id, team_id)`

---

## Data Quality Checks

Data quality is enforced during ingestion:
- Primary key uniqueness
- Not-null constraints
- Minimum row count thresholds
- Graceful handling of partial API failures

Pipelines continue even if individual API calls fail.

---

## Ingestion Metadata & Observability

Each ingestion run logs metadata including:
- Pipeline name
- Entity name
- Row count
- Status (`SUCCESS` / `FAILED`)
- Error message (if any)
- Run timestamp

Stored as: `data/metadata/ingestion_metadata.parquet`

This enables monitoring, debugging, and auditing.

---

## Workflow Orchestration (Airflow)

Apache Airflow is fully **Dockerized**.

### Idempotency Guard

The DAG includes an **idempotency guard** so reruns don't duplicate work:

- **Task**: `idempotency_guard` (ShortCircuitOperator) runs first.
- **Logic**: If a **successful** run already exists for the same logical date (execution date), the guard returns `False` and **all downstream tasks are skipped** (ingestion, load, transform).
- **DAG setting**: `max_active_runs=1` so only one run executes at a time.

To force a full re-run for the same date, clear or mark the existing successful run before triggering again.

### DAG Responsibilities

- Run dimension and fact ingestions (PythonOperator)
- Load parquet into MotherDuck (truncate + reload)
- Run dbt transform (staging + marts)
- Enforce task dependencies, retries, SLAs

### DAG Flow (TaskGroups)

```
idempotency_guard
       ↓
ingestion:
  fetch_dim_players ──┐
  fetch_dim_teams ────┴──► fetch_fact_player_season_stats ──► fetch_dim_seasons
  fetch_dim_teams ────────► fetch_dim_arenas
  fetch_dim_draft (independent)
       ↓
load: load_dim_players, load_dim_teams, load_dim_seasons, load_fact_player_season_stats,
      load_dim_arenas, load_dim_draft
       ↓
transform: dbt_run
```

---

## MotherDuck (DuckDB) Integration

- Raw data is loaded into MotherDuck `RAW` schema.
- Tables are created if they do not exist.
- **Idempotent loads**: Each load drops and recreates the table before inserting from parquet, so reruns do not create duplicate rows (full refresh per run).
- Connection is managed via environment variables (`.env`).

### Required env vars

```
MOTHERDUCK_TOKEN=<your token>
MOTHERDUCK_DATABASE=nba          # optional, defaults to "nba"
DBT_TARGET_SCHEMA=analytics      # optional, defaults to "analytics"
```

### Reset all tables and re-load raw only

To drop every pipeline table in MotherDuck and then repopulate only raw tables:

1. **Load env** (from project root):
   `set -a && source .env && set +a`

2. **Drop all MotherDuck tables**:
   `python -m warehouse.drop_all_snowflake_objects`

3. **Run ingestion** (writes parquet to `data/raw/`):
   ```
   python -m ingestion.fetch_players
   python -m ingestion.fetch_teams
   python -m ingestion.fetch_player_season_stats
   python -m ingestion.fetch_seasons
   python -m ingestion.fetch_arenas
   python -m ingestion.fetch_draft
   ```
   (Or run the full DAG and stop after the **load** task group.)

4. **Run load** (copy parquet into MotherDuck RAW):
   ```
   python -m warehouse.load_dim_players
   python -m warehouse.load_dim_teams
   python -m warehouse.load_dim_seasons
   python -m warehouse.load_fact_player_season_stats
   python -m warehouse.load_dim_arenas
   python -m warehouse.load_dim_draft
   ```

5. **Verify `ingested_at` in raw**:
   `python -m warehouse.verify_raw_ingested_at`

---

## dbt (Transform Layer)

**dbt** runs after the load step and builds the analytics layer in MotherDuck.

- **Adapter**: `dbt-duckdb`, connecting to MotherDuck via `MOTHERDUCK_TOKEN`.
- **Profile**: `dbt_nba/profiles.yml` — uses `type: duckdb`, path `md:<database>`.
- **Staging**: Views in the `staging` schema (e.g. `stg_players`, `stg_teams`, `stg_player_season_stats`, `stg_seasons`, `stg_arenas`, `stg_draft`).
- **Marts**: Incremental tables in the `marts` schema:
  - `dim_players`, `dim_teams`, `dim_seasons`, `dim_arenas`, `dim_draft` — MERGE on primary key
  - `fact_player_season_stats` — MERGE on `(player_id, season_id, team_id)`
  - `player_season_performance`, `active_players`
- **Incremental**: All mart models use MERGE strategy. Since raw is truncated+reloaded each run, all rows are processed on every run. Use `--full-refresh` to rebuild from scratch.

dbt is invoked from the Airflow DAG task `transform.dbt_run`. Run locally:

```bash
cd dbt_nba
dbt deps
dbt run --profiles-dir .
dbt test --profiles-dir .
dbt docs generate --profiles-dir . && dbt docs serve --profiles-dir .
```

---

## Data Governance

Data governance is implemented across **catalog**, **lineage**, **quality**, **ownership**, and **policies**:

- **Catalog & lineage**: dbt docs (`dbt docs generate && dbt docs serve`), YAML descriptions, ingestion metadata.
- **Quality**: Ingestion checks (`ingestion/data_quality.py`) and dbt tests (`dbt test`).
- **Ownership**: dbt `meta` (owner, tier) and Airflow DAG owner; see generated docs.
- **Policies**: Naming (dim/fact/stg), SLAs on tasks, idempotency (guard + truncate-reload).

See **[docs/DATA_GOVERNANCE.md](docs/DATA_GOVERNANCE.md)** for the full governance guide.
