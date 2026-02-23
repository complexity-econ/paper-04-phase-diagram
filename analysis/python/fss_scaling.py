"""
Campaign 3 analysis -- finite-size scaling (FSS).

Produces:
    fig08_susceptibility.png     chi(BDP, N) = N * var(adoption)
    fig09_data_collapse.png      rescaled data collapse
    fig10_bdpc_convergence.png   BDP_c(N) convergence
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import differential_evolution

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import (
    RESULTS_DIR, FIGURES_DIR, BDP_LEVELS_FSS, FSS_SIZES, read_terminal,
)

# ── data loading ──────────────────────────────────────────────────────────

def load_c3_data() -> pd.DataFrame:
    """Read Campaign-3 terminal CSVs.

    Directory: c3_fss/n{N}/
    Filename:  c3_n{N}_bdp{bdp}_terminal.csv
    """
    rows = []
    base = RESULTS_DIR / "c3_fss"
    for N in FSS_SIZES:
        ndir = base / f"n{N}"
        for bdp in BDP_LEVELS_FSS:
            fname = f"c3_n{N}_bdp{bdp}_terminal.csv"
            fpath = ndir / fname
            if not fpath.exists():
                continue
            try:
                df = read_terminal(fpath)
            except Exception as exc:
                print(f"WARNING: cannot read {fpath}: {exc}")
                continue
            df = df.copy()
            df["bdp"] = bdp
            df["N"] = N
            df.rename(columns={"TotalAdoption": "adoption",
                                "Inflation": "inflation",
                                "Unemployment": "unemployment"},
                      inplace=True)
            rows.append(df)
    if not rows:
        print("WARNING: no C3 data found.")
        return pd.DataFrame()
    return pd.concat(rows, ignore_index=True)


def _compute_chi(df: pd.DataFrame):
    """Return DataFrame with columns: bdp, N, chi (= N * var(adoption)), var_adopt."""
    agg = df.groupby(["N", "bdp"])["adoption"].agg(["var", "mean", "std"]).reset_index()
    agg["chi"] = agg["N"] * agg["var"]
    return agg


# ── figure 8 — susceptibility ────────────────────────────────────────────

def plot_susceptibility(df: pd.DataFrame) -> None:
    if df.empty:
        print("WARNING: empty dataframe, skipping susceptibility.")
        return

    agg = _compute_chi(df)
    fig, ax = plt.subplots(figsize=(9, 5))
    cmap = plt.cm.viridis
    sizes = sorted(agg["N"].unique())
    colors = {N: cmap(i / max(1, len(sizes) - 1)) for i, N in enumerate(sizes)}

    for N in sizes:
        sub = agg[agg["N"] == N].sort_values("bdp")
        ax.plot(sub["bdp"], sub["chi"], "o-", ms=4,
                color=colors[N], label=f"N = {N:,}")

    ax.set_xlabel("BDP (PLN)")
    ax.set_ylabel(r"$\chi = N \cdot \mathrm{Var}(\mathrm{adoption})$")
    ax.set_title("Susceptibility: peaks grow with system size")
    ax.legend(fontsize=9)
    ax.set_xlim(left=min(BDP_LEVELS_FSS))
    plt.tight_layout()
    out = FIGURES_DIR / "fig08_susceptibility.png"
    fig.savefig(out)
    plt.close(fig)
    print(f"Saved: {out}")


# ── figure 9 — data collapse ─────────────────────────────────────────────

def _collapse_cost(params, agg, bdp_c_by_N):
    """Cost function: minimize spread of rescaled curves.

    params = [nu_inv, gamma_over_nu]
    Rescaled x = (BDP - BDP_c) * N^{1/nu}
    Rescaled y = chi / N^{gamma/nu}
    """
    nu_inv, g_over_nu = params
    xs, ys = [], []
    for N, grp in agg.groupby("N"):
        bc = bdp_c_by_N.get(N, np.nan)
        if np.isnan(bc):
            continue
        x_rescaled = (grp["bdp"].values - bc) * (N ** nu_inv)
        y_rescaled = grp["chi"].values / (N ** g_over_nu)
        xs.append(x_rescaled)
        ys.append(y_rescaled)
    if len(xs) < 2:
        return 1e12

    # Bin the rescaled x values and measure inter-curve spread
    all_x = np.concatenate(xs)
    all_y = np.concatenate(ys)
    labels = np.concatenate([np.full(len(x), i) for i, x in enumerate(xs)])

    # coarse binning
    n_bins = 20
    x_min, x_max = np.nanmin(all_x), np.nanmax(all_x)
    if x_max <= x_min:
        return 1e12
    edges = np.linspace(x_min, x_max, n_bins + 1)
    cost = 0.0
    count = 0
    for lo, hi in zip(edges[:-1], edges[1:]):
        mask = (all_x >= lo) & (all_x < hi)
        if mask.sum() < 2:
            continue
        bin_y = all_y[mask]
        bin_labels = labels[mask]
        # need points from at least 2 curves
        if len(set(bin_labels)) < 2:
            continue
        cost += np.var(bin_y)
        count += 1
    return cost / max(count, 1)


def plot_data_collapse(df: pd.DataFrame) -> None:
    if df.empty:
        print("WARNING: empty dataframe, skipping data collapse.")
        return

    agg = _compute_chi(df)

    # BDP_c per N
    bdp_c_by_N = {}
    for N in sorted(agg["N"].unique()):
        sub = agg[agg["N"] == N]
        if sub.empty or sub["chi"].isna().all():
            continue
        bdp_c_by_N[N] = sub.loc[sub["chi"].idxmax(), "bdp"]

    if len(bdp_c_by_N) < 2:
        print("WARNING: not enough sizes for data collapse.")
        return

    # Optimize nu_inv and gamma/nu with bounded global optimizer
    res = differential_evolution(
        _collapse_cost,
        bounds=[(0.01, 3.0), (0.01, 3.0)],
        args=(agg, bdp_c_by_N),
        maxiter=1000,
        seed=42,
    )
    nu_inv_opt, g_nu_opt = res.x
    print(f"  Data-collapse optimum: 1/nu = {nu_inv_opt:.3f}, "
          f"gamma/nu = {g_nu_opt:.3f}")

    fig, ax = plt.subplots(figsize=(9, 5))
    cmap = plt.cm.viridis
    sizes = sorted(agg["N"].unique())
    colors = {N: cmap(i / max(1, len(sizes) - 1)) for i, N in enumerate(sizes)}

    for N in sizes:
        sub = agg[agg["N"] == N].sort_values("bdp")
        bc = bdp_c_by_N.get(N, np.nan)
        if np.isnan(bc):
            continue
        x_r = (sub["bdp"].values - bc) * (N ** nu_inv_opt)
        y_r = sub["chi"].values / (N ** g_nu_opt)
        ax.plot(x_r, y_r, "o-", ms=4, color=colors[N],
                label=f"N = {N:,}")

    ax.set_xlabel(r"$(BDP - BDP_c)\; N^{1/\nu}$")
    ax.set_ylabel(r"$\chi / N^{\gamma/\nu}$")
    ax.set_title(
        f"Data collapse  "
        r"($1/\nu$" + f" = {nu_inv_opt:.2f}, "
        r"$\gamma/\nu$" + f" = {g_nu_opt:.2f})"
    )
    ax.legend(fontsize=9)
    plt.tight_layout()
    out = FIGURES_DIR / "fig09_data_collapse.png"
    fig.savefig(out)
    plt.close(fig)
    print(f"Saved: {out}")


# ── figure 10 — BDP_c convergence ────────────────────────────────────────

def plot_bdpc_convergence(df: pd.DataFrame) -> None:
    if df.empty:
        print("WARNING: empty dataframe, skipping BDP_c convergence.")
        return

    agg = _compute_chi(df)
    records = []
    for N in sorted(agg["N"].unique()):
        sub = agg[agg["N"] == N]
        if sub.empty or sub["chi"].isna().all():
            continue
        bdp_c = sub.loc[sub["chi"].idxmax(), "bdp"]
        records.append({"N": N, "bdp_c": bdp_c})

    if not records:
        print("WARNING: cannot compute BDP_c convergence.")
        return

    rdf = pd.DataFrame(records)

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(rdf["N"], rdf["bdp_c"], "s-", color="#1f77b4", ms=8, lw=2)
    ax.set_xscale("log")
    ax.set_xlabel("System size N")
    ax.set_ylabel(r"$BDP_c$ (PLN)")
    ax.set_title(r"Critical point convergence $BDP_c(N)$")
    # annotate points
    for _, row in rdf.iterrows():
        ax.annotate(f"{row['bdp_c']:.0f}",
                    (row["N"], row["bdp_c"]),
                    textcoords="offset points", xytext=(8, 5),
                    fontsize=9)
    plt.tight_layout()
    out = FIGURES_DIR / "fig10_bdpc_convergence.png"
    fig.savefig(out)
    plt.close(fig)
    print(f"Saved: {out}")


# ── main ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Loading Campaign 3 data ...")
    data = load_c3_data()
    print(f"  rows: {len(data)}")

    plot_susceptibility(data)
    plot_data_collapse(data)
    plot_bdpc_convergence(data)
    print("Done (fss_scaling).")
