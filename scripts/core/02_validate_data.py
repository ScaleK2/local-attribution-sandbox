import duckdb

con = duckdb.connect("output/attribution_sandbox.duckdb")

print("\n=== TABLE STRUCTURE ===")
print(con.execute("""
DESCRIBE stitched_events
""").fetchdf())

print("\n=== SAMPLE ROWS ===")
print(con.execute("""
SELECT *
FROM stitched_events
LIMIT 10
""").fetchdf())

print("\n=== MATCH QUALITY BY EVENT ===")
print(con.execute("""
SELECT
  event_name,
  match_quality,
  COUNT(*) AS row_count
FROM stitched_events
GROUP BY 1,2
ORDER BY row_count DESC
""").fetchdf())