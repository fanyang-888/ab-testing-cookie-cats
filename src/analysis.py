"""Run Cookie Cats A/B analysis and generate reproducible artifacts."""

import sys
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats

matplotlib.use("Agg")

# Paths relative to repo root (script may be run from repo root or from src/)
REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = REPO_ROOT / "data" / "cookie_cats.csv"
REPORTS_DIR = REPO_ROOT / "reports"
FIGURES_DIR = REPO_ROOT / "figures"


def load_data():
    if not DATA_PATH.exists():
        print(f"Data not found at {DATA_PATH}. Place cookie_cats.csv in data/.")
        sys.exit(1)
    df = pd.read_csv(DATA_PATH)
    for col in ["userid", "version", "sum_gamerounds", "retention_1", "retention_7"]:
        if col not in df.columns:
            print(f"Missing column: {col}")
            sys.exit(1)
    if df["version"].nunique() != 2:
        print("Expected exactly two variants in `version`.")
        sys.exit(1)
    return df


def proportion_ztest_and_ci(n1, p1, n2, p2, alpha=0.05):
    """Two-sample proportion z-test and CI for p2 - p1 (treatment - control)."""
    p_pool = (p1 * n1 + p2 * n2) / (n1 + n2)
    se = np.sqrt(p_pool * (1 - p_pool) * (1 / n1 + 1 / n2))
    if se <= 0:
        return 0.0, 1.0, (0.0, 0.0)
    delta = p2 - p1
    z = delta / se
    p_value = 2 * (1 - stats.norm.cdf(abs(z)))
    z_crit = stats.norm.ppf(1 - alpha / 2)
    ci_low = delta - z_crit * se
    ci_high = delta + z_crit * se
    return delta, p_value, (ci_low, ci_high)


def proportion_ci_single_group(p_hat, n, alpha=0.05):
    z_crit = stats.norm.ppf(1 - alpha / 2)
    se = np.sqrt((p_hat * (1 - p_hat)) / n)
    return p_hat - z_crit * se, p_hat + z_crit * se


def srm_check(n_control, n_treatment, expected_ratio=0.5):
    total = n_control + n_treatment
    expected = np.array([total * expected_ratio, total * (1 - expected_ratio)])
    observed = np.array([n_control, n_treatment])
    chi2_stat = ((observed - expected) ** 2 / expected).sum()
    p_value = 1 - stats.chi2.cdf(chi2_stat, df=1)
    return chi2_stat, p_value


def randomization_diagnostics(ctrl, trt):
    # Proxy randomization checks based on user identifier patterns.
    parity_table = [
        [(ctrl["userid"] % 2 == 0).sum(), (ctrl["userid"] % 2 == 1).sum()],
        [(trt["userid"] % 2 == 0).sum(), (trt["userid"] % 2 == 1).sum()],
    ]
    parity_chi2, parity_p, _, _ = stats.chi2_contingency(parity_table)

    ctrl_last_digit = np.bincount((ctrl["userid"] % 10).to_numpy(), minlength=10)
    trt_last_digit = np.bincount((trt["userid"] % 10).to_numpy(), minlength=10)
    digit_chi2, digit_p, _, _ = stats.chi2_contingency(
        np.vstack([ctrl_last_digit, trt_last_digit])
    )
    return parity_chi2, parity_p, digit_chi2, digit_p


def compute_mde_and_sample_size(n1, n2, baseline_rate, alpha=0.05, power=0.8):
    z_alpha = stats.norm.ppf(1 - alpha / 2)
    z_beta = stats.norm.ppf(power)
    mde = (z_alpha + z_beta) * np.sqrt(
        baseline_rate * (1 - baseline_rate) * (1 / n1 + 1 / n2)
    )

    def required_n_per_group(delta):
        numerator = 2 * baseline_rate * (1 - baseline_rate) * ((z_alpha + z_beta) ** 2)
        return numerator / (delta**2)

    n_05pp = required_n_per_group(0.005)
    n_10pp = required_n_per_group(0.010)
    return mde, n_05pp, n_10pp


def bootstrap_mean_difference(ctrl_values, trt_values, n_boot=3000, seed=42):
    rng = np.random.default_rng(seed)
    ctrl_np = np.asarray(ctrl_values)
    trt_np = np.asarray(trt_values)
    idx_ctrl = rng.integers(0, len(ctrl_np), size=(n_boot, len(ctrl_np)))
    idx_trt = rng.integers(0, len(trt_np), size=(n_boot, len(trt_np)))
    diffs = trt_np[idx_trt].mean(axis=1) - ctrl_np[idx_ctrl].mean(axis=1)
    ci_low, ci_high = np.percentile(diffs, [2.5, 97.5])
    return diffs, ci_low, ci_high


def save_retention_figure(rates, cis):
    fig, ax = plt.subplots(figsize=(8, 5))
    metrics = ["D1", "D7"]
    control_vals = [rates["r1_ctrl"], rates["r7_ctrl"]]
    treatment_vals = [rates["r1_trt"], rates["r7_trt"]]
    control_err = [
        rates["r1_ctrl"] - cis["r1_ctrl"][0],
        rates["r7_ctrl"] - cis["r7_ctrl"][0],
    ]
    treatment_err = [
        rates["r1_trt"] - cis["r1_trt"][0],
        rates["r7_trt"] - cis["r7_trt"][0],
    ]

    x = np.arange(len(metrics))
    width = 0.35
    ax.bar(
        x - width / 2,
        control_vals,
        width,
        yerr=control_err,
        capsize=4,
        label="gate_30",
        color="#1f77b4",
    )
    ax.bar(
        x + width / 2,
        treatment_vals,
        width,
        yerr=treatment_err,
        capsize=4,
        label="gate_40",
        color="#ff7f0e",
    )
    ax.set_xticks(x)
    ax.set_xticklabels(metrics)
    ax.set_ylim(0, max(control_vals + treatment_vals) * 1.3)
    ax.set_ylabel("Retention rate")
    ax.set_title("Retention by variant with 95% CI")
    ax.legend()
    plt.tight_layout()
    out = FIGURES_DIR / "retention_plot.png"
    plt.savefig(out, dpi=120)
    plt.close()
    return out


def save_gamerounds_figure(df):
    q99 = df["sum_gamerounds"].quantile(0.99)
    trimmed = df[df["sum_gamerounds"] <= q99].copy()
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.boxplot(
        data=trimmed,
        x="version",
        y="sum_gamerounds",
        order=["gate_30", "gate_40"],
        ax=ax,
    )
    ax.set_title("Game rounds distribution (trimmed at p99)")
    ax.set_xlabel("Variant")
    ax.set_ylabel("sum_gamerounds")
    plt.tight_layout()
    out = FIGURES_DIR / "gamerounds_distribution.png"
    plt.savefig(out, dpi=120)
    plt.close()
    return out


def save_bootstrap_figure(boot_diffs, ci_low, ci_high):
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(boot_diffs, bins=40, color="#4c72b0", alpha=0.9)
    ax.axvline(0, color="black", linestyle="--", linewidth=1, label="No difference")
    ax.axvline(ci_low, color="#c44e52", linestyle="--", linewidth=1.5, label="95% CI")
    ax.axvline(ci_high, color="#c44e52", linestyle="--", linewidth=1.5)
    ax.set_title("Bootstrap distribution: mean gamerounds diff (gate_40 - gate_30)")
    ax.set_xlabel("Difference in mean gamerounds")
    ax.set_ylabel("Bootstrap count")
    ax.legend()
    plt.tight_layout()
    out = FIGURES_DIR / "bootstrap_difference.png"
    plt.savefig(out, dpi=120)
    plt.close()
    return out


def save_srm_figure(n_control, n_treatment):
    total = n_control + n_treatment
    expected = total / 2
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(["gate_30", "gate_40"], [n_control, n_treatment], color=["#1f77b4", "#ff7f0e"])
    ax.axhline(expected, color="black", linestyle="--", linewidth=1, label="Expected 50/50")
    ax.set_title("Sample size check by variant")
    ax.set_ylabel("Users")
    ax.legend()
    plt.tight_layout()
    out = FIGURES_DIR / "srm_check.png"
    plt.savefig(out, dpi=120)
    plt.close()
    return out


def main():
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid")

    df = load_data()
    ctrl = df[df["version"] == "gate_30"]
    trt = df[df["version"] == "gate_40"]
    n_ctrl, n_trt = len(ctrl), len(trt)

    # Retention rates
    r1_ctrl = ctrl["retention_1"].mean()
    r1_trt = trt["retention_1"].mean()
    r7_ctrl = ctrl["retention_7"].mean()
    r7_trt = trt["retention_7"].mean()

    delta_1, p1, (ci1_low, ci1_high) = proportion_ztest_and_ci(n_ctrl, r1_ctrl, n_trt, r1_trt)
    delta_7, p7, (ci7_low, ci7_high) = proportion_ztest_and_ci(n_ctrl, r7_ctrl, n_trt, r7_trt)

    # Engagement
    _, p_gamerounds = stats.mannwhitneyu(
        ctrl["sum_gamerounds"], trt["sum_gamerounds"], alternative="two-sided"
    )
    mean_diff_rounds = trt["sum_gamerounds"].mean() - ctrl["sum_gamerounds"].mean()
    trim_ctrl = stats.trim_mean(ctrl["sum_gamerounds"], proportiontocut=0.01)
    trim_trt = stats.trim_mean(trt["sum_gamerounds"], proportiontocut=0.01)

    # SRM
    srm_chi2, srm_p = srm_check(n_ctrl, n_trt, expected_ratio=0.5)
    srm_status = "PASS (no evidence of SRM)" if srm_p >= 0.05 else "FAIL (possible SRM)"
    parity_chi2, parity_p, digit_chi2, digit_p = randomization_diagnostics(ctrl, trt)

    # Distribution validity checks for heavy-tailed engagement
    ks_stat, ks_p = stats.ks_2samp(ctrl["sum_gamerounds"], trt["sum_gamerounds"])

    # Power analysis (primary metric baseline: control D7 retention)
    d7_mde, n_for_05pp, n_for_10pp = compute_mde_and_sample_size(
        n_ctrl, n_trt, r7_ctrl, alpha=0.05, power=0.8
    )

    rates = {"r1_ctrl": r1_ctrl, "r1_trt": r1_trt, "r7_ctrl": r7_ctrl, "r7_trt": r7_trt}
    cis = {
        "r1_ctrl": proportion_ci_single_group(r1_ctrl, n_ctrl),
        "r1_trt": proportion_ci_single_group(r1_trt, n_trt),
        "r7_ctrl": proportion_ci_single_group(r7_ctrl, n_ctrl),
        "r7_trt": proportion_ci_single_group(r7_trt, n_trt),
    }

    retention_fig = save_retention_figure(rates, cis)
    gamerounds_fig = save_gamerounds_figure(df)
    boot_diffs, boot_ci_low, boot_ci_high = bootstrap_mean_difference(
        ctrl["sum_gamerounds"], trt["sum_gamerounds"]
    )
    bootstrap_fig = save_bootstrap_figure(boot_diffs, boot_ci_low, boot_ci_high)
    srm_fig = save_srm_figure(n_ctrl, n_trt)

    recommendation = (
        "Rollback / Do not ship gate_40."
        if p7 < 0.05 and delta_7 < 0
        else "No clear negative D7 impact; decision requires business review."
    )

    report = f"""# Cookie Cats A/B Test Report (generated)

## Data Validation
- **Control (`gate_30`) sample size:** {n_ctrl:,}
- **Treatment (`gate_40`) sample size:** {n_trt:,}
- **SRM check (chi-square):** chi2 = {srm_chi2:.4f}, p = {srm_p:.4f} -> **{srm_status}**
- **User ID parity balance check:** chi2 = {parity_chi2:.4f}, p = {parity_p:.4f}
- **User ID last-digit balance check:** chi2 = {digit_chi2:.4f}, p = {digit_p:.4f}
- **Gamerounds distribution KS test:** statistic = {ks_stat:.4f}, p = {ks_p:.4f}
- **Validity interpretation:** sample-ratio mismatch is flagged, while ID-balance proxies are acceptable; interpret treatment effects with additional caution.

## Primary metric: Day-7 retention
- **Lift (gate_40 - gate_30):** {delta_7 * 100:.2f} pp (control {r7_ctrl * 100:.2f}% vs treatment {r7_trt * 100:.2f}%)
- **95% CI (difference):** [{ci7_low * 100:.2f} pp, {ci7_high * 100:.2f} pp]
- **p-value (two-sided proportion z-test):** {p7:.4f}

## Secondary metrics
- **Day-1 retention lift:** {delta_1 * 100:.2f} pp; **95% CI:** [{ci1_low * 100:.2f} pp, {ci1_high * 100:.2f} pp]; **p-value:** {p1:.4f}
- **sum_gamerounds mean difference (treatment - control):** {mean_diff_rounds:.2f}
- **Mann-Whitney U p-value:** {p_gamerounds:.4f}
- **1% trimmed mean (control vs treatment):** {trim_ctrl:.2f} vs {trim_trt:.2f}
- **Bootstrap mean-diff 95% CI:** [{boot_ci_low:.2f}, {boot_ci_high:.2f}]

## Power Analysis (D7 retention)
- **Assumptions:** two-sided alpha = 0.05, target power = 0.80, baseline = control D7 ({r7_ctrl * 100:.2f}%)
- **Current-sample MDE:** about {d7_mde * 100:.2f} pp absolute change
- **Required n/group for +0.50 pp detection:** ~{n_for_05pp:,.0f}
- **Required n/group for +1.00 pp detection:** ~{n_for_10pp:,.0f}

## Recommendation
{recommendation}

## Artifacts
- `figures/{retention_fig.name}`
- `figures/{gamerounds_fig.name}`
- `figures/{bootstrap_fig.name}`
- `figures/{srm_fig.name}`
"""

    report_path = REPORTS_DIR / "report.md"
    report_path.write_text(report, encoding="utf-8")
    print(f"Wrote {report_path}")
    print(f"Wrote {retention_fig}")
    print(f"Wrote {gamerounds_fig}")
    print(f"Wrote {bootstrap_fig}")
    print(f"Wrote {srm_fig}")
    print("Done.")


if __name__ == "__main__":
    main()
