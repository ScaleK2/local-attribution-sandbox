import duckdb

con = duckdb.connect("output/attribution_sandbox.duckdb")

print("\n=== RAW TABLE ROW COUNTS ===")
print(con.execute("""
SELECT 'ga4_events' AS table_name, COUNT(*) AS rows FROM ga4_events
UNION ALL
SELECT 'backend_outcomes' AS table_name, COUNT(*) AS rows FROM backend_outcomes
UNION ALL
SELECT 'stitched_events' AS table_name, COUNT(*) AS rows FROM stitched_events
""").fetchdf())

print("\n=== DISTINCT USER / OUTCOME COUNTS ===")
print(con.execute("""
SELECT
  COUNT(DISTINCT stitched_user_key) AS stitched_users,
  COUNT(DISTINCT quote_id) AS quote_ids,
  COUNT(DISTINCT order_id) AS order_ids,
  COUNT(DISTINCT CASE WHEN backend_status = 'won' THEN order_id END) AS won_order_ids,
  SUM(revenue) AS total_revenue
FROM stitched_events
""").fetchdf())

print("\n=== POSSIBLE DUPLICATED BACKEND OUTCOMES ===")
print(con.execute("""
SELECT
  COALESCE(order_id, quote_id, stitched_user_key) AS outcome_or_user_key,
  backend_status,
  revenue,
  COUNT(*) AS joined_rows
FROM stitched_events
WHERE backend_status IS NOT NULL
GROUP BY 1,2,3
HAVING COUNT(*) > 1
ORDER BY joined_rows DESC
LIMIT 25
""").fetchdf())

print("\n=== REVENUE BY MATCH QUALITY ===")
print(con.execute("""
SELECT
  match_quality,
  COUNT(*) AS rows,
  COUNT(DISTINCT stitched_user_key) AS users,
  COUNT(DISTINCT order_id) AS distinct_orders,
  SUM(revenue) AS summed_revenue
FROM stitched_events
GROUP BY 1
ORDER BY rows DESC
""").fetchdf())