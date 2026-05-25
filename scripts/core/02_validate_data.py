from pathlib import Path

import duckdb

REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = REPO_ROOT / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = OUTPUT_DIR / "attribution_sandbox.duckdb"

con = duckdb.connect(str(DB_PATH))

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