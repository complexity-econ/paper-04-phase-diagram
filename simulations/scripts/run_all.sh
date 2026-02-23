#!/usr/bin/env bash
set -euo pipefail

# Paper-04: Phase Diagram & Universality — Master Orchestrator
# Runs all 4 campaigns sequentially.
#
# Total simulation budget:
#   Campaign 1 (Phase Diagram):        21 BDP x 10 sigma x 2 regimes x 30 seeds = 12,600
#   Campaign 2 (Topology):             11 BDP x 4 topos  x 2 regimes x 30 seeds =  2,640
#   Campaign 3 (Finite-Size Scaling):  11 BDP x 4 sizes              x 30 seeds =  1,320
#   Campaign 4 (Decision Sensitivity): 11 BDP x 5 variants           x 30 seeds =  1,650
#   -----------------------------------------------------------------------
#   Grand total:                                                               18,210

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "============================================================"
echo "  Paper-04: Phase Diagram & Universality — Full Sweep"
echo "============================================================"
echo ""
echo "  Campaign 1 — Phase Diagram:          12,600 simulations"
echo "  Campaign 2 — Topology Universality:   2,640 simulations"
echo "  Campaign 3 — Finite-Size Scaling:     1,320 simulations"
echo "  Campaign 4 — Decision Sensitivity:    1,650 simulations"
echo "  ---------------------------------------------------------"
echo "  Grand total:                         18,210 simulations"
echo ""
echo "Start time: $(date)"
echo ""

# --- Campaign 1 ---
echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
echo "  Starting Campaign 1: Phase Diagram"
echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
bash "${SCRIPT_DIR}/run_campaign1_phase.sh"
echo ""

# --- Campaign 2 ---
echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
echo "  Starting Campaign 2: Topology Universality"
echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
bash "${SCRIPT_DIR}/run_campaign2_topology.sh"
echo ""

# --- Campaign 3 ---
echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
echo "  Starting Campaign 3: Finite-Size Scaling"
echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
bash "${SCRIPT_DIR}/run_campaign3_fss.sh"
echo ""

# --- Campaign 4 ---
echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
echo "  Starting Campaign 4: Decision Rule Sensitivity"
echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
bash "${SCRIPT_DIR}/run_campaign4_decision.sh"
echo ""

echo "============================================================"
echo "  All campaigns complete!"
echo "  End time: $(date)"
echo "============================================================"
