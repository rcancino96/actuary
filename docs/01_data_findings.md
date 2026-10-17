# 01 — Data findings (Week 1 EDA)

Scripts: `src/eda/inspect1.py` … `inspect9.py`. Every finding below was produced by code, not asserted.

## Data quality issues (planted or real) and treatment

| # | Issue | Evidence | Treatment |
|---|---|---|---|
| DQ1 | `exposure` wrong on ~0.4% of rows: ~3,000 rows at 1.0139 for a 365-day period, ~600 rows recorded in **days** (e.g. 365.0) | exposure vs (period_end − period_start + 1)/365 | Recompute exposure from dates in all files; test is clean |
| DQ2 | `sum_insured` ×1000 on ~0.2% of buildings/contents rows (52M–594M) | gap: max normal 953k vs min bad 52M; premium unchanged | Divide by 1000 when above threshold; also present in test (~370 rows/line) |
| DQ3 | `construction_type` inconsistent case (Brick/brick/BRICK…) and **recode**: `T` (2021–22) becomes `W` (2023+), test only has `W` | crosstab by year | Lower-case; map T/t/W/w → timber |
| DQ4 | 604 duplicate claims (same content, different `claim_id`) | full-row duplicate check | Drop duplicates |
| DQ5 | 413 claims (0.3%) fall outside any policy row (most with 2020 loss dates, before cover) | date-range join | Exclude; logged |
| DQ6 | ~2.5% missing in several fields (occupation, soil, roof, flood_zone…) | NA scan | Explicit missing category / NaN handled by GBM |
| DQ7 | One motor bodily-injury claim of 11.9M CU (next largest 1.1M) | top-N by peril | Large-loss cap + spread excess as a loading |

## Leakage / non-admissible variables

| Variable | Why excluded |
|---|---|
| `customer_service_contacts` | **Outcome leakage**: rows with 0 contacts have 0.000 claims; contacts rise with claims (mean 0.41 for no-claim rows, 2.96 with one claim). Test distribution matches no-claim rows. |
| `renewal_decision` | Post-period and train-only; `declined_by_insurer` has 1.26 claims/row |
| `written_premium` | Current tariff — used only as a benchmark, not a feature (circularity, may not exist in Week 2) |
| `surname`, `email_domain`, `vehicle_colour`, `marketing_*`, `campaign_code`, `branch_id`, `document_preference`, `previous_insurer` | No causal link to risk and/or proxy for protected characteristics; excluded via an explicit list with a test |

## Claims and target

- Repudiated claims have incurred = 0 → excluding them is automatic and safe.
- Closed claims: paid = incurred. Recoveries only on motor own damage (~23%) and theft (~4%).
- Row-level target = Σ (incurred_to_date − recoveries) over non-repudiated claims whose loss_date falls in the row.
- Claim-to-row assignment: no overlapping rows, no multi-matches.

## Immaturity at 31/12/2024

- **Motor bodily injury is the dominant IBNR problem**: reported frequency 2024 = 5.9‰ vs ~10.5‰ in 2021–23; 95th percentile reporting delay ≈ 475 days; 80% of 2024 BI is still open.
- Subsidence: 95th percentile delay ≈ 342 days, 69% of 2024 still open.
- Other perils report within 1–2 months; 2024 Q4 counts are visibly incomplete.
- Case reserves look **roughly unbiased**: open vs closed mean incurred are comparable within cohort → IBNER assumed small (flagged as an uncertainty, notably for BI).
- Late-reported BI is ~20% more severe than early-reported BI (2021–22 cohorts).

## Trend

- Claims inflation on severity is clear: buildings ~+5–8% p.a. (escape of water, storm, flood), motor own damage ~+5%, third party property ~+8%, glass ~+8%, contents ~+3%.
- Frequencies broadly stable, except motor own damage / TPP drifting down (partly IBNR in 2024).
- Weather data includes **2025** for every address → we can use the actual weather of the year being predicted.

## Test set

- 85% of 2025 policies already appear in training → their own claims history is available as a feature (built in time order).
- Test exposure is correct; ~20% of rows are partial-year.
