"""
Campaign 4 analysis -- decision-rule sensitivity.

Produces:
    fig11_decision_sensitivity.png  adoption vs BDP for 5 decision variants
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import (
    RESULTS_DIR, FIGURES_DIR, BDP_LEVELS_11,
    DECISION_VARIANTS, DECISION_COLORS, DECISION_LABELS,
    read_terminal,
)

# ── data loading ──────────────────────────────────────────────────────────

def load_c4_data() -> pd.DataFrame:
    """Read Campaign-4 terminal CSVs.

    Directory: c4_decision/{variant}/
    Filename:  c4_{variant}_bdp{bdp}_terminal.csv
    """
    rows = []
    base = RESULTS_DIR / "c4_decision"
    for variant in DECISION_VARIANTS:
        vdir = base / variant
        for bdp in BDP_LEVELS_11:
            fname = f"c4_{variant}_bdp{bdp}_terminal.csv"
            fpath = vdir / fname
            if not fpath.exists():
                continue
            try:
                df = read_terminal(fpath)
            except Exception as exc:
                print(f"WARNING: cannot read {fpath}: {exc}")
                continue
            df = df.copy()
            df["bdp"] = bdp
            df["variant"] = variant
            df.rename(columns={"TotalAdoption": "adoption",
                                "Inflation": "inflation",
                                "Unemployment": "unemployment"},
                      inplace=True)
            rows.append(df)
    if not rows:
        print("WARNING: no C4 data found.")
        return pd.DataFrame()
    return pd.concat(rows, ignore_index=True)


# ── figure 11 — decision sensitivity ─────────────────────────────────────

def plot_decision_sensitivity(df: pd.DataFrame) -> None:
    if df.empty:
        print("WARNING: empty dataframe, skipping decision sensitivity.")
        return

    fig, ax = plt.subplots(figsize=(9, 5))

    for variant in DECISION_VARIANTS:
        sub = df[df["variant"] == variant]
        if sub.empty:
            continue
        agg = sub.groupby("bdp")["adoption"].agg(["mean", "std"]).reset_index()
        color = DECISION_COLORS[variant]
        label = DECISION_LABELS[variant]
        ax.plot(agg["bdp"], agg["mean"], "o-", ms=4,
                color=color, label=label)
        ax.fill_between(agg["bdp"],
                        agg["mean"] - agg["std"],
                        agg["mean"] + agg["std"],
                        alpha=0.12, color=color)

    ax.set_xlabel("BDP (PLN)")
    ax.set_ylabel("Adoption fraction")
    ax.set_title("Decision-rule sensitivity: critical point survives perturbations")
    ax.legend(fontsize=9)
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    plt.tight_layout()
    out = FIGURES_DIR / "fig11_decision_sensitivity.png"
    fig.savefig(out)
    plt.close(fig)
    print(f"Saved: {out}")


# ── main ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Loading Campaign 4 data ...")
    data = load_c4_data()
    print(f"  rows: {len(data)}")

    plot_decision_sensitivity(data)
    print("Done (decision_sensitivity).")
