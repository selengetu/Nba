{{
    config(
        materialized='incremental',
        unique_key='season_id',
        incremental_strategy='merge',
        on_schema_change='sync_all_columns',
        cluster_by=['season_id'],
    )
}}
select
    season_id,
    season_start_year,
    season_end_year,
    season_label,
    {{ cast_ingested_at('ingested_at') }} as ingested_at
from {{ ref('stg_seasons') }}
