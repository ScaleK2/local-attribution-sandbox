from pathlib import Path

import duckdb

REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = REPO_ROOT / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = OUTPUT_DIR / "attribution_sandbox.duckdb"

con = duckdb.connect(str(DB_PATH))

con.execute("""
CREATE OR REPLACE TABLE attribution_model_comparison AS

WITH first_last AS (
  SELECT
    source,
    medium,
    SUM(first_touch_revenue) AS first_touch_revenue,
    SUM(last_touch_revenue) AS last_touch_revenue
  FROM touchpoint_attribution
  GROUP BY 1,2
),

linear AS (
  SELECT
    source,
    medium,
    SUM(linear_attribution_revenue) AS linear_revenue
  FROM linear_attribution
  GROUP BY 1,2
),

position_based AS (
  SELECT
    source,
    medium,
    SUM(position_based_revenue) AS position_based_revenue
  FROM position_based_attribution
  GROUP BY 1,2
),

time_decay AS (
  SELECT
    source,
    medium,
    SUM(time_decay_revenue) AS time_decay_revenue
  FROM time_decay_attribution
  GROUP BY 1,2
),

combined AS (
  SELECT
    COALESCE(fl.source, l.source, p.source, td.source) AS source,
    COALESCE(fl.medium, l.medium, p.medium, td.medium) AS medium,

    COALESCE(fl.first_touch_revenue, 0) AS first_touch_revenue,
    COALESCE(fl.last_touch_revenue, 0) AS last_touch_revenue,
    COALESCE(l.linear_revenue, 0) AS linear_revenue,
    COALESCE(p.position_based_revenue, 0) AS position_based_revenue,
    COALESCE(td.time_decay_revenue, 0) AS time_decay_revenue

  FROM first_last fl
  FULL OUTER JOIN linear l
    ON fl.source = l.source
    AND fl.medium = l.medium
  FULL OUTER JOIN position_based p
    ON COALESCE(fl.source, l.source) = p.source
    AND COALESCE(fl.medium, l.medium) = p.medium
  FULL OUTER JOIN time_decay td
    ON COALESCE(fl.source, l.source, p.source) = td.source
    AND COALESCE(fl.medium, l.medium, p.medium) = td.medium
)

SELECT
  source,
  medium,

  ROUND(first_touch_revenue, 2) AS first_touch_revenue,
  ROUND(last_touch_revenue, 2) AS last_touch_revenue,
  ROUND(linear_revenue, 2) AS linear_revenue,
  ROUND(position_based_revenue, 2) AS position_based_revenue,
  ROUND(time_decay_revenue, 2) AS time_decay_revenue,

  ROUND(
    GREATEST(
      first_touch_revenue,
      last_touch_revenue,
      linear_revenue,
      position_based_revenue,
      time_decay_revenue
    ), 2
  ) AS max_model_revenue,

  ROUND(
    LEAST(
      first_touch_revenue,
      last_touch_revenue,
      linear_revenue,
      position_based_revenue,
      time_decay_revenue
    ), 2
  ) AS min_model_revenue,

  ROUND(
    GREATEST(
      first_touch_revenue,
      last_touch_revenue,
      linear_revenue,
      position_based_revenue,
      time_decay_revenue
    )
    -
    LEAST(
      first_touch_revenue,
      last_touch_revenue,
      linear_revenue,
      position_based_revenue,
      time_decay_revenue
    ), 2
  ) AS model_spread,

  CASE
    WHEN first_touch_revenue > last_touch_revenue
      AND first_touch_revenue > time_decay_revenue
      THEN 'Discovery / demand generation'

    WHEN last_touch_revenue > first_touch_revenue
      AND time_decay_revenue >= linear_revenue
      THEN 'Conversion capture / late-stage intent'

    WHEN linear_revenue >= first_touch_revenue * 0.8
      AND linear_revenue >= last_touch_revenue * 0.8
      THEN 'Consistent journey participant / assist channel'

    ELSE 'Mixed or unclear role'
  END AS likely_channel_role

FROM combined;
""")

print("\n=== ATTRIBUTION MODEL COMPARISON ===")
print(con.execute("""
SELECT *
FROM attribution_model_comparison
ORDER BY max_model_revenue DESC
""").fetchdf())

print("\n=== MODEL TOTAL VALIDATION ===")
print(con.execute("""
SELECT
  ROUND(SUM(first_touch_revenue), 2) AS first_touch_total,
  ROUND(SUM(last_touch_revenue), 2) AS last_touch_total,
  ROUND(SUM(linear_revenue), 2) AS linear_total,
  ROUND(SUM(position_based_revenue), 2) AS position_total,
  ROUND(SUM(time_decay_revenue), 2) AS time_decay_total
FROM attribution_model_comparison
""").fetchdf())

print("\n=== STRATEGIC INTERPRETATION ===")

rows = con.execute("""
SELECT
  source,
  medium,
  first_touch_revenue,
  last_touch_revenue,
  linear_revenue,
  position_based_revenue,
  time_decay_revenue,
  model_spread,
  likely_channel_role
FROM attribution_model_comparison
ORDER BY max_model_revenue DESC
""").fetchall()

for row in rows:
    (
        source,
        medium,
        first_touch,
        last_touch,
        linear,
        position,
        decay,
        spread,
        role
    ) = row

    channel = f"{source} / {medium}"

    print(f"\n--- {channel} ---")
    print(f"Likely role: {role}")
    print(f"First-touch: ${first_touch:,.2f}")
    print(f"Last-touch: ${last_touch:,.2f}")
    print(f"Linear: ${linear:,.2f}")
    print(f"Position-based: ${position:,.2f}")
    print(f"Time-decay: ${decay:,.2f}")
    print(f"Model spread: ${spread:,.2f}")

    if first_touch > last_touch:
        print("Interpretation: This channel appears stronger earlier in the journey, suggesting discovery, awareness, or demand generation behaviour.")

    elif last_touch > first_touch:
        print("Interpretation: This channel appears stronger later in the journey, suggesting intent capture, conversion assistance, or closing behaviour.")

    else:
        print("Interpretation: This channel appears relatively balanced between introduction and closure.")

    if spread > 5000:
        print("Warning: This channel is highly sensitive to attribution model choice. Do not evaluate it using one model only.")

print("\n=== END OF COMPARISON ===")