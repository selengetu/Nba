{{
    config(
        materialized='view',
    )
}}
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
    {{ cast_ingested_at('ingested_at') }} as ingested_at
from {{ source('raw', 'dim_draft') }}
