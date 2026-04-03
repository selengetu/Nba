{{
    config(
        materialized='view',
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
    {{ cast_ingested_at('ingested_at') }} as ingested_at
from {{ source('raw', 'dim_arenas') }}
