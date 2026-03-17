# Cookie Cats A/B Test Report (generated)

## Data Validation
- **Control (`gate_30`) sample size:** 44,700
- **Treatment (`gate_40`) sample size:** 45,489
- **SRM check (chi-square):** chi2 = 6.9024, p = 0.0086 -> **FAIL (possible SRM)**
- **User ID parity balance check:** chi2 = 2.3951, p = 0.1217
- **User ID last-digit balance check:** chi2 = 5.4216, p = 0.7961
- **Gamerounds distribution KS test:** statistic = 0.0103, p = 0.0171
- **Validity interpretation:** sample-ratio mismatch is flagged, while ID-balance proxies are acceptable; interpret treatment effects with additional caution.

## Primary metric: Day-7 retention
- **Lift (gate_40 - gate_30):** -0.82 pp (control 19.02% vs treatment 18.20%)
- **95% CI (difference):** [-1.33 pp, -0.31 pp]
- **p-value (two-sided proportion z-test):** 0.0016

## Secondary metrics
- **Day-1 retention lift:** -0.59 pp; **95% CI:** [-1.24 pp, 0.06 pp]; **p-value:** 0.0744
- **sum_gamerounds mean difference (treatment - control):** -1.16
- **Mann-Whitney U p-value:** 0.0502
- **1% trimmed mean (control vs treatment):** 45.11 vs 44.83
- **Bootstrap mean-diff 95% CI:** [-4.03, 0.99]

## Power Analysis (D7 retention)
- **Assumptions:** two-sided alpha = 0.05, target power = 0.80, baseline = control D7 (19.02%)
- **Current-sample MDE:** about 0.73 pp absolute change
- **Required n/group for +0.50 pp detection:** ~96,714
- **Required n/group for +1.00 pp detection:** ~24,178

## Recommendation
Rollback / Do not ship gate_40.

## Artifacts
- `figures/retention_plot.png`
- `figures/gamerounds_distribution.png`
- `figures/bootstrap_difference.png`
- `figures/srm_check.png`
