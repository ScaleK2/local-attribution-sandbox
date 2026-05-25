from pathlib import Path

import duckdb

REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = REPO_ROOT / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = OUTPUT_DIR / "attribution_sandbox.duckdb"

con = duckdb.connect(str(DB_PATH))

con.execute("""
CREATE OR REPLACE TABLE conversion_journeys AS
WITH backend_conversions AS (
  SELECT
    order_id AS conversion_key,
    backend_user_id,
    quote_id,
    order_id,
    status,
    revenue
  FROM backend_outcomes
  WHERE status = 'won'
    AND revenue > 0
    AND order_id IS NOT NULL
),

matched_touchpoints AS (
  SELECT
    b.conversion_key,
    b.backend_user_id,
    b.quote_id,
    b.order_id,
    b.revenue,
    g.event_timestamp,
    g.source,
    g.medium,
    g.event_name,
    g.gclid,
    g.fbclid,
    CASE
      WHEN g.order_id_after_generated = b.order_id THEN 'order_id_match'
      WHEN g.quote_number_after_generated = b.quote_id THEN 'quote_id_match'
      WHEN g.user_id_ui = b.backend_user_id THEN 'user_id_match'
      ELSE 'no_match'
    END AS match_quality
  FROM backend_conversions b
  LEFT JOIN ga4_events g
    ON g.order_id_after_generated = b.order_id
    OR g.quote_number_after_generated = b.quote_id
    OR g.user_id_ui = b.backend_user_id
),

conversion_level AS (
  SELECT
    conversion_key,
    MAX(backend_user_id) AS backend_user_id,
    MAX(quote_id) AS quote_id,
    MAX(order_id) AS order_id,
    MAX(revenue) AS conversion_revenue,
    COUNT(event_timestamp) AS touchpoint_count,
    MIN(event_timestamp) AS first_touch_time,
    MAX(event_timestamp) AS last_touch_time,
    STRING_AGG(
      source || ' / ' || medium || ' / ' || event_name,
      ' > '
      ORDER BY event_timestamp
    ) AS journey_path
  FROM matched_touchpoints
  GROUP BY conversion_key
)

SELECT *
FROM conversion_level;
""")

print("\n=== BACKEND WON CONVERSIONS SOURCE OF TRUTH ===")
print(con.execute("""
SELECT
  COUNT(*) AS backend_won_rows,
  COUNT(DISTINCT order_id) AS backend_won_order_ids,
  SUM(revenue) AS backend_won_revenue
FROM backend_outcomes
WHERE status = 'won'
  AND revenue > 0
  AND order_id IS NOT NULL
""").fetchdf())

print("\n=== CONVERSION JOURNEYS CREATED ===")
print(con.execute("""
SELECT
  COUNT(*) AS conversion_journeys,
  SUM(conversion_revenue) AS deduped_revenue,
  AVG(touchpoint_count) AS avg_touchpoints
FROM conversion_journeys
""").fetchdf())

print("\n=== SAMPLE JOURNEYS ===")
print(con.execute("""
SELECT
  conversion_key,
  backend_user_id,
  quote_id,
  order_id,
  conversion_revenue,
  touchpoint_count,
  journey_path
FROM conversion_journeys
ORDER BY conversion_revenue DESC
LIMIT 10
""").fetchdf())

print("\n=== JOURNEYS WITHOUT TOUCHPOINTS ===")
print(con.execute("""
SELECT
  COUNT(*) AS conversions_without_touchpoints
FROM conversion_journeys
WHERE touchpoint_count = 0
""").fetchdf())