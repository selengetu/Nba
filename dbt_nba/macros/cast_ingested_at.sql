{# Parse ingested_at from raw: ISO-style string or legacy nanoseconds (string or number). #}
{# Only use numeric path when value is all digits (avoids parse errors). #}
{% macro cast_ingested_at(column_expr) %}
  coalesce(
    try_strptime({{ column_expr }}::varchar, '%Y-%m-%d %H:%M:%S.%f'),
    try_strptime({{ column_expr }}::varchar, '%Y-%m-%d %H:%M:%S'),
    try_strptime({{ column_expr }}::varchar, '%Y-%m-%d'),
    case
      when regexp_matches(trim({{ column_expr }}::varchar), '^[0-9]+$')
      then epoch_ms((try_cast({{ column_expr }}::varchar AS BIGINT) / 1000000)::BIGINT)::TIMESTAMP
      else null
    end
  )
{% endmacro %}
