import duckdb

con = duckdb.connect("output/attribution_sandbox.duckdb")

con.execute("""
CREATE OR REPLACE TABLE position_based_attribution AS

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

  CASE

    -- Single-touch journeys get 100%
    WHEN total_touchpoints = 1
      THEN revenue

    -- Two-touch journeys split evenly
    WHEN total_touchpoints = 2
      THEN revenue * 0.5

    -- Multi-touch first touch gets 40%
    WHEN touchpoint_position = 1
      THEN revenue * 0.4

    -- Multi-touch last touch gets 40%
    WHEN touchpoint_position = total_touchpoints
      THEN revenue * 0.4

    -- Middle touches split 20%
    ELSE
      (revenue * 0.2) / (total_touchpoints - 2)

  END AS position_based_revenue

FROM matched_touchpoints;
""")

print("\n=== POSITION-BASED ATTRIBUTION CREATED ===")
print(con.execute("""
SELECT
  COUNT(*) AS touchpoint_rows,
  COUNT(DISTINCT conversion_key) AS conversions
FROM position_based_attribution
""").fetchdf())

print("\n=== POSITION-BASED REVENUE BY CHANNEL ===")
print(con.execute("""
SELECT
  source,
  medium,
  ROUND(SUM(position_based_revenue), 2) AS position_based_revenue
FROM position_based_attribution
GROUP BY 1,2
ORDER BY position_based_revenue DESC
""").fetchdf())

print("\n=== SAMPLE POSITION-BASED ATTRIBUTION ===")
print(con.execute("""
SELECT
  conversion_key,
  source,
  medium,
  revenue,
  touchpoint_position,
  total_touchpoints,
  ROUND(position_based_revenue, 2) AS position_based_revenue
FROM position_based_attribution
LIMIT 25
""").fetchdf())

print("\n=== VALIDATION CHECK ===")
print(con.execute("""
SELECT
  ROUND(SUM(position_based_revenue), 2) AS total_position_based_revenue
FROM position_based_attribution
""").fetchdf())