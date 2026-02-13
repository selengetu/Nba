{{
    config(
        materialized='view',
    )
}}
select
    player_id,
    season_id,
    team_id,
    games_played,
    minutes,
    points,
    rebounds,
    assists,
    steals,
    blocks,
    turnovers,
    fg_pct,
    fg3_pct,
    ft_pct,
    {{ cast_ingested_at('ingested_at') }} as ingested_at
from {{ source('raw', 'fact_player_season_stats') }}
