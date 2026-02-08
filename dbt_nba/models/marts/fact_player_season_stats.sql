{{
    config(
        materialized='incremental',
        unique_key=['player_id', 'season_id', 'team_id'],
        incremental_strategy='merge',
        on_schema_change='append_new_columns',
        cluster_by=['season_id'],
    )
}}
-- Incremental fact table: only processes new/updated rows based on ingested_at
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
    ingested_at
from {{ ref('stg_player_season_stats') }}

{% if is_incremental() %}
    -- Only process rows newer than the max ingested_at in the current table
    where ingested_at > (select max(ingested_at) from {{ this }})
{% endif %}
