# dbt NBA – Transform Layer

Runs **after** Airflow loads raw data into Snowflake (`RAW` schema). Builds staging views and mart tables in the target schema (default: `ANALYTICS`).

## Pipeline Flow

```
NBA API → Ingestion (parquet) → Snowflake RAW → dbt Transform → ANALYTICS (marts)
```

1. **Ingestion**: Fetch from NBA API, write to `data/raw/*.parquet`
2. **Load**: Copy parquet into Snowflake `RAW` schema (with truncate for idempotency)
3. **Transform (dbt)**: Build staging views and marts in `ANALYTICS` schema

## Idempotency Guards

### DAG-Level Guard (`idempotency_guard` task)

The Airflow DAG includes an **idempotency guard** that prevents duplicate work:

- **Checks**: If a successful DAG run already exists for the same logical date (execution date)
- **Action**: If yes → **short-circuits** (skips all downstream tasks: ingestion, load, transform)
- **Action**: If no → **proceeds** normally

**Why**: Prevents re-triggering the same date from duplicating data or wasting compute.

**DAG config**: `max_active_runs=1` ensures only one run executes at a time (no overlapping runs).

### Load-Level Idempotency

All Snowflake load tasks use **truncate + reload**:

- `TRUNCATE TABLE` before `COPY INTO`
- Ensures reruns don't create duplicate rows
- Full refresh approach (safe and simple)

**Tables protected**: `DIM_PLAYERS`, `DIM_TEAMS`, `DIM_SEASONS`, `FACT_PLAYER_SEASON_STATS`

## Setup

### Environment Variables

Uses same env vars as the rest of the project (from `.env`):

- `SNOWFLAKE_USER`, `SNOWFLAKE_PASSWORD`, `SNOWFLAKE_ACCOUNT`
- `SNOWFLAKE_WAREHOUSE` (default: `COMPUTE_WH`)
- `SNOWFLAKE_DATABASE` (default: `NBA`)
- `SNOWFLAKE_SCHEMA` (default: `RAW`) – used for **sources** (raw tables)
- `SNOWFLAKE_ROLE` (default: `ACCOUNTADMIN`)
- `DBT_TARGET_SCHEMA` (default: `ANALYTICS`) – schema where dbt writes models

### Profiles

`profiles.yml` reads from environment variables using Jinja templating:

```yaml
account: "{{ env_var('SNOWFLAKE_ACCOUNT') }}"
user: "{{ env_var('SNOWFLAKE_USER') }}"
password: "{{ env_var('SNOWFLAKE_PASSWORD') }}"
```

## Model Structure

### Staging (`staging` schema)

**Views** that read from raw tables in `RAW` schema:

- `stg_players` → `RAW.DIM_PLAYERS`
- `stg_teams` → `RAW.DIM_TEAMS`
- `stg_seasons` → `RAW.DIM_SEASONS`
- `stg_player_season_stats` → `RAW.FACT_PLAYER_SEASON_STATS`

### Marts (`marts` schema)

**Tables** for analytics:

- **`fact_player_season_stats`** (incremental)
  - MERGE strategy on `(player_id, season_id, team_id)`
  - Clustered by `season_id` for performance
  - Only processes new rows: `ingested_at > max(ingested_at)`
  - See [marts/README.md](models/marts/README.md) for details

- **`player_season_performance`** (table)
  - Analytics-ready: joins fact with dims (players, teams, seasons)
  - Includes calculated fields (e.g. PPG)
  - Reads from `fact_player_season_stats`

- **`active_players`** (table)
  - Convenience mart: current active players only

## Usage

### Run Locally

```bash
cd dbt_nba
export DBT_PROFILES_DIR=.
dbt deps                    # Install dependencies (if any)
dbt run                    # Run all models
dbt run --select fact_player_season_stats  # Run specific model
dbt test                   # Run tests (if defined)
```

### In Docker (same as Airflow)

```bash
docker compose run --rm airflow-scheduler bash -c \
  "cd /opt/airflow/nba_project/dbt_nba && \
   dbt run --profiles-dir ."
```

### Incremental vs Full Refresh

**Incremental (default)**:
```bash
dbt run --select fact_player_season_stats
```

**Full refresh** (when needed):
```bash
dbt run --select fact_player_season_stats --full-refresh
```

**When to use full refresh**:
- First run (table doesn't exist)
- Schema changes (new columns)
- Data quality issues requiring reprocessing
- When raw tables are truncated+reloaded (current setup processes all rows anyway)

## In the Pipeline

The Airflow DAG (`nba_ingestion_pipeline`) runs dbt after all four load tasks complete:

1. **Ingestion** → Fetch from NBA API
2. **Load** → Copy to Snowflake RAW (with truncate)
3. **Transform** → `dbt run` (builds staging + marts)

**Task**: `transform.dbt_run` runs:
```bash
cd /opt/airflow/nba_project/dbt_nba
dbt deps 2>/dev/null || true
dbt run --profiles-dir .
```

**Note**: Since raw tables are truncated+reloaded, the incremental fact model will process all rows each run (because `ingested_at` is newer). This is fine—MERGE updates existing rows and inserts new ones. When raw becomes truly incremental (append-only), dbt will automatically process only new rows.

## Project Structure

```
dbt_nba/
├── dbt_project.yml          # Project config
├── profiles.yml             # Snowflake connection (env vars)
├── models/
│   ├── sources.yml          # Raw table definitions
│   ├── staging/             # Views on raw
│   │   ├── stg_players.sql
│   │   ├── stg_teams.sql
│   │   ├── stg_seasons.sql
│   │   └── stg_player_season_stats.sql
│   └── marts/               # Analytics tables
│       ├── fact_player_season_stats.sql  # Incremental
│       ├── player_season_performance.sql
│       ├── active_players.sql
│       └── README.md
└── README.md                # This file
```
