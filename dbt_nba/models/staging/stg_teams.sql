{{
    config(
        materialized='view',
    )
}}
select
    team_id,
    team_name,
    city,
    abbreviation,
    nickname,
    year_founded,
    {{ cast_ingested_at('ingested_at') }} as ingested_at
from {{ source('raw', 'dim_teams') }}
