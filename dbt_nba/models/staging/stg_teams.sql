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
    ingested_at
from {{ source('raw', 'dim_teams') }}
