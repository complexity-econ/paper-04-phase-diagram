#!/usr/bin/env bash
set -euo pipefail

# Campaign 3: Finite-Size Scaling — 11 BDP x 4 sizes x 30 seeds = 1,320 simulations
# Extracts critical exponents via data collapse at varying system sizes.
# Fixed: WS topology, PLN regime, SIGMA_MULT=1.0.
#
# NOTE: N=50000 is ~25x slower than N=1000. Budget wall-clock time accordingly.
#       Consider running N=50000 on a separate machine or overnight.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CORE_DIR="$(cd "${SCRIPT_DIR}/../../../core" && pwd)"
RESULTS_DIR="$(cd "${SCRIPT_DIR}/../results" && pwd)"
JAR="${CORE_DIR}/target/scala-3.5.2/sfc-abm.jar"
SEEDS=30

BDP_LEVELS=(500 800 1100 1400 1700 2000 2300 2600 2900 3200 3500)
FIRM_SIZES=(1000 5000 10000 50000)

TOTAL=$(( ${#BDP_LEVELS[@]} * ${#FIRM_SIZES[@]} * SEEDS ))

echo "============================================="
echo "  Campaign 3: Finite-Size Scaling"
echo "============================================="
echo "Core:       ${CORE_DIR}"
echo "JAR:        ${JAR}"
echo "Output:     ${RESULTS_DIR}/c3_fss/"
echo "Seeds:      ${SEEDS}"
echo "BDP levels: ${#BDP_LEVELS[@]}"
echo "Firm sizes: ${FIRM_SIZES[*]}"
echo "Fixed:      WS topology, PLN regime, SIGMA_MULT=1.0"
echo "Total runs: $(( ${#BDP_LEVELS[@]} * ${#FIRM_SIZES[@]} )) points x ${SEEDS} seeds = ${TOTAL} simulations"
echo ""
echo "WARNING: N=50000 is ~25x slower than N=1000. Plan accordingly."
echo ""

if [[ ! -f "${JAR}" ]]; then
    echo "ERROR: JAR not found at ${JAR}"
    echo "Build it first: cd ${CORE_DIR} && sbt assembly"
    exit 1
fi

cd "${CORE_DIR}"

for N in "${FIRM_SIZES[@]}"; do
    echo "--- Firm count: N=${N} ---"
    for bdp in "${BDP_LEVELS[@]}"; do
        prefix="c3_n${N}_bdp${bdp}"
        echo -n "  BDP=${bdp} ... "
        TOPOLOGY=ws SIGMA_MULT=1.0 FIRMS_COUNT="${N}" \
            java -jar "${JAR}" "${bdp}" "${SEEDS}" "${prefix}" pln > /dev/null 2>&1
        mv "mc/${prefix}_terminal.csv" "${RESULTS_DIR}/c3_fss/n${N}/"
        rm -f "mc/${prefix}_timeseries.csv"
        echo "done"
    done
done

echo ""
echo "=== Campaign 3 complete ==="
for N in "${FIRM_SIZES[@]}"; do
    count=$(ls "${RESULTS_DIR}/c3_fss/n${N}/"*.csv 2>/dev/null | wc -l)
    echo "n${N}: ${count} files"
done
