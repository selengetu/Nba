{{
    config(
        materialized='incremental',
        unique_key='player_id',
        incremental_strategy='merge',
        on_schema_change='sync_all_columns',
        cluster_by=['player_id'],
    )
}}
-- Deduplicate by player_id (keep latest ingested_at) so MERGE does not see duplicate keys
select
    player_id,
    full_name,
    player_slug,
    from_year,
    to_year,
    is_active,
    ingested_at
from (
    select *,
        row_number() over (partition by player_id order by ingested_at desc nulls last) as rn
    from {{ ref('stg_players') }}
)
where rn = 1
