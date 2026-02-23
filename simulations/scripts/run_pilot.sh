#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# Pilot run: all 4 campaigns with SEEDS=3 (instead of 30).
# Total: ~1,821 simulations for end-to-end pipeline validation.
#
# C1 Phase:    21 BDP x 10 sigma_mult x 2 regimes x 3 seeds = 1,260
# C2 Topology: 11 BDP x 4 topologies  x 2 regimes x 3 seeds =   264
# C3 FSS:      11 BDP x 4 sizes       x 3 seeds              =   132
# C4 Decision: 11 BDP x 5 variants    x 3 seeds              =   165
# Total:                                                        1,821
#
# FSS note: uses N=20000 instead of N=50000 (25x faster).
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CORE_DIR="$(cd "${SCRIPT_DIR}/../../../core" && pwd)"
RESULTS_DIR="$(cd "${SCRIPT_DIR}/../results" && pwd)"
JAR="${CORE_DIR}/target/scala-3.5.2/sfc-abm.jar"
SEEDS=3

if [[ ! -f "${JAR}" ]]; then
    echo "ERROR: JAR not found at ${JAR}"
    echo "Build it first: cd ${CORE_DIR} && sbt assembly"
    exit 1
fi

cd "${CORE_DIR}"

START_TIME=$(date +%s)

# =============================================================================
# Campaign 1: Phase Diagram — 21 BDP x 10 sigma_mult x 2 regimes x 3 seeds
# =============================================================================

BDP_LEVELS_21=(0 250 500 750 1000 1250 1500 1750 2000 2250 2500 2750 3000 3250 3500 3750 4000 4250 4500 4750 5000)
SIGMA_MULTS=(0.1 0.2 0.5 0.75 1.0 1.5 2.0 3.0 5.0 10.0)
REGIMES=(pln eur)

C1_TOTAL=$(( ${#BDP_LEVELS_21[@]} * ${#SIGMA_MULTS[@]} * ${#REGIMES[@]} * SEEDS ))
echo "============================================="
echo "  Campaign 1: Phase Diagram (pilot)"
echo "============================================="
echo "  ${C1_TOTAL} simulations (21 BDP x 10 sigma x 2 regimes x ${SEEDS} seeds)"
echo ""

C1_DONE=0
for regime in "${REGIMES[@]}"; do
    echo "--- Regime: ${regime} ---"
    for mult in "${SIGMA_MULTS[@]}"; do
        mult_safe="${mult//./_}"
        echo -n "  SIGMA_MULT=${mult}: "
        for bdp in "${BDP_LEVELS_21[@]}"; do
            prefix="c1_${regime}_sm${mult_safe}_bdp${bdp}"
            TOPOLOGY=ws SIGMA_MULT="${mult}" FIRMS_COUNT=10000 \
                java -jar "${JAR}" "${bdp}" "${SEEDS}" "${prefix}" "${regime}" > /dev/null 2>&1
            mv "mc/${prefix}_terminal.csv" "${RESULTS_DIR}/c1_phase/${regime}/"
            rm -f "mc/${prefix}_timeseries.csv"
            C1_DONE=$(( C1_DONE + 1 ))
        done
        echo "done (${C1_DONE}/${C1_TOTAL})"
    done
done

echo ""
echo "=== Campaign 1 complete ==="
echo "PLN: $(ls "${RESULTS_DIR}/c1_phase/pln/"*.csv 2>/dev/null | wc -l | tr -d ' ') files"
echo "EUR: $(ls "${RESULTS_DIR}/c1_phase/eur/"*.csv 2>/dev/null | wc -l | tr -d ' ') files"
echo ""

# =============================================================================
# Campaign 2: Topology Universality — 11 BDP x 4 topos x 2 regimes x 3 seeds
# =============================================================================

BDP_LEVELS_11=(0 500 1000 1500 2000 2500 3000 3500 4000 4500 5000)
TOPOLOGIES=(ws er ba lattice)

C2_TOTAL=$(( ${#BDP_LEVELS_11[@]} * ${#TOPOLOGIES[@]} * ${#REGIMES[@]} * SEEDS ))
echo "============================================="
echo "  Campaign 2: Topology Universality (pilot)"
echo "============================================="
echo "  ${C2_TOTAL} simulations (11 BDP x 4 topos x 2 regimes x ${SEEDS} seeds)"
echo ""

C2_DONE=0
for topo in "${TOPOLOGIES[@]}"; do
    for regime in "${REGIMES[@]}"; do
        echo -n "--- ${topo}/${regime}: "
        for bdp in "${BDP_LEVELS_11[@]}"; do
            prefix="c2_${topo}_${regime}_bdp${bdp}"
            TOPOLOGY="${topo}" SIGMA_MULT=1.0 FIRMS_COUNT=10000 \
                java -jar "${JAR}" "${bdp}" "${SEEDS}" "${prefix}" "${regime}" > /dev/null 2>&1
            mv "mc/${prefix}_terminal.csv" "${RESULTS_DIR}/c2_topology/${topo}/${regime}/"
            rm -f "mc/${prefix}_timeseries.csv"
            C2_DONE=$(( C2_DONE + 1 ))
        done
        echo "done (${C2_DONE}/${C2_TOTAL})"
    done
done

echo ""
echo "=== Campaign 2 complete ==="
for topo in "${TOPOLOGIES[@]}"; do
    for regime in "${REGIMES[@]}"; do
        count=$(ls "${RESULTS_DIR}/c2_topology/${topo}/${regime}/"*.csv 2>/dev/null | wc -l | tr -d ' ')
        echo "  ${topo}/${regime}: ${count} files"
    done
done
echo ""

# =============================================================================
# Campaign 3: Finite-Size Scaling — 11 BDP x 4 sizes x 3 seeds
# NOTE: N=20000 replaces N=50000 for pilot speed.
# =============================================================================

BDP_LEVELS_FSS=(500 800 1100 1400 1700 2000 2300 2600 2900 3200 3500)
FIRM_SIZES=(1000 5000 10000 20000)

C3_TOTAL=$(( ${#BDP_LEVELS_FSS[@]} * ${#FIRM_SIZES[@]} * SEEDS ))
echo "============================================="
echo "  Campaign 3: Finite-Size Scaling (pilot)"
echo "============================================="
echo "  ${C3_TOTAL} simulations (11 BDP x 4 sizes x ${SEEDS} seeds)"
echo "  Sizes: ${FIRM_SIZES[*]} (N=20000 replaces N=50000)"
echo ""

C3_DONE=0
for N in "${FIRM_SIZES[@]}"; do
    echo -n "--- N=${N}: "
    for bdp in "${BDP_LEVELS_FSS[@]}"; do
        prefix="c3_n${N}_bdp${bdp}"
        TOPOLOGY=ws SIGMA_MULT=1.0 FIRMS_COUNT="${N}" \
            java -jar "${JAR}" "${bdp}" "${SEEDS}" "${prefix}" pln > /dev/null 2>&1
        mv "mc/${prefix}_terminal.csv" "${RESULTS_DIR}/c3_fss/n${N}/"
        rm -f "mc/${prefix}_timeseries.csv"
        C3_DONE=$(( C3_DONE + 1 ))
    done
    echo "done (${C3_DONE}/${C3_TOTAL})"
done

echo ""
echo "=== Campaign 3 complete ==="
for N in "${FIRM_SIZES[@]}"; do
    count=$(ls "${RESULTS_DIR}/c3_fss/n${N}/"*.csv 2>/dev/null | wc -l | tr -d ' ')
    echo "  n${N}: ${count} files"
done
echo ""

# =============================================================================
# Campaign 4: Decision Rule Sensitivity — 11 BDP x 5 variants x 3 seeds
# =============================================================================

declare -A VARIANTS
VARIANTS=(
    [baseline]=0.40
    [high_demo]=0.25
    [low_demo]=0.60
    [narrow_risk]=0.40
    [cautious]=0.40
)
VARIANT_ORDER=(baseline high_demo low_demo narrow_risk cautious)

C4_TOTAL=$(( ${#BDP_LEVELS_11[@]} * ${#VARIANT_ORDER[@]} * SEEDS ))
echo "============================================="
echo "  Campaign 4: Decision Rule Sensitivity (pilot)"
echo "============================================="
echo "  ${C4_TOTAL} simulations (11 BDP x 5 variants x ${SEEDS} seeds)"
echo ""

C4_DONE=0
for variant in "${VARIANT_ORDER[@]}"; do
    demo_thresh="${VARIANTS[${variant}]}"
    echo -n "--- ${variant} (DEMO_THRESH=${demo_thresh}): "
    for bdp in "${BDP_LEVELS_11[@]}"; do
        prefix="c4_${variant}_bdp${bdp}"
        TOPOLOGY=ws SIGMA_MULT=1.0 FIRMS_COUNT=10000 DEMO_THRESH="${demo_thresh}" \
            java -jar "${JAR}" "${bdp}" "${SEEDS}" "${prefix}" pln > /dev/null 2>&1
        mv "mc/${prefix}_terminal.csv" "${RESULTS_DIR}/c4_decision/${variant}/"
        rm -f "mc/${prefix}_timeseries.csv"
        C4_DONE=$(( C4_DONE + 1 ))
    done
    echo "done (${C4_DONE}/${C4_TOTAL})"
done

echo ""
echo "=== Campaign 4 complete ==="
for variant in "${VARIANT_ORDER[@]}"; do
    count=$(ls "${RESULTS_DIR}/c4_decision/${variant}/"*.csv 2>/dev/null | wc -l | tr -d ' ')
    echo "  ${variant}: ${count} files"
done
echo ""

# =============================================================================
# Summary
# =============================================================================

END_TIME=$(date +%s)
ELAPSED=$(( END_TIME - START_TIME ))
MINUTES=$(( ELAPSED / 60 ))
SECONDS=$(( ELAPSED % 60 ))

GRAND_TOTAL=$(( C1_TOTAL + C2_TOTAL + C3_TOTAL + C4_TOTAL ))
echo "============================================="
echo "  PILOT COMPLETE"
echo "============================================="
echo "  Total simulations: ${GRAND_TOTAL}"
echo "  Elapsed time:      ${MINUTES}m ${SECONDS}s"
echo ""
echo "  Next: run analysis scripts in analysis/python/"
echo "============================================="
