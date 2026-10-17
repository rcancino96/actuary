# AI-assisted workflow log

Each entry: what the AI proposed or found → how it was verified → human decision.

| Date | Stage | AI contribution | Verification | Human decision |
|---|---|---|---|---|
| 2026-10-17 | Scoping | Read the brief; flagged ultimate vs incurred, Tweedie zero-prediction risk, leakage candidates (renewal_decision, written_premium) | Checked against data dictionary | Accepted plan |
| 2026-10-17 | EDA | Wrote 9 inspection scripts; detected exposure-in-days rows, SI ×1000, T→W recode, duplicate claims | Each issue reproduced by code with counts (docs/01) | Treatments accepted |
| 2026-10-17 | EDA | Found `customer_service_contacts` is outcome leakage | Claims/row = 0.000 when contacts = 0; test distribution matches no-claim rows | Excluded |
| 2026-10-17 | EDA | Identified BI IBNR (2024 freq 5.9‰ vs 10.5‰) and case-reserve adequacy check | Open vs closed severity by cohort | IBNR via delay triangle; IBNER assumed ~0, flagged |
