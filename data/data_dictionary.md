# Simulated Multi-Channel Marketing Dataset - Data Dictionary

## meta_ads_insights

| Field | Definition |
|---|---|
| date_start/date_stop | Reporting date window. |
| account_id | Simulated Meta ad account. |
| campaign_id/campaign_name | Meta campaign identifiers. |
| adset_id/adset_name | Meta ad set identifiers. |
| ad_id/ad_name | Meta ad identifiers. |
| objective/buying_type | Campaign objective and buying type. |
| publisher_platform/platform_position/impression_device | Reporting breakdown dimensions. |
| spend | Platform spend in AUD. |
| impressions/reach/frequency | Aggregated delivery metrics. |
| clicks/inline_link_clicks/landing_page_views | Aggregated engagement and site landing metrics. |
| ctr/cpc/cpm | Derived platform efficiency metrics. |
| reported_leads/reported_sales | Meta-attributed conversions; intentionally inflated vs backend proof. |

## google_ads_clicks

| Field | Definition |
|---|---|
| date/timestamp | Click date and timestamp. |
| customer_id | Simulated Google Ads customer ID. |
| campaign_id/campaign_name | Google Ads campaign identifiers. |
| ad_group_id/ad_group_name/ad_id | Search ad group/ad identifiers. |
| keyword_text/search_term | Matched keyword and user query. |
| device/network | Click device and network. |
| gclid | Google click ID; occasionally missing/broken. |
| cost | Click cost in AUD. |
| reported_conversion | Google-reported conversion flag; intentionally biased to last-click. |

## ga4_events

| Field | Definition |
|---|---|
| event_timestamp/event_date | Event time and date. |
| user_pseudo_id/ga_client_id/session_id | GA/browser/session identity fields. |
| user_id_ui | Front-end user ID where available; missing for some events. |
| event_name | Event type, e.g. page_view, generate_lead, purchase. |
| source/medium/traffic_category | GA4 traffic attribution fields; some Direct/Unknown leakage included. |
| gclid/fbclid/fbc/fbp | Paid click/browser identifiers; sometimes missing. |
| page_uri/full_page_url/full_referrer | Page and referrer context. |
| form_name/form_step_name/form_valid | Lead form context. |
| quote_number_after_generated/order_id_after_generated | Outcome-created join keys, only after lead/sale events. |
| custom_event | Simple conversion classifier. |

## backend_outcomes

| Field | Definition |
|---|---|
| backend_user_id | CRM identity; equals user_id_ui only for clean stitches. |
| lead_id/quote_id/order_id | Outcome identifiers; order_id only on sales. |
| created_at/sale_at | Lead creation and sale timestamps. |
| status | Outcome status. |
| revenue/margin | Commercial value for sales. |
| call_result/sales_stage/source_system | CRM workflow context. |

