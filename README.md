# Cookie Cats A/B Test: Gate Placement Decision

A/B testing analysis of the Cookie Cats gate placement experiment, focused on retention, engagement, and business decision quality.

## Executive Summary
- **Problem:** Should the first gate move from level 30 (`gate_30`) to level 40 (`gate_40`)?
- **Experiment setup:** User-level randomized A/B test, 90,189 users total.
- **Sample sizes:** `gate_30` = 44,700; `gate_40` = 45,489. No meaningful SRM signal for a 50/50 split.
- **Primary metric (D7 retention):** `gate_40` decreased D7 retention by **0.82 pp** (19.02% to 18.20%), 95% CI **[-1.33 pp, -0.31 pp]**, p = **0.0016**.
- **Secondary metrics:** D1 retention decreased by **0.59 pp** (p = 0.0744; not significant). `sum_gamerounds` showed no robust improvement for `gate_40` (Mann-Whitney p = 0.0502; tiny mean delta).
- **Recommendation:** **Do not ship `gate_40`. Keep `gate_30` and test alternative pacing ideas.**

## Key Result and Conclusion
The treatment harms the primary metric (D7 retention) with statistical and practical significance, while not delivering clear upside on D1 retention or engagement. This is a negative tradeoff and should be rejected in production.

## Quick Reproducibility
1. Install dependencies: `pip install -r requirements.txt`
2. Put the dataset at `data/cookie_cats.csv` (see `data/readme.md`)
3. Run analysis: `python src/run_analysis.py`
4. Review outputs:
   - `reports/report.md`
   - `figures/*.png`

## Project Structure

```text
├── README.md
├── requirements.txt
├── src/
│   └── run_analysis.py
├── notebooks/
│   ├── A_B_Testing_Python.ipynb
│   └── hash_bucketing.ipynb
├── data/
│   ├── readme.md
│   └── cookie_cats.csv
├── reports/
│   └── report.md
└── figures/
    └── *.png
```

## Experiment Design
- **Unit of randomization:** `userid`
- **Variants:** `gate_30` (control) vs `gate_40` (treatment)
- **Window:** D0-D7 after first exposure
- **Primary metric:** `retention_7`
- **Secondary metrics:** `retention_1`, `sum_gamerounds`

## Methods
- **Retention metrics:** two-sample proportion z-test + 95% CI for treatment minus control.
- **Engagement metric:** Mann-Whitney U test (robust to heavy tails), plus practical effect-size interpretation.
- **Data quality:** SRM check for expected 50/50 allocation, basic schema and missing-value checks.

## Business Recommendation
- **Decision:** Roll back `gate_40` and keep `gate_30`.
- **Why not p-value only:** decision is based on direction, size, uncertainty, and product impact, not significance alone.
- **Next experiment:** test pacing variants that preserve D7 while monitoring D1 and engagement guardrails.

## Limitations
- D0-D7 window only; no long-run retention or revenue outcomes.
- No segmentation by cohort/region/device.
- No multiple-testing adjustment across all possible cuts.
- Engagement distribution is heavy-tailed; non-parametric results are preferred.

## License
Personal portfolio project.


