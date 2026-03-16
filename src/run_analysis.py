"""
Run Cookie Cats A/B test analysis: load data, run tests, write report and figures.
Expects data/cookie_cats.csv; writes reports/report.md and figures/*.png.
"""
import os
import sys

import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path

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


def main():
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    df = load_data()
    ctrl = df[df["version"] == "gate_30"]
    trt = df[df["version"] == "gate_40"]
    n1, n2 = len(ctrl), len(trt)

    # Retention rates
    r1_ctrl = ctrl["retention_1"].mean()
    r1_trt = trt["retention_1"].mean()
    r7_ctrl = ctrl["retention_7"].mean()
    r7_trt = trt["retention_7"].mean()

    delta_1, p1, (ci1_low, ci1_high) = proportion_ztest_and_ci(
        n1, r1_ctrl, n2, r1_trt
    )
    delta_7, p7, (ci7_low, ci7_high) = proportion_ztest_and_ci(
        n1, r7_ctrl, n2, r7_trt
    )

    # Engagement: Mann-Whitney (two-sided)
    _, p_gamerounds = stats.mannwhitneyu(
        ctrl["sum_gamerounds"], trt["sum_gamerounds"], alternative="two-sided"
    )
    mean_diff_rounds = trt["sum_gamerounds"].mean() - ctrl["sum_gamerounds"].mean()

    # Build report
    report = f"""# Cookie Cats A/B Test Report (generated)

## Primary: Day-7 retention
- **Lift (gate_40 vs gate_30):** {delta_7 * 100:.2f} pp (control {r7_ctrl * 100:.2f}% vs treatment {r7_trt * 100:.2f}%)
- **95% CI (difference):** [{ci7_low:.4f}, {ci7_high:.4f}]
- **p-value (two-sided proportion z-test):** {p7:.4f}

## Secondary: Day-1 retention
- **Lift:** {delta_1 * 100:.2f} pp; **p-value:** {p1:.4f}; **95% CI:** [{ci1_low:.4f}, {ci1_high:.4f}]

## Engagement (sum_gamerounds)
- **Mean difference (treatment - control):** {mean_diff_rounds:.2f}
- **p-value (Mann-Whitney U, two-sided):** {p_gamerounds:.4f}

## Recommendation
{"Rollback / Do not ship gate_40." if p7 < 0.05 and delta_7 < 0 else "See README for full recommendation."}
"""

    report_path = REPO_ROOT / "reports" / "report.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")
    print(f"Wrote {report_path}")

    # Simple figure: retention comparison
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(1, 2, figsize=(8, 4))
        for ax_i, (name, vals) in enumerate([
            ("Day-1 retention", (r1_ctrl, r1_trt)),
            ("Day-7 retention", (r7_ctrl, r7_trt)),
        ]):
            ax[ax_i].bar(["gate_30", "gate_40"], vals, color=["#1f77b4", "#ff7f0e"])
            ax[ax_i].set_ylabel("Rate")
            ax[ax_i].set_title(name)
        plt.tight_layout()
        plt.savefig(FIGURES_DIR / "retention_comparison.png", dpi=100)
        plt.close()
        print(f"Wrote {FIGURES_DIR / 'retention_comparison.png'}")
    except Exception as e:
        print(f"Could not save figure: {e}")

    print("Done.")


if __name__ == "__main__":
    main()
