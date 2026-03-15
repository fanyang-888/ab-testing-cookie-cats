# Cookie Cats Gate Placement A/B Test

This repository contains an A/B testing analysis of the **Cookie Cats** experiment, where the first in-game gate was placed at **level 30** (control) vs **level 40** (treatment). The goal is to evaluate whether moving the gate changes **retention** and **engagement**.

- Control: `gate_30`
- Treatment: `gate_40`

A small notebook demonstrates **deterministic hash bucketing** (how an online system can consistently assign users to A/B groups).

---

## Objectives

- To analyze the effect of gate placement (level 30 vs level 40) on Day-1 and Day-7 retention and on engagement (game rounds played).
- To apply two-sample tests for binary and continuous metrics and to interpret confidence intervals and p-values.
- To demonstrate deterministic hash-based assignment of users to experiment groups (as used in production A/B testing).

---

## Background / Theory

In level-based games, gates are used to control pacing and encourage progression. But gate placement is a trade-off:
- If the gate is too early, players may churn quickly.
- If it is too late, players may progress too freely and lose long-term engagement incentives.

This experiment asks:

> Does moving the first gate from level 30 to level 40 improve retention (especially Day 7), and what happens to engagement?

---

## Hypotheses

- **H0 (null):** There is no difference between `gate_30` and `gate_40` on the key metrics.
- **H1 (alternative):** `gate_40` changes the key metrics compared to `gate_30` (this experiment uses a two-sided test unless there is a strong reason for one-sided).

---

## Experiment Metrics

### Primary Metric
- **Day-7 retention (`retention_7`)**: whether a user returns on day 7 (0/1)

### Secondary Metrics
- **Day-1 retention (`retention_1`)**: whether a user returns on day 1 (0/1)
- **Engagement (`sum_gamerounds`)**: total game rounds played in the first week (continuous)

### Guardrails (practical)
The dataset does not include direct “negative experience” metrics (crashes, complaints, refunds). This lab treats:
- `retention_1` as a short-term guardrail (avoid improving D7 while hurting D1 too much)
- robustness checks for `sum_gamerounds` (to avoid conclusions driven by extreme outliers / heavy users)

---

## Experiment Design

- **Unit of randomization:** `userid` (user-level)
- **Allocation:** two variants (`gate_30` vs `gate_40`)
- **Analysis window:** **D0–D7** after first exposure
  - `sum_gamerounds` is the first-week total
  - `retention_1` and `retention_7` are binary return indicators
- **Assignment in production (concept):** deterministic hashing / bucketing (see `code/hash_bucketing.ipynb`)

---

## Data Schema

Expected columns:
- `userid` (int): user identifier
- `version` (str): experiment group (`gate_30` or `gate_40`)
- `sum_gamerounds` (int/float): rounds played in first week
- `retention_1` (0/1): returned on day 1
- `retention_7` (0/1): returned on day 7

Data file location (recommended):
- `data/cookie_cats.csv`

> Note: If the original dataset cannot be shared publicly, I will keep only a small sample file and document how to reproduce results.

---

## Methods (what I run)

### Binary metrics (retention)
- two-sample proportion test (z-test) for difference in retention rates
- confidence intervals for the lift (treatment - control)
- bootstrap as a robustness check (optional but helpful)

### Continuous metric (engagement)
- Welch’s t-test (does not assume equal variance)
- Mann–Whitney U test (non-parametric robustness check)
- outlier sensitivity checks (e.g., trimming / winsorization), because `sum_gamerounds` can be heavy-tailed

### Data quality checks
- SRM (Sample Ratio Mismatch): verify group sizes are consistent with expected allocation
- basic sanity checks: missing values, duplicates, extreme outliers

---

## Repo Structure

```text
├── code/
│   ├── A_B_Testing_Python.ipynb # main analysis notebook
│   └── hash_bucketing.ipynb     # deterministic hash bucketing example
├── data/
│   ├── README.md                # data notes + schema
│   └── cookie_cats.xlsx
└── file/
    ├── report.md                # final write-up (to be generated)
    └── figs/                    # saved charts (to be generated)
```

---

## Procedure

### How to Run (recommended)
1) Put the dataset at:
   - `data/cookie_cats.csv`
2) Open and run:
   - `code/A_B_Testing_Python.ipynb`
   - `code/hash_bucketing.ipynb` (optional)

### Option 2: (Planned) Scripted run
I plan to add a script entry point so that running one command generates:
- `file/report.md`
- charts in `file/figs/`

---

## Results / Conclusion (TODO)
I will summarize:
- the estimated lift on **Day-7 retention** (primary), with CI and p-value
- what happens to **Day-1 retention** and **engagement**
- whether the recommendation is **ship / iterate / rollback**
- limitations and assumptions

---

## Notes / Next Steps
- add automated SRM checks + plots
- add multiple testing correction (Holm or BH-FDR) when comparing several metrics/segments
- add segmented analysis (if more user attributes are available)
- convert the notebook results into a clean `file/report.md`

---

## License
TBD


