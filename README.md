# Phase Diagram & Universality

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18751083.svg)](https://doi.org/10.5281/zenodo.18751083)

Phase transition universality analysis for the SFC-ABM model of AI-driven labor market automation.

## Campaigns

| # | Campaign | Axes | Runs |
|---|----------|------|------|
| 1 | Phase Diagram | BDP(21) × σ_mult(10) × regime(2) × 30 seeds | 12,600 |
| 2 | Topology Universality | BDP(11) × topology(4) × regime(2) × 30 seeds | 2,640 |
| 3 | Finite-Size Scaling | BDP(11) × N(5) × 30 seeds | 1,650 |
| 4 | Decision Rule Sensitivity | BDP(11) × variant(5) × 30 seeds | 1,650 |
| | **Total** | | **18,540** |

## Prerequisites

Build the fat JAR first:

```bash
cd ../core && sbt assembly
```

## Usage

```bash
# Run everything
make all

# Individual campaigns
bash simulations/scripts/run_campaign1_phase.sh
bash simulations/scripts/run_campaign2_topology.sh
bash simulations/scripts/run_campaign3_fss.sh
bash simulations/scripts/run_campaign4_decision.sh

# Generate figures
make figures

# Compile paper
make paper
```

## Figures

| Fig | Description | Script |
|-----|-------------|--------|
| 01 | Phase diagram (BDP × σ_mult heatmap) | phase_diagram.py |
| 02 | Variance landscape (critical ridge) | phase_diagram.py |
| 03 | Cross-section slices | phase_diagram.py |
| 04 | Topology bifurcation overlay | topology_universality.py |
| 05 | Critical point comparison | topology_universality.py |
| 06 | Log-log critical exponents | critical_exponents.py |
| 07 | Exponent forest plot | critical_exponents.py |
| 08 | Susceptibility curves | fss_scaling.py |
| 09 | Data collapse | fss_scaling.py |
| 10 | BDP_c convergence | fss_scaling.py |
| 11 | Decision rule sensitivity | decision_sensitivity.py |
