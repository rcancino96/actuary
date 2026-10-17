# CLAUDE.md — project context (read first)

IAA AI-Assisted Hackathon 2026. Owner: Raul Cancino (non-life actuary). Communicate in Spanish; code/docs in English.

## Task
Predict 2025 expected **ultimate** claim cost per policy row for motor, buildings, contents:
final cost of claims with loss date in the row period, net of excess (already net in `paid/incurred`), net of recoveries, excluding repudiated.
Metric: **Tweedie D², power 1.5**, one CSV `row_id,prediction` for all three test files (likely scored jointly → cross-line level calibration matters). Predictions ≥ 0; use a small positive floor, never exactly 0.

Grading: 40% accuracy W1+W2 & adaptation, 25% AI use (log in `docs/ai_log.md`: proposal → verification → human decision), 20% validation/governance/tests, 15% video (5 min) + report (5 pages) + git repo. Week 2 = new market dataset → keep pipeline modular (target build / features / model / drift checks).

## Data
Raw parquet in `data/raw/public/` (gitignored, not in repo — re-download from Kaggle or unzip the competition zip there).
Read IDs as strings. Run Python scripts with `python3 -I`.

## Confirmed findings (see docs/01_data_findings.md; scripts in src/eda/)
Data quality fixes:
- exposure wrong on ~0.4% rows (1.0139, or in days e.g. 365) → recompute from dates `(end-start+1)/365.25`
- sum_insured ×1000 on ~0.2% buildings/contents rows (>2M; also in test) → /1000
- construction_type: lower-case; T/t (2021–22) and W/w (2023+, test) → `timber`
- 604 duplicate claims (identical except claim_id) → drop
- 413 claims outside any policy row (mostly 2020 loss dates) → exclude
- one motor BI claim 11.9M (next 1.1M) → large-loss cap + spread as loading
- ~2.5% NAs in several fields

Excluded features (with reason, enforce with a test):
- `customer_service_contacts` — OUTCOME LEAKAGE (0 contacts ⇒ 0 claims; test dist = no-claim rows)
- `renewal_decision` — post-period, train only
- `written_premium` — benchmark only, not a feature
- surname, email_domain, vehicle_colour, marketing_segment, marketing_consent, campaign_code, branch_id, document_preference, previous_insurer — no risk rationale / protected-proxy

Claims/target:
- Repudiated have incurred=0. Closed: paid=incurred. Recoveries only motor own_damage (~23%) and theft (~4%).
- Claim→row assignment by policy_id + loss_date in [period_start, period_end]: no overlaps, no multi-matches.
- IBNR: motor bodily_injury reported freq 2024 = 5.9‰ vs ~10.5‰ 2021–23 (p95 delay ~475d, 80% of 2024 open); subsidence p95 ~342d; other perils report in 1–2 months (2024 Q4 incomplete).
- Case reserves look ~unbiased (open vs closed severity comparable within cohort) → IBNER ≈ 0, flagged as uncertainty. Late BI ~20% more severe.
- Severity inflation: buildings +5–8% p.a., motor TPP ~8%, own damage ~5%, glass ~8%, contents ~3%.
- Open question: BI median fell ~13.4k (2021–22) → ~9.8k (2023–24): immaturity mix or regime change (whiplash-type reform)?
- Weather has 2025 values for every address → use actual year weather.
- 85% of test policies exist in train → own claims history feature (strictly prior to row start).
- Test exposure is clean; ~20% partial-year rows.

## Plan (next steps)
1. `src/target.py`: per-peril ultimate & 2025 on-level target — count IBNR via delay triangle (applied by row exposure dates), severity/frequency trend to 2025, large-loss cap + loading. Unit tests on reconciliation.
2. `src/metric.py`: Tweedie D² p=1.5 (+ tests). Temporal validation: train 2021–22→val 2023; train 2021–23→val 2024.
3. Benchmarks: line mean, rescaled written_premium, GLM Tweedie.
4. Main: LightGBM Tweedie per line (exposure as weight/offset); compare; calibrate level per line.
5. Tests (pytest): no excluded features, predictions ≥ floor, row count = sample_submission, per-line totals vs expected.

## Environment
pip: pandas pyarrow lightgbm scikit-learn (use `--break-system-packages` if needed).
