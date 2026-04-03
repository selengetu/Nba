{{
    config(
        materialized='incremental',
        unique_key='team_id',
        incremental_strategy='merge',
        on_schema_change='sync_all_columns',
        cluster_by=['team_id'],
    )
}}
select
    team_id,
    arena_name,
    arena_capacity,
    owner,
    general_manager,
    head_coach,
    dleague_affiliation,
    ingested_at
from (
    select *,
        row_number() over (partition by team_id order by ingested_at desc nulls last) as rn
    from {{ ref('stg_arenas') }}
)
where rn = 1
