import duckdb
import json
import urllib.request
from pathlib import Path

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:7b"

DB_PATH = "output/attribution_sandbox.duckdb"
OUTPUT_PATH = Path("output/ai_attribution_interpretation.md")

con = duckdb.connect(DB_PATH)

comparison_df = con.execute("""
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
""").fetchdf()

validation_df = con.execute("""
SELECT
  ROUND(SUM(first_touch_revenue), 2) AS first_touch_total,
  ROUND(SUM(last_touch_revenue), 2) AS last_touch_total,
  ROUND(SUM(linear_revenue), 2) AS linear_total,
  ROUND(SUM(position_based_revenue), 2) AS position_total,
  ROUND(SUM(time_decay_revenue), 2) AS time_decay_total
FROM attribution_model_comparison
""").fetchdf()

backend_df = con.execute("""
SELECT
  COUNT(*) AS won_conversions,
  ROUND(SUM(revenue), 2) AS backend_revenue
FROM backend_outcomes
WHERE status = 'won'
  AND revenue > 0
  AND order_id IS NOT NULL
""").fetchdf()

channel_facts_df = con.execute("""
SELECT
  source,
  medium,
  first_touch_revenue,
  last_touch_revenue,
  linear_revenue,
  position_based_revenue,
  time_decay_revenue,
  model_spread,
  ROUND(last_touch_revenue - first_touch_revenue, 2) AS first_to_last_delta,
  CASE
    WHEN last_touch_revenue > first_touch_revenue THEN 'stronger later in journey'
    WHEN first_touch_revenue > last_touch_revenue THEN 'stronger earlier in journey'
    ELSE 'balanced between first and last touch'
  END AS journey_direction,
  likely_channel_role
FROM attribution_model_comparison
ORDER BY max_model_revenue DESC
""").fetchdf()

most_sensitive = channel_facts_df.sort_values("model_spread", ascending=False).iloc[0]
most_stable = channel_facts_df.sort_values("model_spread", ascending=True).iloc[0]

comparison_text = comparison_df.to_string(index=False)
validation_text = validation_df.to_string(index=False)
channel_facts_text = channel_facts_df.to_string(index=False)

backend_revenue = float(backend_df.loc[0, "backend_revenue"])
won_conversions = int(backend_df.loc[0, "won_conversions"])

verified_facts = f"""
VERIFIED FACTS — DO NOT RECALCULATE

Backend source of truth:
- Won conversions: {won_conversions}
- Backend revenue: ${backend_revenue:,.2f}

Most attribution-sensitive channel:
- Channel: {most_sensitive['source']} / {most_sensitive['medium']}
- Model spread: ${most_sensitive['model_spread']:,.2f}
- First-touch revenue: ${most_sensitive['first_touch_revenue']:,.2f}
- Last-touch revenue: ${most_sensitive['last_touch_revenue']:,.2f}
- First-to-last delta: ${most_sensitive['first_to_last_delta']:,.2f}
- Journey direction: {most_sensitive['journey_direction']}

Most stable channel:
- Channel: {most_stable['source']} / {most_stable['medium']}
- Model spread: ${most_stable['model_spread']:,.2f}
- First-touch revenue: ${most_stable['first_touch_revenue']:,.2f}
- Last-touch revenue: ${most_stable['last_touch_revenue']:,.2f}
- First-to-last delta: ${most_stable['first_to_last_delta']:,.2f}
- Journey direction: {most_stable['journey_direction']}

Channel-level verified facts:
{channel_facts_text}
"""

prompt = f"""
You are a senior marketing analytics strategist and behavioural measurement analyst.

You are analysing a deterministic attribution model comparison generated from a locally-built attribution sandbox.

The reader is a marketer learning:
- attribution modelling,
- analytical systems thinking,
- behavioural interpretation,
- and modern local analytics workflows.

Your job is NOT to define attribution models generally.

Your job is to interpret the ACTUAL NUMBERS from this dataset and explain what they imply about:
- customer behaviour,
- channel roles,
- attribution assumptions,
- and strategic marketing interpretation.

You must reason from verified evidence first, then interpretation.

# Critical Rules

1. Do NOT make generic claims.
2. Every major interpretation MUST reference exact numbers from the verified facts or attribution table.
3. Use the VERIFIED FACTS as the source of truth.
4. Do NOT calculate rankings, deltas, totals, or spreads yourself.
5. Use the provided model_spread value when discussing attribution sensitivity.
6. Do NOT calculate model spread using total backend revenue.
7. The most attribution-sensitive channel is already identified in the verified facts.
8. The most stable channel is already identified in the verified facts.
9. If your interpretation conflicts with the verified facts, the verified facts are correct.
10. Do NOT claim attribution proves causality.
11. Do NOT overstate certainty.
12. When interpreting Unknown or Direct, default to tracking ambiguity rather than assuming clean channel behaviour.
13. Direct should usually be treated as brand recall, returning intent, or attribution leakage unless the data proves otherwise.
14. Unknown should usually be treated as tracking ambiguity, not a real behavioural channel.
15. Explain HOW channel valuation changes across attribution models.
16. Explain WHY those valuation changes matter strategically.
17. Treat the attribution models as behavioural lenses, not objective truth systems.
18. Avoid shallow summaries, generic AI phrasing, buzzwords, hype, and textbook filler.

# Dataset Context

The attribution table compares:
- First-touch attribution
- Last-touch attribution
- Linear attribution
- Position-based attribution
- Time-decay attribution

All attribution models should reconcile approximately back to backend revenue.

# Verified Facts

{verified_facts}

# Attribution Comparison Table

{comparison_text}

# Model Validation Totals

{validation_text}

# Behavioural Interpretation Requirement

Do NOT analyse attribution models independently.

Instead:
- analyse the relationship BETWEEN models;
- explain how channel valuation changes across models;
- explain what those changes imply behaviourally;
- explain where attribution uncertainty exists;
- explain how attribution philosophy changes the strategic narrative.

The goal is behavioural interpretation, strategic reasoning, and attribution sensitivity analysis.

# Required Analysis

For EACH major channel:
- compare how the channel behaves across all attribution models;
- explain what the overall attribution pattern suggests behaviourally;
- reference exact numerical values;
- reference model_spread;
- explain whether the channel appears earlier, later, consistent, or ambiguous;
- identify whether it appears over-valued or under-valued by specific models.

Specifically analyse:
1. Meta / paid_social
2. Google Ads / cpc
3. Direct / (none)
4. Organic / organic
5. Unknown / (not set)

# Additional Analysis Requirements

You must also:
- identify the most attribution-sensitive channel using the verified facts;
- identify the most stable channel using the verified facts;
- explain why stability matters strategically;
- explain why attribution-sensitive channels are dangerous to evaluate using only one model;
- explain why Direct traffic is dangerous to over-interpret;
- explain how attribution model choice materially changes perceived channel value;
- explain why last-click can undervalue demand generation channels;
- explain why first-touch can undervalue conversion capture channels;
- explain which channels appear to create demand vs monetise existing demand;
- explain where attribution uncertainty is highest;
- identify where the business may be under-investigating tracking quality.

# Output Structure

# Attribution Interpretation Report

## Executive Summary

Provide:
- the single most important behavioural insight;
- the biggest attribution risk;
- the most important strategic takeaway.

## Channel Role Analysis

Provide detailed interpretation for each channel using exact numbers.

## Attribution Sensitivity Analysis

Explain:
- which channels shift the most between models;
- what that implies behaviourally;
- why attribution philosophy materially changes the marketing story.

## Strategic Risks

Explain:
- risks of relying too heavily on last-click;
- risks of over-crediting Direct;
- risks of weak identity stitching;
- risks of interpreting attribution as causality;
- risks of evaluating channels using only one attribution philosophy.

## Recommended Next Investigations

Provide practical next analytical steps.

Examples:
- path analysis;
- sessionisation;
- event weighting;
- incrementality testing;
- probabilistic attribution;
- MMM;
- channel grouping refinement;
- backend identity strengthening;
- Direct traffic decomposition.

## Final Key Takeaway

End with a concise explanation of the single most important lesson from the dataset and why attribution should be interpreted cautiously.
"""

payload = {
    "model": MODEL_NAME,
    "prompt": prompt,
    "stream": False
}

data = json.dumps(payload).encode("utf-8")

req = urllib.request.Request(
    OLLAMA_URL,
    data=data,
    headers={"Content-Type": "application/json"}
)

print("\n=== SENDING VERIFIED ATTRIBUTION FACTS TO LOCAL QWEN MODEL ===\n")

try:
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode("utf-8"))
        ai_output = result.get("response", "")

    print(ai_output)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(ai_output, encoding="utf-8")

    print("\n=== SAVED REPORT ===")
    print(OUTPUT_PATH)

except Exception as e:
    print("\nERROR: Could not connect to Ollama.")
    print("Make sure Ollama is running and the model is installed.")
    print(f"Details: {e}")