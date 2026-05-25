from pathlib import Path

import duckdb

REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = REPO_ROOT / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = OUTPUT_DIR / "attribution_sandbox.duckdb"

con = duckdb.connect(str(DB_PATH))

print("\n=== RAW TABLE ROW COUNTS ===")
print(con.execute("""
SELECT 'ga4_events' AS table_name, COUNT(*) AS rows FROM ga4_events
UNION ALL
SELECT 'backend_outcomes' AS table_name, COUNT(*) AS rows FROM backend_outcomes
UNION ALL
SELECT 'stitched_events' AS table_name, COUNT(*) AS rows FROM stitched_events
""").fetchdf())

print("\n=== BACKEND SOURCE OF TRUTH ===")
print(con.execute("""
SELECT
  status,
  COUNT(*) AS backend_rows,
  COUNT(DISTINCT order_id) AS distinct_order_ids,
  COUNT(DISTINCT quote_id) AS distinct_quote_ids,
  COUNT(DISTINCT backend_user_id) AS distinct_backend_user_ids,
  SUM(revenue) AS backend_revenue
FROM backend_outcomes
GROUP BY status
ORDER BY backend_rows DESC
""").fetchdf())

print("\n=== BACKEND WON CONVERSIONS ONLY ===")
print(con.execute("""
SELECT
  COUNT(*) AS won_rows,
  COUNT(DISTINCT order_id) AS won_order_ids,
  SUM(revenue) AS won_revenue
FROM backend_outcomes
WHERE status = 'won'
  AND revenue > 0
  AND order_id IS NOT NULL
""").fetchdf())

print("\n=== STITCHED EVENTS VIEW OF WON CONVERSIONS ===")
print(con.execute("""
SELECT
  COUNT(*) AS stitched_won_event_rows,
  COUNT(DISTINCT order_id) AS stitched_won_order_ids,
  COUNT(DISTINCT quote_id) AS stitched_won_quote_ids,
  COUNT(DISTINCT stitched_user_key) AS stitched_won_users,
  SUM(revenue) AS repeated_stitched_revenue
FROM stitched_events
WHERE backend_status = 'won'
  AND revenue > 0
""").fetchdf())

print("\n=== MATCH QUALITY SUMMARY ===")
print(con.execute("""
SELECT
  match_quality,
  COUNT(*) AS rows,
  COUNT(DISTINCT stitched_user_key) AS users,
  COUNT(DISTINCT order_id) AS order_ids,
  SUM(revenue) AS repeated_revenue
FROM stitched_events
GROUP BY match_quality
ORDER BY rows DESC
""").fetchdf())

print("\n=== ORDER-ID DUPLICATION CHECK ===")
print("If this returns an empty table, there are no duplicated won orders at the order_id match level.")
print("Revenue can still be repeated across user_id or quote_id stitched touchpoints, so use backend_outcomes as source of truth.")
print(con.execute("""
SELECT
  order_id,
  backend_status,
  MAX(revenue) AS true_order_revenue,
  COUNT(*) AS matched_touchpoint_rows,
  SUM(revenue) AS inflated_revenue_if_summed
FROM stitched_events
WHERE backend_status = 'won'
  AND revenue > 0
  AND order_id IS NOT NULL
GROUP BY order_id, backend_status
HAVING COUNT(*) > 1
ORDER BY matched_touchpoint_rows DESC
LIMIT 20
""").fetchdf())