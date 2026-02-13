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
    {{ cast_ingested_at('ingested_at') }} as ingested_at
from {{ source('raw', 'dim_seasons') }}
