import duckdb
import json
import urllib.request

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:7b"

con = duckdb.connect("output/attribution_sandbox.duckdb")

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

comparison_text = comparison_df.to_string(index=False)
validation_text = validation_df.to_string(index=False)

prompt = f"""
You are a senior marketing analytics strategist and behavioural measurement analyst.

You are analysing a deterministic attribution model comparison generated from a locally-built attribution sandbox.

The reader is a marketer learning:

* attribution modelling,
* analytical systems thinking,
* behavioural interpretation,
* and modern local analytics workflows.

Your job is NOT to define attribution models generally.

Your job is to interpret the ACTUAL NUMBERS from this dataset and explain what they imply about:

* customer behaviour,
* channel roles,
* attribution assumptions,
* and strategic marketing interpretation.

You must reason from evidence first, then interpretation.

# Critical Rules

1. Do NOT make generic claims.
2. Every major interpretation MUST reference exact numbers from the attribution table.
3. Do NOT summarise attribution models theoretically unless directly tied to the dataset.
4. Explain HOW channel valuation changes across attribution models.
5. Explain WHY those valuation changes matter strategically.
6. Identify where attribution ambiguity exists.
7. If a channel may represent tracking leakage or unclear attribution, say so explicitly.
8. Do NOT claim attribution proves causality.
9. Do NOT overstate certainty.
10. Explain what a marketer should investigate next.
11. Focus on behavioural interpretation and strategic implications.
12. Use commercially practical language, not academic language.
13. Prioritise insight density over filler.
14. Treat the attribution models as behavioural lenses, not objective truth systems.
15. Use the data as evidence BEFORE giving judgement.
16. Avoid shallow summaries and generic AI phrasing.
17. Use the provided model_spread value when discussing attribution sensitivity.
18. Do NOT calculate model spread using total backend revenue.
19. The most attribution-sensitive channel is the channel with the highest model_spread.
20. The most stable channel is the channel with the lowest model_spread.
21. Use the verified facts as the source of truth.
22. Do not calculate rankings, deltas, or spreads.
23. If your interpretation conflicts with the verified facts, the verified facts are correct.
24. When interpreting Unknown or Direct, default to tracking ambiguity rather than assuming clean channel behaviour.

# Dataset Context

The attribution table compares:

* First-touch attribution
* Last-touch attribution
* Linear attribution
* Position-based attribution
* Time-decay attribution

The backend conversion source-of-truth is:

* 75 won conversions
* $28,353.55 total backend revenue

All attribution models should reconcile approximately back to this value.

VERIFIED FACTS — DO NOT RECALCULATE

Backend revenue: $28,353.55
Won conversions: 75

Most attribution-sensitive channel:
Meta / paid_social
Model spread: $7,077.48
Reason: first-touch $13,664.88 vs last-touch $6,587.40

Most stable channel:
Unknown / (not set)
Model spread: $484.24

Google Ads / cpc:
First-touch: $7,107.66
Last-touch: $10,917.85
Delta: +$3,810.19
Interpretation direction: stronger later in journey

Direct / (none):
First-touch: $6,296.44
Last-touch: $7,456.31
Delta: +$1,159.87
Interpretation direction: slightly stronger later, but ambiguous

# Attribution Comparison Table

{comparison_text}

# Model Validation Totals

{validation_text}

# Behavioural Interpretation Requirement

Do NOT analyse attribution models independently.

Instead:

* analyse the relationship BETWEEN models;
* explain how channel valuation changes across models;
* explain what those changes imply behaviourally;
* explain where attribution uncertainty exists;
* explain how attribution philosophy changes the strategic narrative.

The goal is:

* behavioural interpretation,
* strategic reasoning,
* and attribution sensitivity analysis.

NOT merely restating the table.

# Required Analysis

For EACH major channel:

* compare how the channel behaves across ALL attribution models:

  * first-touch,
  * last-touch,
  * linear,
  * position-based,
  * time-decay;

* explain what the overall attribution pattern suggests behaviourally;

* explain whether the channel appears to function primarily as:

  * discovery,
  * awareness,
  * consideration,
  * reinforcement,
  * conversion capture,
  * retention,
  * or an ambiguous/mixed role;

* reference the exact numerical differences between models;

* explain what the model spread implies about attribution sensitivity;

* explain whether the channel appears:

  * earlier in journeys,
  * later in journeys,
  * consistently throughout journeys,
  * or inconsistently attributed;

* identify whether the channel appears:

  * over-valued by certain models,
  * under-valued by certain models,
  * or relatively stable across attribution philosophies.

Specifically analyse:

1. Meta / paid_social
2. Google Ads / cpc
3. Direct / (none)
4. Organic / organic
5. Unknown / (not set)

# Additional Analysis Requirements

You must also:

* identify which channel is MOST attribution-sensitive;
* identify which channel is MOST stable across models;
* explain why stability matters strategically;
* explain why attribution-sensitive channels are dangerous to evaluate using only one model;
* explain why Direct traffic is dangerous to over-interpret;
* explain how attribution model choice materially changes perceived channel value;
* explain why last-click can undervalue demand generation channels;
* explain why first-touch can undervalue conversion capture channels;
* explain which channels appear to create demand vs monetise existing demand;
* explain where attribution uncertainty is highest;
* identify where the business may be under-investigating tracking quality.

# Strategic Interpretation Expectations

Interpret the outputs like a senior operator reviewing a real marketing business.

You should:

* infer likely funnel positioning;
* infer behavioural journey patterns;
* infer likely customer behaviour;
* explain operational risks;
* explain strategic trade-offs.

Do NOT:

* pretend the models represent perfect truth;
* speak with false certainty;
* oversimplify behavioural complexity.

# Output Style

Write like:

* an experienced marketing strategist,
* analytics lead,
* or behavioural measurement consultant.

The tone should feel:

* analytical,
* commercially grounded,
* nuanced,
* practical,
* and evidence-driven.

Avoid:

* buzzwords,
* hype,
* generic AI phrasing,
* textbook filler,
* surface-level commentary.

# Output Structure

# Attribution Interpretation Report

## Executive Summary

Provide:

* the single most important behavioural insight;
* the biggest attribution risk;
* the most important strategic takeaway.

## Channel Role Analysis

Provide detailed interpretation for each channel using exact numbers from the dataset.

## Attribution Sensitivity Analysis

Explain:

* which channels shift the most between models;
* what that implies behaviourally;
* why attribution philosophy materially changes the marketing story.

## Strategic Risks

Explain:

* risks of relying too heavily on last-click;
* risks of over-crediting Direct;
* risks of weak identity stitching;
* risks of interpreting attribution as causality;
* risks of evaluating channels using only one attribution philosophy.

## Recommended Next Investigations

Provide practical next analytical steps.

Examples:

* path analysis,
* sessionisation,
* event weighting,
* incrementality testing,
* probabilistic attribution,
* MMM,
* channel grouping refinement,
* backend identity strengthening,
* Direct traffic decomposition.

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

print("\n=== SENDING ATTRIBUTION DATA TO LOCAL QWEN MODEL ===\n")

try:
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode("utf-8"))
        ai_output = result.get("response", "")

    print(ai_output)

    with open("output/ai_attribution_interpretation.md", "w", encoding="utf-8") as f:
        f.write(ai_output)

    print("\n=== SAVED REPORT ===")
    print("output/ai_attribution_interpretation.md")

except Exception as e:
    print("\nERROR: Could not connect to Ollama.")
    print("Make sure Ollama is running and the model is installed.")
    print(f"Details: {e}")