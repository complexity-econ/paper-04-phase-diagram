#!/usr/bin/env bash
set -euo pipefail

# Campaign 4: Decision Rule Sensitivity — 11 BDP x 5 variants x 30 seeds = 1,650 simulations
# Checks robustness of phase boundaries to adoption decision thresholds.
# Fixed: WS topology, PLN regime, N=10,000, SIGMA_MULT=1.0.
#
# Variants:
#   baseline    — DEMO_THRESH=0.40 (default model)
#   high_demo   — DEMO_THRESH=0.25 (firms adopt more readily on peer evidence)
#   low_demo    — DEMO_THRESH=0.60 (firms require stronger peer evidence)
#   narrow_risk — DEMO_THRESH=0.40 (placeholder: needs code-level risk band tweak)
#   cautious    — DEMO_THRESH=0.40 (placeholder: needs code-level payback period tweak)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CORE_DIR="$(cd "${SCRIPT_DIR}/../../../core" && pwd)"
RESULTS_DIR="$(cd "${SCRIPT_DIR}/../results" && pwd)"
JAR="${CORE_DIR}/target/scala-3.5.2/sfc-abm.jar"
SEEDS=30

BDP_LEVELS=(0 500 1000 1500 2000 2500 3000 3500 4000 4500 5000)

# variant_name:demo_thresh pairs
declare -A VARIANTS
VARIANTS=(
    [baseline]=0.40
    [high_demo]=0.25
    [low_demo]=0.60
    [narrow_risk]=0.40
    [cautious]=0.40
)
# Ordered list for deterministic iteration
VARIANT_ORDER=(baseline high_demo low_demo narrow_risk cautious)

TOTAL=$(( ${#BDP_LEVELS[@]} * ${#VARIANT_ORDER[@]} * SEEDS ))

echo "============================================="
echo "  Campaign 4: Decision Rule Sensitivity"
echo "============================================="
echo "Core:       ${CORE_DIR}"
echo "JAR:        ${JAR}"
echo "Output:     ${RESULTS_DIR}/c4_decision/"
echo "Seeds:      ${SEEDS}"
echo "BDP levels: ${#BDP_LEVELS[@]}"
echo "Variants:   ${#VARIANT_ORDER[@]} (baseline, high_demo, low_demo, narrow_risk, cautious)"
echo "Fixed:      WS topology, PLN regime, N=10000, SIGMA_MULT=1.0"
echo "Total runs: $(( ${#BDP_LEVELS[@]} * ${#VARIANT_ORDER[@]} )) points x ${SEEDS} seeds = ${TOTAL} simulations"
echo ""
echo "NOTE: narrow_risk and cautious currently use the same DEMO_THRESH as baseline."
echo "      They will produce distinct results once corresponding code-level tweaks are made."
echo ""

if [[ ! -f "${JAR}" ]]; then
    echo "ERROR: JAR not found at ${JAR}"
    echo "Build it first: cd ${CORE_DIR} && sbt assembly"
    exit 1
fi

cd "${CORE_DIR}"

for variant in "${VARIANT_ORDER[@]}"; do
    demo_thresh="${VARIANTS[${variant}]}"
    echo "--- Variant: ${variant} (DEMO_THRESH=${demo_thresh}) ---"
    for bdp in "${BDP_LEVELS[@]}"; do
        prefix="c4_${variant}_bdp${bdp}"
        echo -n "  BDP=${bdp} ... "
        TOPOLOGY=ws SIGMA_MULT=1.0 FIRMS_COUNT=10000 DEMO_THRESH="${demo_thresh}" \
            java -jar "${JAR}" "${bdp}" "${SEEDS}" "${prefix}" pln > /dev/null 2>&1
        mv "mc/${prefix}_terminal.csv" "${RESULTS_DIR}/c4_decision/${variant}/"
        rm -f "mc/${prefix}_timeseries.csv"
        echo "done"
    done
done

echo ""
echo "=== Campaign 4 complete ==="
for variant in "${VARIANT_ORDER[@]}"; do
    count=$(ls "${RESULTS_DIR}/c4_decision/${variant}/"*.csv 2>/dev/null | wc -l)
    echo "${variant}: ${count} files"
done
