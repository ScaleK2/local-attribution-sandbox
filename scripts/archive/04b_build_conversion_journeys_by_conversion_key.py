import duckdb

con = duckdb.connect("output/attribution_sandbox.duckdb")

con.execute("""
CREATE OR REPLACE TABLE conversion_journeys AS
WITH won_events AS (
  SELECT
    COALESCE(order_id, quote_id, stitched_user_key) AS conversion_key,
    stitched_user_key,
    event_timestamp,
    source,
    medium,
    event_name,
    gclid,
    fbclid,
    quote_id,
    order_id,
    backend_status,
    revenue,
    match_quality
  FROM stitched_events
  WHERE backend_status = 'won'
    AND revenue > 0
),

conversion_level AS (
  SELECT
    conversion_key,
    MAX(stitched_user_key) AS stitched_user_key,
    MAX(revenue) AS conversion_revenue,
    MAX(order_id) AS order_id,
    MAX(quote_id) AS quote_id,
    MIN(event_timestamp) AS first_touch_time,
    MAX(event_timestamp) AS last_touch_time,
    COUNT(*) AS touchpoint_count,
    STRING_AGG(
      source || ' / ' || medium || ' / ' || event_name,
      ' > '
      ORDER BY event_timestamp
    ) AS journey_path
  FROM won_events
  GROUP BY conversion_key
)

SELECT *
FROM conversion_level;
""")

print("\n=== CONVERSION JOURNEYS CREATED ===")
print(con.execute("""
SELECT COUNT(*) AS conversion_journeys
FROM conversion_journeys
""").fetchdf())

print("\n=== REVENUE CHECK ===")
print(con.execute("""
SELECT
  COUNT(*) AS conversions,
  SUM(conversion_revenue) AS deduped_revenue,
  AVG(touchpoint_count) AS avg_touchpoints_per_conversion
FROM conversion_journeys
""").fetchdf())

print("\n=== SAMPLE CONVERSION JOURNEYS ===")
print(con.execute("""
SELECT
  conversion_key,
  stitched_user_key,
  order_id,
  quote_id,
  conversion_revenue,
  touchpoint_count,
  journey_path
FROM conversion_journeys
ORDER BY conversion_revenue DESC
LIMIT 10
""").fetchdf())