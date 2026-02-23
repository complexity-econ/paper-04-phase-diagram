"""
Shared configuration for paper-04-phase-diagram analysis scripts.
"""

from pathlib import Path
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[2]          # paper-04 root
RESULTS_DIR = BASE_DIR / "simulations" / "results"
FIGURES_DIR = BASE_DIR / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Matplotlib defaults
# ---------------------------------------------------------------------------
mpl.rcParams.update({
    "figure.dpi": 200,
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.labelsize": 12,
    "savefig.dpi": 200,
    "savefig.bbox": "tight",
})

# ---------------------------------------------------------------------------
# Color palettes
# ---------------------------------------------------------------------------
REGIME_COLORS = {"pln": "#1f77b4", "eur": "#d62728"}   # blue / red
REGIME_LABELS = {"pln": "PLN", "eur": "EUR"}

TOPO_COLORS = {
    "ws":      "#1f77b4",   # blue
    "er":      "#ff7f0e",   # orange
    "ba":      "#2ca02c",   # green
    "lattice": "#9467bd",   # purple
}
TOPO_LABELS = {
    "ws":      "Watts-Strogatz",
    "er":      "Erdos-Renyi",
    "ba":      "Barabasi-Albert",
    "lattice": "Ring Lattice",
}

DECISION_COLORS = {
    "baseline":    "#1f77b4",
    "high_demo":   "#ff7f0e",
    "low_demo":    "#2ca02c",
    "narrow_risk": "#d62728",
    "cautious":    "#9467bd",
}
DECISION_LABELS = {
    "baseline":    "Baseline",
    "high_demo":   "High demonstration",
    "low_demo":    "Low demonstration",
    "narrow_risk": "Narrow risk",
    "cautious":    "Cautious",
}

# ---------------------------------------------------------------------------
# Sweep grids
# ---------------------------------------------------------------------------
BDP_LEVELS_21 = list(range(0, 5001, 250))               # 21 levels
BDP_LEVELS_11 = list(range(0, 5001, 500))               # 11 levels
BDP_LEVELS_FSS = list(range(500, 3501, 300))             # FSS sweep
SIGMA_MULTS = [0.1, 0.2, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 5.0, 10.0]
TOPOLOGIES = ["ws", "er", "ba", "lattice"]
FSS_SIZES = [1000, 5000, 10000, 20000, 50000]
DECISION_VARIANTS = ["baseline", "high_demo", "low_demo",
                     "narrow_risk", "cautious"]

# ---------------------------------------------------------------------------
# CSV helper
# ---------------------------------------------------------------------------

def read_terminal(path: Path) -> pd.DataFrame:
    """Read a terminal-state CSV (semicolon-separated, comma decimals)."""
    return pd.read_csv(path, sep=";", decimal=",")
