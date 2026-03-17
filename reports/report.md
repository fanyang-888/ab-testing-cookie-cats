# Cookie Cats A/B Test Report (generated)

## Experiment and data quality checks
- **Control (`gate_30`) sample size:** 44,700
- **Treatment (`gate_40`) sample size:** 45,489
- **SRM check (chi-square):** chi2 = 6.9024, p = 0.0086 -> **FAIL (possible SRM)**

## Primary metric: Day-7 retention
- **Lift (gate_40 - gate_30):** -0.82 pp (control 19.02% vs treatment 18.20%)
- **95% CI (difference):** [-1.33 pp, -0.31 pp]
- **p-value (two-sided proportion z-test):** 0.0016

## Secondary metrics
- **Day-1 retention lift:** -0.59 pp; **95% CI:** [-1.24 pp, 0.06 pp]; **p-value:** 0.0744
- **sum_gamerounds mean difference (treatment - control):** -1.16
- **Mann-Whitney U p-value:** 0.0502
- **1% trimmed mean (control vs treatment):** 45.11 vs 44.83

## Recommendation
Rollback / Do not ship gate_40.

## Artifacts
- `figures/retention_with_ci.png`
- `figures/gamerounds_boxplot_trimmed.png`
- `figures/sample_size_srm_check.png`
