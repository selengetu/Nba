{{
    config(
        materialized='view',
    )
}}
select
    season_id,
    season_start_year,
    season_end_year,
    season_label,
    ingested_at
from {{ source('raw', 'dim_seasons') }}
