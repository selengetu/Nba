{{
    config(
        materialized='incremental',
        unique_key='team_id',
        incremental_strategy='merge',
        on_schema_change='sync_all_columns',
        cluster_by=['team_id'],
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
from {{ ref('stg_teams') }}
