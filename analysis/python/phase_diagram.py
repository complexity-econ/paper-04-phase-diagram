"""
Campaign 1 analysis -- phase diagram in (BDP, sigma_mult) space.

Produces:
    fig01_phase_diagram.png      mean adoption heatmap (PLN / EUR)
    fig02_variance_landscape.png std(adoption) heatmap  (PLN / EUR)
    fig03_cross_sections.png     adoption vs BDP for selected sigma slices
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# allow sibling import
sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import (
    RESULTS_DIR, FIGURES_DIR, REGIME_COLORS, REGIME_LABELS,
    BDP_LEVELS_21, SIGMA_MULTS, read_terminal,
)

# ── data loading ──────────────────────────────────────────────────────────

def _mult_str(mult: float) -> str:
    """0.1 -> '0_1', 1.0 -> '1_0', 10.0 -> '10_0'."""
    return str(mult).replace(".", "_")


def load_c1_data() -> pd.DataFrame:
    """Read all Campaign-1 terminal CSVs.

    Returns a long DataFrame with columns:
        bdp, sigma_mult, regime, seed, adoption, inflation, unemployment, ...
    """
    rows = []
    base = RESULTS_DIR / "c1_phase"
    for regime in ("pln", "eur"):
        regime_dir = base / regime
        for sm in SIGMA_MULTS:
            ms = _mult_str(sm)
            for bdp in BDP_LEVELS_21:
                fname = f"c1_{regime}_sm{ms}_bdp{bdp}_terminal.csv"
                fpath = regime_dir / fname
                if not fpath.exists():
                    continue
                try:
                    df = read_terminal(fpath)
                except Exception as exc:
                    print(f"WARNING: cannot read {fpath}: {exc}")
                    continue
                df = df.copy()
                df["bdp"] = bdp
                df["sigma_mult"] = sm
                df["regime"] = regime
                df.rename(columns={"TotalAdoption": "adoption",
                                   "Inflation": "inflation",
                                   "Unemployment": "unemployment"},
                          inplace=True)
                rows.append(df)
    if not rows:
        print("WARNING: no C1 data found.")
        return pd.DataFrame()
    return pd.concat(rows, ignore_index=True)


# ── figure 1 — phase heatmap ─────────────────────────────────────────────

def plot_phase_heatmap(df: pd.DataFrame) -> None:
    if df.empty:
        print("WARNING: empty dataframe, skipping phase heatmap.")
        return

    fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharey=True)
    bdps = sorted(df["bdp"].unique())
    sms = sorted(df["sigma_mult"].unique())

    for ax, regime in zip(axes, ("pln", "eur")):
        sub = df[df["regime"] == regime]
        grid = np.full((len(sms), len(bdps)), np.nan)
        for i, sm in enumerate(sms):
            for j, b in enumerate(bdps):
                vals = sub.loc[(sub["sigma_mult"] == sm) &
                               (sub["bdp"] == b), "adoption"]
                if len(vals):
                    grid[i, j] = vals.mean()

        im = ax.pcolormesh(
            bdps, sms, grid,
            shading="nearest",
            cmap="viridis",
            vmin=0, vmax=1,
        )
        ax.set_yscale("log")
        # phase boundary contour at 20 % adoption
        try:
            X, Y = np.meshgrid(bdps, sms)
            ax.contour(X, Y, grid, levels=[0.20],
                       colors="white", linewidths=1.5, linestyles="--")
        except Exception:
            pass
        ax.set_xlabel("BDP (PLN)")
        ax.set_title(f"{REGIME_LABELS[regime]} regime")

    axes[0].set_ylabel(r"$\sigma$ multiplier")
    fig.colorbar(im, ax=axes, label="Mean adoption", shrink=0.8)
    fig.suptitle("Phase diagram: mean AI adoption", fontsize=14, y=1.02)
    plt.tight_layout()
    out = FIGURES_DIR / "fig01_phase_diagram.png"
    fig.savefig(out)
    plt.close(fig)
    print(f"Saved: {out}")


# ── figure 2 — variance landscape ────────────────────────────────────────

def plot_variance_landscape(df: pd.DataFrame) -> None:
    if df.empty:
        print("WARNING: empty dataframe, skipping variance landscape.")
        return

    fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharey=True)
    bdps = sorted(df["bdp"].unique())
    sms = sorted(df["sigma_mult"].unique())

    for ax, regime in zip(axes, ("pln", "eur")):
        sub = df[df["regime"] == regime]
        grid = np.full((len(sms), len(bdps)), np.nan)
        for i, sm in enumerate(sms):
            for j, b in enumerate(bdps):
                vals = sub.loc[(sub["sigma_mult"] == sm) &
                               (sub["bdp"] == b), "adoption"]
                if len(vals):
                    grid[i, j] = vals.std()

        im = ax.pcolormesh(
            bdps, sms, grid,
            shading="nearest",
            cmap="inferno",
        )
        ax.set_yscale("log")
        ax.set_xlabel("BDP (PLN)")
        ax.set_title(f"{REGIME_LABELS[regime]} regime")

    axes[0].set_ylabel(r"$\sigma$ multiplier")
    fig.colorbar(im, ax=axes, label="Std(adoption)", shrink=0.8)
    fig.suptitle("Variance landscape: critical ridge", fontsize=14, y=1.02)
    plt.tight_layout()
    out = FIGURES_DIR / "fig02_variance_landscape.png"
    fig.savefig(out)
    plt.close(fig)
    print(f"Saved: {out}")


# ── figure 3 — cross-sections at selected sigma ──────────────────────────

def plot_cross_sections(df: pd.DataFrame) -> None:
    if df.empty:
        print("WARNING: empty dataframe, skipping cross sections.")
        return

    slices = [0.2, 0.5, 1.0, 2.0, 5.0]
    sub = df[df["regime"] == "pln"]

    fig, ax = plt.subplots(figsize=(9, 5))
    cmap = plt.cm.plasma
    colors = [cmap(i / (len(slices) - 1)) for i in range(len(slices))]

    for sm, color in zip(slices, colors):
        s = sub[sub["sigma_mult"] == sm]
        if s.empty:
            continue
        agg = s.groupby("bdp")["adoption"].agg(["mean", "std"]).reset_index()
        ax.plot(agg["bdp"], agg["mean"], "o-", color=color, ms=4,
                label=rf"$\sigma\times${sm}")
        ax.fill_between(agg["bdp"],
                        agg["mean"] - agg["std"],
                        agg["mean"] + agg["std"],
                        alpha=0.15, color=color)

    ax.set_xlabel("BDP (PLN)")
    ax.set_ylabel("Adoption fraction")
    ax.set_title("Cross-sections at selected " + r"$\sigma$ multipliers (PLN)")
    ax.legend(fontsize=9)
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    plt.tight_layout()
    out = FIGURES_DIR / "fig03_cross_sections.png"
    fig.savefig(out)
    plt.close(fig)
    print(f"Saved: {out}")


# ── main ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Loading Campaign 1 data ...")
    data = load_c1_data()
    print(f"  rows: {len(data)}")

    plot_phase_heatmap(data)
    plot_variance_landscape(data)
    plot_cross_sections(data)
    print("Done (phase_diagram).")
