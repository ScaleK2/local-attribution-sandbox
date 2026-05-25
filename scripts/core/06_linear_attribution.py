from pathlib import Path

import duckdb

REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = REPO_ROOT / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = OUTPUT_DIR / "attribution_sandbox.duckdb"

con = duckdb.connect(str(DB_PATH))

con.execute("""
CREATE OR REPLACE TABLE linear_attribution AS

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
    g.event_name

  FROM backend_conversions b

  LEFT JOIN ga4_events g
    ON g.order_id_after_generated = b.order_id
    OR g.quote_number_after_generated = b.quote_id
    OR g.user_id_ui = b.backend_user_id

  WHERE g.event_timestamp IS NOT NULL
),

touchpoint_counts AS (
  SELECT
    conversion_key,
    COUNT(*) AS touchpoint_count
  FROM matched_touchpoints
  GROUP BY conversion_key
)

SELECT
  m.conversion_key,
  m.order_id,
  m.revenue,
  m.event_timestamp,
  m.source,
  m.medium,
  m.event_name,
  t.touchpoint_count,

  ROUND(
    m.revenue / t.touchpoint_count,
    2
  ) AS linear_attribution_revenue

FROM matched_touchpoints m

LEFT JOIN touchpoint_counts t
  ON m.conversion_key = t.conversion_key;
""")

print("\n=== LINEAR ATTRIBUTION CREATED ===")
print(con.execute("""
SELECT
  COUNT(*) AS touchpoint_rows,
  COUNT(DISTINCT conversion_key) AS conversions
FROM linear_attribution
""").fetchdf())

print("\n=== LINEAR ATTRIBUTION BY CHANNEL ===")
print(con.execute("""
SELECT
  source,
  medium,
  ROUND(SUM(linear_attribution_revenue), 2) AS linear_revenue
FROM linear_attribution
GROUP BY 1,2
ORDER BY linear_revenue DESC
""").fetchdf())

print("\n=== SAMPLE LINEAR ATTRIBUTION ===")
print(con.execute("""
SELECT
  conversion_key,
  source,
  medium,
  revenue,
  touchpoint_count,
  linear_attribution_revenue
FROM linear_attribution
LIMIT 25
""").fetchdf())

print("\n=== VALIDATION CHECK ===")
print(con.execute("""
SELECT
  ROUND(SUM(linear_attribution_revenue), 2) AS total_linear_revenue
FROM linear_attribution
""").fetchdf())