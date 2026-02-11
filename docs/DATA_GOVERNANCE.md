# Data Governance – NBA Pipeline

This document describes how **data governance** is implemented and how to extend it: catalog, lineage, quality, ownership, security, and policies.

---

## 1. Data catalog & discoverability

**Goal:** One place to see what data exists, where it lives, and what it means.

| Mechanism | What it does |
|-----------|----------------|
| **dbt docs** | Generated catalog: models, sources, columns, descriptions, types. Run `dbt docs generate && dbt docs serve`. |
| **YAML descriptions** | `sources.yml`, `models/*/schema.yml`: table and column descriptions (business meaning). |
| **Ingestion metadata** | `data/metadata/ingestion_metadata.parquet`: pipeline name, entity, row count, status, run time. |

**How to improve:**  
- Publish `dbt docs` (e.g. CI → S3/GitHub Pages) as the single “data catalog” entry point.  
- Add a **glossary** (e.g. `docs/glossary.md`) for terms like `season_id`, `player_slug`, grain of fact tables.

---

## 2. Lineage

**Goal:** Trace where data comes from and what depends on it.

| Mechanism | What it does |
|-----------|----------------|
| **dbt lineage** | In `dbt docs`, the DAG shows: sources → staging → marts. |
| **Airflow DAG** | Task graph shows: ingestion → load → dbt. |
| **dbt `ref()` / `source()`** | Code-level lineage; dbt compiles this into the docs graph. |

**How to improve:**  
- Add **column-level lineage** (dbt can expose this in docs when column names align).  
- Optional: push dbt manifest to a lineage tool (e.g. OpenLineage, Atlan) for cross-system lineage.

---

## 3. Data quality

**Goal:** Define and enforce rules; monitor and alert.

| Layer | What’s in place |
|-------|------------------|
| **Ingestion** | `ingestion/data_quality.py`: `check_not_null`, `check_unique`, `check_row_count` before writing parquet. |
| **Transform (dbt)** | Schema tests in `models/*/schema.yml`: `unique`, `not_null`, `relationships`. Run `dbt test`. |
| **Observability** | Ingestion metadata logs success/failure and row counts; Airflow logs and SLAs. |

**How to improve:**  
- Run `dbt test` in CI or as an Airflow task after `dbt run`.  
- Add **custom dbt tests** (e.g. `accepted_range` for percentages, row count bounds).  
- Optional: send test results to a monitoring/alerting system.

---

## 4. Ownership & accountability

**Goal:** Clear ownership of datasets and pipelines.

| Mechanism | What it does |
|-----------|----------------|
| **dbt `meta`** | In `dbt_project.yml` or `schema.yml`, set `owner`, `tier`, `pii`. These appear in dbt docs. |
| **Airflow DAG** | `default_args = {"owner": "..."}`. |
| **README / GOVERNANCE** | This doc and README state who maintains the pipeline. |

**Implemented:**  
- dbt models and sources include `meta.owner` and `meta.tier` where set.  
- Use a single team/alias (e.g. `data-engineering`) or per-domain owners as you scale.

**How to improve:**  
- Add `meta` to every model/source.  
- Map owners to Slack/email for incident routing.

---

## 5. Security & access

**Goal:** Control who can read/write what; protect sensitive data.

| Area | Recommendations |
|------|------------------|
| **Snowflake** | Use roles and warehouses per environment (e.g. `NBA_READER`, `NBA_TRANSFORM`). Grant read on marts to analysts, write on RAW to the loader only. |
| **Secrets** | Keep credentials in `.env` (or a secrets manager); never commit. Use Airflow Variables/Connections for prod. |
| **PII** | This pipeline uses public NBA data (no PII). If you add user data later, tag PII in dbt `meta` and apply Snowflake masking policies. |

**How to improve:**  
- Apply **Snowflake object tags** (e.g. `domain=NBA`, `layer=raw|staging|marts`) and use them in access policies.  
- Document access matrix (who has read/write to which schemas) in this doc or the wiki.

---

## 6. Policies & standards

**Goal:** Consistent naming, SLAs, and retention.

| Policy | Current / suggestion |
|--------|----------------------|
| **Naming** | Dims: `dim_*`; fact: `fact_*`; staging: `stg_*`. Snowflake: `RAW.*`, `ANALYTICS.staging.*`, `ANALYTICS.marts.*`. |
| **SLAs** | Airflow tasks have SLA timeouts; document expected run frequency and latency (e.g. “daily by 07:00”). |
| **Retention** | Raw parquet and Snowflake: no automatic purge in code. Define retention (e.g. keep 2 years of raw) and implement with Snowflake lifecycle or a cleanup job. |
| **Change process** | Schema changes via dbt and code review; backfill/breaking changes documented in PRs or runbooks. |

**How to improve:**  
- Add a short **runbook** (e.g. `docs/RUNBOOK.md`) for common failures and how to re-run or backfill.  
- Formalize retention in Snowflake (e.g. time-travel + fail-safe, or explicit drop/archive jobs).

---

## 7. Checklist for this project

- [x] **Catalog**: dbt docs + YAML descriptions; ingestion metadata for run history.  
- [x] **Lineage**: dbt docs DAG; Airflow DAG.  
- [x] **Quality**: Ingestion checks + dbt tests; run `dbt test` regularly.  
- [x] **Ownership**: dbt `meta` (owner/tier) where added; DAG owner in Airflow.  
- [ ] **Access**: Document Snowflake roles and grants; add tags if needed.  
- [ ] **Policies**: Document SLAs and retention; add runbook for ops.

---

## References

- [dbt Documentation](https://docs.getdbt.com/docs/build/documentation)  
- [dbt Model metadata](https://docs.getdbt.com/reference/resource-properties/meta)  
- [Snowflake Data Governance](https://docs.snowflake.com/en/user-guide/governance-overview)
