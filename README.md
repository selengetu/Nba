# 🏀 NBA Data Pipeline – End-to-End Data Engineering Project

This project is a **production-style end-to-end data pipeline** that ingests NBA data from public APIs, applies data quality checks, orchestrates workflows with Apache Airflow, loads data into Snowflake, and prepares it for analytics using dbt (next step).

The focus is on **real-world Data Engineering practices**, not a toy demo.

---

## 🏗 Architecture Overview

BA API
↓
Python Ingestion Layer
• API ingestion
• Rate limiting
• Error handling
• Data quality checks
• Ingestion metadata logging
↓
Parquet (Raw Zone)
↓
Snowflake (RAW schema)
↓
dbt (staging → marts) [next]
↓
Analytics / BI

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

### DAG Responsibilities
- Run dimension ingestions
- Run fact ingestion
- Enforce task dependencies
- Handle retries
- Prepare data for downstream transformations

### DAG Flow
fetch_dim_players
fetch_dim_teams
↓
fetch_fact_player_season_stats
↓
fetch_dim_seasons


---

## ❄️ Snowflake Integration

- Raw data is loaded into Snowflake `RAW` schema
- Tables are created if they do not exist
- Python loaders insert data from Parquet files

Snowflake connection is managed via environment variables.

---


