"""
Critical-exponent estimation from Campaigns 1 and 2.

The measured quantity is the susceptibility exponent gamma:
    std(adoption) ~ |BDP - BDP_c|^{-gamma/2}
so the log-log slope equals -gamma/2.

Produces:
    fig06_critical_exponents.png  log-log variance scaling near BDP_c
    fig07_exponent_forest.png     forest plot of estimated gamma/2 values
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import linregress

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import (
    FIGURES_DIR, TOPO_COLORS, TOPO_LABELS, TOPOLOGIES,
)

# Re-use loaders from sibling modules
from phase_diagram import load_c1_data
from topology_universality import load_c2_data

# ── helpers ───────────────────────────────────────────────────────────────

def estimate_critical_point(bdps: np.ndarray,
                            std_adoptions: np.ndarray) -> float:
    """Return BDP_c = BDP at maximum std(adoption)."""
    idx = np.nanargmax(std_adoptions)
    return bdps[idx]


def fit_exponent(bdps: np.ndarray,
                 std_adoptions: np.ndarray,
                 bdp_c: float,
                 window: float = 1500.0):
    """Fit log(std_adoption) ~ slope * log(|BDP - BDP_c|) near BDP_c.

    Since std ~ |BDP - BDP_c|^{-gamma/2}, the slope = -gamma/2.
    Returns (gamma_half, r2) or (np.nan, np.nan) on failure,
    where gamma_half = -slope (positive).
    """
    eps = np.abs(bdps - bdp_c)
    mask = (eps > 0) & (eps <= window) & (std_adoptions > 0)
    if mask.sum() < 3:
        return np.nan, np.nan
    log_eps = np.log(eps[mask])
    log_std = np.log(std_adoptions[mask])
    slope, intercept, r, p, se = linregress(log_eps, log_std)
    gamma_half = -slope  # positive: std decreases away from BDP_c
    return gamma_half, r ** 2


def _agg_std(df: pd.DataFrame, group_col: str = "bdp"):
    """Aggregate adoption std over seeds per BDP."""
    agg = df.groupby(group_col)["adoption"].agg(["std"]).reset_index()
    agg.columns = [group_col, "std_adopt"]
    agg = agg.dropna(subset=["std_adopt"])
    return agg[group_col].values, agg["std_adopt"].values


# ── figure 6 — log-log exponent plot ─────────────────────────────────────

def plot_loglog_exponents(c1_df: pd.DataFrame,
                          c2_df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(9, 6))

    results = {}

    # WS from C1 at sigma_mult = 1.0, PLN
    ws_c1 = c1_df[(c1_df["regime"] == "pln") & (c1_df["sigma_mult"] == 1.0)]
    if not ws_c1.empty:
        bdps, stds = _agg_std(ws_c1)
        bdp_c = estimate_critical_point(bdps, stds)
        eps = np.abs(bdps - bdp_c)
        mask = (eps > 0) & (stds > 0)
        if mask.sum() >= 2:
            ax.scatter(np.log(eps[mask]), np.log(stds[mask]),
                       marker="s", s=40, color=TOPO_COLORS["ws"],
                       label=f"WS (C1, sm=1.0)", zorder=5)
        gamma_half, r2 = fit_exponent(bdps, stds, bdp_c)
        results["WS (C1)"] = (gamma_half, r2)

    # 4 topologies from C2, PLN
    for topo in TOPOLOGIES:
        sub = c2_df[(c2_df["regime"] == "pln") & (c2_df["topology"] == topo)]
        if sub.empty:
            continue
        bdps, stds = _agg_std(sub)
        bdp_c = estimate_critical_point(bdps, stds)
        eps = np.abs(bdps - bdp_c)
        mask = (eps > 0) & (stds > 0)
        if mask.sum() >= 2:
            ax.scatter(np.log(eps[mask]), np.log(stds[mask]),
                       marker="o", s=30, color=TOPO_COLORS[topo],
                       label=f"{TOPO_LABELS[topo]} (C2)", zorder=4)
        gamma_half, r2 = fit_exponent(bdps, stds, bdp_c)
        results[TOPO_LABELS[topo]] = (gamma_half, r2)

    # Reference slopes (negative, since std decreases away from BDP_c)
    x_ref = np.linspace(ax.get_xlim()[0] if ax.lines or ax.collections else 3,
                        ax.get_xlim()[1] if ax.lines or ax.collections else 8, 50)
    # recompute x range from data
    if ax.collections:
        all_x = np.concatenate([c.get_offsets()[:, 0] for c in ax.collections])
        lo, hi = all_x.min() - 0.5, all_x.max() + 0.5
        x_ref = np.linspace(lo, hi, 50)

    mid_y = np.mean(ax.get_ylim()) if ax.collections else -2.0
    for gamma_half_ref, label, ls in [
        (0.5, r"Mean-field $\gamma/2=0.5$", "--"),
        (0.875, r"2D Ising $\gamma/2=0.875$", "-."),
        (1.2, r"Percolation $\gamma/2\approx1.2$", ":"),
    ]:
        # slope is -gamma/2 in the ln-ln plane
        y_ref = -gamma_half_ref * (x_ref - x_ref.mean()) + mid_y
        ax.plot(x_ref, y_ref, ls, color="gray", alpha=0.6, label=label)

    ax.set_xlabel(r"$\ln\,|\mathrm{BDP} - \mathrm{BDP}_c|$")
    ax.set_ylabel(r"$\ln\,\mathrm{std}(\mathrm{adoption})$")
    ax.set_title(r"Susceptibility exponent: $\mathrm{std} \sim |\mathrm{BDP}-\mathrm{BDP}_c|^{-\gamma/2}$")
    ax.legend(fontsize=8, loc="best")
    plt.tight_layout()
    out = FIGURES_DIR / "fig06_critical_exponents.png"
    fig.savefig(out)
    plt.close(fig)
    print(f"Saved: {out}")

    return results


# ── figure 7 — forest plot of gamma/2 estimates ─────────────────────────

def plot_exponent_comparison(results: dict) -> None:
    """Horizontal forest plot of estimated gamma/2 values.

    `results`: {label: (gamma_half, r2), ...}
    """
    labels = [k for k, (g, _) in results.items() if not np.isnan(g)]
    gammas = [results[k][0] for k in labels]
    r2s = [results[k][1] for k in labels]

    if not labels:
        print("WARNING: no valid gamma estimates, skipping forest plot.")
        return

    fig, ax = plt.subplots(figsize=(8, max(3, 0.6 * len(labels) + 1.5)))
    y_pos = np.arange(len(labels))

    ax.barh(y_pos, gammas, height=0.5, color="#4c72b0", alpha=0.8)
    for yp, g, r2 in zip(y_pos, gammas, r2s):
        ax.text(g + 0.02, yp, f"{g:.3f}  ($R^2$={r2:.2f})",
                va="center", fontsize=9)

    # reference lines for gamma/2
    for val, lbl, col in [
        (0.5, r"Mean-field $\gamma/2$=0.5", "#e377c2"),
        (0.875, r"2D Ising $\gamma/2$=0.875", "#bcbd22"),
        (1.2, r"Percolation $\gamma/2 \approx$1.2", "#17becf"),
    ]:
        ax.axvline(val, ls="--", color=col, alpha=0.6, label=lbl)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=10)
    ax.set_xlabel(r"Estimated $\gamma/2$")
    ax.set_title(r"Susceptibility exponent $\gamma/2$ comparison")
    ax.legend(fontsize=8, loc="lower right")
    ax.set_xlim(left=0)
    ax.invert_yaxis()
    plt.tight_layout()
    out = FIGURES_DIR / "fig07_exponent_forest.png"
    fig.savefig(out)
    plt.close(fig)
    print(f"Saved: {out}")


# ── main ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Loading Campaign 1 data ...")
    c1 = load_c1_data()
    print(f"  C1 rows: {len(c1)}")

    print("Loading Campaign 2 data ...")
    c2 = load_c2_data()
    print(f"  C2 rows: {len(c2)}")

    results = plot_loglog_exponents(c1, c2)
    if results:
        plot_exponent_comparison(results)

    print("Done (critical_exponents).")
