{{
    config(
        materialized='table',
    )
}}
-- Current active players (convenience mart for reporting)
select
    player_id,
    full_name,
    player_slug,
    from_year,
    to_year,
    ingested_at
from {{ ref('stg_players') }}
where is_active = '1'
