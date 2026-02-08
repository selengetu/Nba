# Marts

## fact_player_season_stats

**Incremental model** that reads from `stg_player_season_stats` and only processes new rows based on `ingested_at`.

- **Strategy**: MERGE (upsert on `player_id`, `season_id`, `team_id`)
- **Partition/cluster**: By `season_id` for query performance
- **Incremental logic**: Only rows where `ingested_at > max(ingested_at)` in the current table

### Usage

**Incremental (default):**
```bash
dbt run --select fact_player_season_stats
```

**Full refresh (when needed):**
```bash
dbt run --select fact_player_season_stats --full-refresh
```

### When to use full refresh

- Schema changes (new columns)
- Data quality issues requiring reprocessing
- First run (table doesn't exist yet)

## player_season_performance

Analytics-ready table joining fact with dims (players, teams, seasons). Reads from `fact_player_season_stats` (the incremental fact).
