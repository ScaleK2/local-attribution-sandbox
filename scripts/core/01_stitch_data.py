from pathlib import Path

import duckdb

REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = REPO_ROOT / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = OUTPUT_DIR / "attribution_sandbox.duckdb"

con = duckdb.connect(str(DB_PATH))

ga4_events_csv = (REPO_ROOT / 'data' / 'ga4_events.csv').as_posix()
backend_outcomes_csv = (REPO_ROOT / 'data' / 'backend_outcomes.csv').as_posix()

con.execute(f"""
CREATE OR REPLACE TABLE ga4_events AS
SELECT * FROM read_csv_auto('{ga4_events_csv}');

CREATE OR REPLACE TABLE backend_outcomes AS
SELECT * FROM read_csv_auto('{backend_outcomes_csv}');

CREATE OR REPLACE TABLE stitched_events AS
SELECT
  COALESCE(NULLIF(g.user_id_ui, ''), CAST(g.user_pseudo_id AS VARCHAR)) AS stitched_user_key,
  g.event_timestamp,
  g.source,
  g.medium,
  g.event_name,
  g.gclid,
  g.fbclid,
  g.quote_number_after_generated AS quote_id,
  g.order_id_after_generated AS order_id,
  b.status AS backend_status,
  b.revenue,
  CASE
    WHEN b.backend_user_id = g.user_id_ui THEN 'user_id_match'
    WHEN b.order_id = g.order_id_after_generated THEN 'order_id_match'
    WHEN b.quote_id = g.quote_number_after_generated THEN 'quote_id_match'
    ELSE 'no_backend_match'
  END AS match_quality
FROM ga4_events g
LEFT JOIN backend_outcomes b
  ON b.backend_user_id = g.user_id_ui
  OR b.order_id = g.order_id_after_generated
  OR b.quote_id = g.quote_number_after_generated;
""")

print(con.execute("SELECT match_quality, COUNT(*) FROM stitched_events GROUP BY 1").fetchdf())