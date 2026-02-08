{{
    config(
        materialized='view',
    )
}}
select
    player_id,
    full_name,
    player_slug,
    from_year,
    to_year,
    is_active,
    ingested_at
from {{ source('raw', 'dim_players') }}
