{# Parse ingested_at from raw: ISO-style string or legacy nanoseconds (string or number). #}
{# Only use numeric path when value is all digits (avoids "Numeric value ... is not recognized"). #}
{% macro cast_ingested_at(column_expr) %}
  coalesce(
    try_to_timestamp_ntz({{ column_expr }}::varchar, 'YYYY-MM-DD HH24:MI:SS.FF3'),
    try_to_timestamp_ntz({{ column_expr }}::varchar, 'YYYY-MM-DD HH24:MI:SS'),
    try_to_timestamp_ntz({{ column_expr }}::varchar, 'YYYY-MM-DD'),
    case
      when regexp_like(trim({{ column_expr }}::varchar), '^[0-9]+$')
      then to_timestamp_ntz(try_to_number({{ column_expr }}::varchar) / 1000000000)
      else null
    end
  )
{% endmacro %}
