{{
    config(
        materialized='table',
    )
}}
-- Analytics-ready: player season stats with player, team, and season labels
select
    s.season_id,
    s.season_label,
    s.season_start_year,
    p.player_id,
    p.full_name as player_name,
    p.player_slug,
    p.is_active,
    t.team_id,
    t.team_name,
    t.abbreviation as team_abbreviation,
    f.games_played,
    round(f.minutes, 1) as minutes,
    round(f.points, 1) as points,
    round(f.rebounds, 1) as rebounds,
    round(f.assists, 1) as assists,
    round(f.steals, 1) as steals,
    round(f.blocks, 1) as blocks,
    round(f.turnovers, 1) as turnovers,
    round(f.fg_pct, 3) as fg_pct,
    round(f.fg3_pct, 3) as fg3_pct,
    round(f.ft_pct, 3) as ft_pct,
    case when f.games_played > 0 then round(f.points / f.games_played, 1) else null end as ppg,
    f.ingested_at
from {{ ref('fact_player_season_stats') }} f
join {{ ref('stg_players') }} p on f.player_id = p.player_id
join {{ ref('stg_teams') }} t on f.team_id = t.team_id
join {{ ref('stg_seasons') }} s on f.season_id = s.season_id
