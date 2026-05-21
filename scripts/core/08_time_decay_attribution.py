import duckdb

con = duckdb.connect("output/attribution_sandbox.duckdb")

con.execute("""
CREATE OR REPLACE TABLE time_decay_attribution AS

WITH backend_conversions AS (
  SELECT
    order_id AS conversion_key,
    backend_user_id,
    quote_id,
    order_id,
    revenue
  FROM backend_outcomes
  WHERE status = 'won'
    AND revenue > 0
    AND order_id IS NOT NULL
),

matched_touchpoints AS (
  SELECT
    b.conversion_key,
    b.order_id,
    b.revenue,
    g.event_timestamp,
    g.source,
    g.medium,
    g.event_name,

    ROW_NUMBER() OVER (
      PARTITION BY b.conversion_key
      ORDER BY g.event_timestamp ASC
    ) AS touchpoint_position,

    COUNT(*) OVER (
      PARTITION BY b.conversion_key
    ) AS total_touchpoints

  FROM backend_conversions b

  LEFT JOIN ga4_events g
    ON g.order_id_after_generated = b.order_id
    OR g.quote_number_after_generated = b.quote_id
    OR g.user_id_ui = b.backend_user_id

  WHERE g.event_timestamp IS NOT NULL
),

weighted_touchpoints AS (
  SELECT
    *,

    CAST(touchpoint_position AS DOUBLE)
    /
    SUM(touchpoint_position) OVER (
      PARTITION BY conversion_key
    ) AS decay_weight

  FROM matched_touchpoints
)

SELECT
  conversion_key,
  order_id,
  revenue,
  event_timestamp,
  source,
  medium,
  event_name,
  touchpoint_position,
  total_touchpoints,
  ROUND(decay_weight, 4) AS decay_weight,

  ROUND(
    revenue * decay_weight,
    2
  ) AS time_decay_revenue

FROM weighted_touchpoints;
""")

print("\n=== TIME DECAY ATTRIBUTION CREATED ===")
print(con.execute("""
SELECT
  COUNT(*) AS touchpoint_rows,
  COUNT(DISTINCT conversion_key) AS conversions
FROM time_decay_attribution
""").fetchdf())

print("\n=== TIME DECAY REVENUE BY CHANNEL ===")
print(con.execute("""
SELECT
  source,
  medium,
  ROUND(SUM(time_decay_revenue), 2) AS time_decay_revenue
FROM time_decay_attribution
GROUP BY 1,2
ORDER BY time_decay_revenue DESC
""").fetchdf())

print("\n=== SAMPLE TIME DECAY ATTRIBUTION ===")
print(con.execute("""
SELECT
  conversion_key,
  source,
  medium,
  revenue,
  touchpoint_position,
  total_touchpoints,
  decay_weight,
  time_decay_revenue
FROM time_decay_attribution
LIMIT 25
""").fetchdf())

print("\n=== VALIDATION CHECK ===")
print(con.execute("""
SELECT
  ROUND(SUM(time_decay_revenue), 2) AS total_time_decay_revenue
FROM time_decay_attribution
""").fetchdf())