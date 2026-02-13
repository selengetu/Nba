# Marts

All mart tables are **incremental** (MERGE strategy). Only new/changed rows (by `ingested_at`) are processed after the first run.

## Dimension tables (incremental)

| Model | Unique key | Source | Incremental filter |
|-------|------------|--------|--------------------|
| **dim_players** | player_id | stg_players | ingested_at > max(ingested_at) |
| **dim_teams** | team_id | stg_teams | ingested_at > max(ingested_at) |
| **dim_seasons** | season_id | stg_seasons | ingested_at > max(ingested_at) |

## fact_player_season_stats

**Incremental fact** from `stg_player_season_stats`. MERGE on `(player_id`, `season_id`, `team_id)`. Clustered by `season_id`.

## player_season_performance

**Incremental** analytics mart. Joins `fact_player_season_stats` with `dim_players`, `dim_teams`, `dim_seasons`. MERGE on `(player_id`, `season_id`, `team_id)`. Includes PPG.

## active_players

**Incremental** subset of `dim_players` where `is_active = '1'`. MERGE on `player_id`.

---

### Running incremental models

**Incremental (default):**
```bash
dbt run
```

**Full refresh (all models or one):**
```bash
dbt run --full-refresh
dbt run --select fact_player_season_stats --full-refresh
```

### When to use full refresh

- First run (tables don't exist)
- Schema changes (new columns)
- Data quality issues requiring full reprocessing
