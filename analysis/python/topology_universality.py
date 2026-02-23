"""
Campaign 2 analysis -- topology universality.

Produces:
    fig04_topology_bifurcation.png  adoption vs BDP by topology (PLN / EUR)
    fig05_critical_points.png       BDP_c bar chart per topology x regime
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import (
    RESULTS_DIR, FIGURES_DIR, REGIME_COLORS, REGIME_LABELS,
    TOPO_COLORS, TOPO_LABELS, TOPOLOGIES,
    BDP_LEVELS_11, read_terminal,
)

# ── data loading ──────────────────────────────────────────────────────────

def load_c2_data() -> pd.DataFrame:
    """Read all Campaign-2 terminal CSVs.

    Directory layout: c2_topology/{topo}/{regime}/
    Filename: c2_{topo}_{regime}_bdp{bdp}_terminal.csv
    """
    rows = []
    base = RESULTS_DIR / "c2_topology"
    for topo in TOPOLOGIES:
        for regime in ("pln", "eur"):
            rdir = base / topo / regime
            for bdp in BDP_LEVELS_11:
                fname = f"c2_{topo}_{regime}_bdp{bdp}_terminal.csv"
                fpath = rdir / fname
                if not fpath.exists():
                    continue
                try:
                    df = read_terminal(fpath)
                except Exception as exc:
                    print(f"WARNING: cannot read {fpath}: {exc}")
                    continue
                df = df.copy()
                df["bdp"] = bdp
                df["topology"] = topo
                df["regime"] = regime
                df.rename(columns={"TotalAdoption": "adoption",
                                   "Inflation": "inflation",
                                   "Unemployment": "unemployment"},
                          inplace=True)
                rows.append(df)
    if not rows:
        print("WARNING: no C2 data found.")
        return pd.DataFrame()
    return pd.concat(rows, ignore_index=True)


# ── figure 4 — bifurcation overlay ───────────────────────────────────────

def plot_bifurcation_overlay(df: pd.DataFrame) -> None:
    if df.empty:
        print("WARNING: empty dataframe, skipping bifurcation overlay.")
        return

    fig, axes = plt.subplots(1, 2, figsize=(14, 5), sharey=True)

    for ax, regime in zip(axes, ("pln", "eur")):
        sub = df[df["regime"] == regime]
        for topo in TOPOLOGIES:
            ts = sub[sub["topology"] == topo]
            if ts.empty:
                continue
            agg = ts.groupby("bdp")["adoption"].agg(["mean", "std"]).reset_index()
            ax.plot(agg["bdp"], agg["mean"], "o-",
                    color=TOPO_COLORS[topo], ms=4,
                    label=TOPO_LABELS[topo])
            ax.fill_between(agg["bdp"],
                            agg["mean"] - agg["std"],
                            agg["mean"] + agg["std"],
                            alpha=0.12, color=TOPO_COLORS[topo])

        ax.set_xlabel("BDP (PLN)")
        ax.set_title(f"{REGIME_LABELS[regime]} regime")
        ax.legend(fontsize=9)
        ax.set_xlim(left=0)
        ax.set_ylim(bottom=0)

    axes[0].set_ylabel("Adoption fraction")
    fig.suptitle("Bifurcation diagram by network topology", fontsize=14, y=1.02)
    plt.tight_layout()
    out = FIGURES_DIR / "fig04_topology_bifurcation.png"
    fig.savefig(out)
    plt.close(fig)
    print(f"Saved: {out}")


# ── figure 5 — critical-point comparison ──────────────────────────────────

def plot_critical_comparison(df: pd.DataFrame) -> None:
    if df.empty:
        print("WARNING: empty dataframe, skipping critical comparison.")
        return

    records = []
    for regime in ("pln", "eur"):
        for topo in TOPOLOGIES:
            sub = df[(df["regime"] == regime) & (df["topology"] == topo)]
            if sub.empty:
                continue
            agg = sub.groupby("bdp")["adoption"].std().reset_index()
            agg.columns = ["bdp", "std_adopt"]
            if agg.empty or agg["std_adopt"].isna().all():
                continue
            bdp_c = agg.loc[agg["std_adopt"].idxmax(), "bdp"]
            records.append({"regime": regime, "topology": topo, "bdp_c": bdp_c})

    if not records:
        print("WARNING: cannot compute critical points.")
        return

    rdf = pd.DataFrame(records)

    fig, ax = plt.subplots(figsize=(8, 5))
    x = np.arange(len(TOPOLOGIES))
    width = 0.35
    for i, regime in enumerate(("pln", "eur")):
        vals = []
        for topo in TOPOLOGIES:
            row = rdf[(rdf["regime"] == regime) & (rdf["topology"] == topo)]
            vals.append(row["bdp_c"].values[0] if len(row) else 0)
        ax.bar(x + i * width, vals, width,
               label=REGIME_LABELS[regime],
               color=REGIME_COLORS[regime], alpha=0.85)

    ax.set_xticks(x + width / 2)
    ax.set_xticklabels([TOPO_LABELS[t] for t in TOPOLOGIES], fontsize=10)
    ax.set_ylabel(r"$BDP_c$ (PLN)")
    ax.set_title("Critical BDP by topology and regime")
    ax.legend()
    plt.tight_layout()
    out = FIGURES_DIR / "fig05_critical_points.png"
    fig.savefig(out)
    plt.close(fig)
    print(f"Saved: {out}")


# ── main ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Loading Campaign 2 data ...")
    data = load_c2_data()
    print(f"  rows: {len(data)}")

    plot_bifurcation_overlay(data)
    plot_critical_comparison(data)
    print("Done (topology_universality).")
