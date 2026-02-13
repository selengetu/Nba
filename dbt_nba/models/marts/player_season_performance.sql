{{
    config(
        materialized='incremental',
        unique_key=['player_id', 'season_id', 'team_id'],
        incremental_strategy='merge',
        on_schema_change='sync_all_columns',
        cluster_by=['season_id'],
    )
}}
-- Analytics-ready: player season stats with player, team, and season labels. Deduplicate by grain so MERGE does not see duplicate keys.
with base as (
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
    join {{ ref('dim_players') }} p on f.player_id = p.player_id
    join {{ ref('dim_teams') }} t on f.team_id = t.team_id
    join {{ ref('dim_seasons') }} s on f.season_id = s.season_id
)
select season_id, season_label, season_start_year, player_id, player_name, player_slug, is_active,
       team_id, team_name, team_abbreviation, games_played, minutes, points, rebounds, assists,
       steals, blocks, turnovers, fg_pct, fg3_pct, ft_pct, ppg, ingested_at
from (
    select *,
        row_number() over (partition by player_id, season_id, team_id order by ingested_at desc nulls last) as rn
    from base
)
where rn = 1
