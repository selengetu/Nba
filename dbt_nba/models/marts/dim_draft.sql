{{
    config(
        materialized='incremental',
        unique_key='player_id',
        incremental_strategy='merge',
        on_schema_change='sync_all_columns',
        cluster_by=['player_id'],
    )
}}
-- One row per player (latest draft record by ingested_at)
select
    player_id,
    player_name,
    draft_year,
    round_number,
    round_pick,
    overall_pick,
    draft_type,
    team_id,
    team_city,
    team_name,
    team_abbreviation,
    organization,
    organization_type,
    has_profile,
    ingested_at
from (
    select *,
        row_number() over (partition by player_id order by ingested_at desc nulls last) as rn
    from {{ ref('stg_draft') }}
)
where rn = 1
