from pathlib import Path

import duckdb

REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = REPO_ROOT / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = OUTPUT_DIR / "attribution_sandbox.duckdb"

con = duckdb.connect(str(DB_PATH))

con.execute("""
CREATE OR REPLACE TABLE touchpoint_attribution AS

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
    ) AS first_touch_rank,

    ROW_NUMBER() OVER (
      PARTITION BY b.conversion_key
      ORDER BY g.event_timestamp DESC
    ) AS last_touch_rank

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

  CASE
    WHEN first_touch_rank = 1 THEN revenue
    ELSE 0
  END AS first_touch_revenue,

  CASE
    WHEN last_touch_rank = 1 THEN revenue
    ELSE 0
  END AS last_touch_revenue

FROM matched_touchpoints;
""")

print("\n=== TOUCHPOINT ATTRIBUTION CREATED ===")
print(con.execute("""
SELECT
  COUNT(*) AS touchpoint_rows,
  COUNT(DISTINCT conversion_key) AS conversions
FROM touchpoint_attribution
""").fetchdf())

print("\n=== FIRST TOUCH REVENUE BY CHANNEL ===")
print(con.execute("""
SELECT
  source,
  medium,
  ROUND(SUM(first_touch_revenue), 2) AS first_touch_revenue
FROM touchpoint_attribution
GROUP BY 1,2
ORDER BY first_touch_revenue DESC
""").fetchdf())

print("\n=== LAST TOUCH REVENUE BY CHANNEL ===")
print(con.execute("""
SELECT
  source,
  medium,
  ROUND(SUM(last_touch_revenue), 2) AS last_touch_revenue
FROM touchpoint_attribution
GROUP BY 1,2
ORDER BY last_touch_revenue DESC
""").fetchdf())

print("\n=== SAMPLE TOUCHPOINTS ===")
print(con.execute("""
SELECT
  conversion_key,
  source,
  medium,
  event_name,
  revenue,
  first_touch_revenue,
  last_touch_revenue
FROM touchpoint_attribution
LIMIT 25
""").fetchdf())