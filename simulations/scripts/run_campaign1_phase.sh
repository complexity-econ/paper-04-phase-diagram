#!/usr/bin/env bash
set -euo pipefail

# Campaign 1: Phase Diagram — 21 BDP x 10 SIGMA_MULT x 2 regimes x 30 seeds = 12,600 simulations
# Sweeps the (BDP, sigma) plane under both monetary regimes.
# Fixed: WS topology, N=10,000 firms.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CORE_DIR="$(cd "${SCRIPT_DIR}/../../../core" && pwd)"
RESULTS_DIR="$(cd "${SCRIPT_DIR}/../results" && pwd)"
JAR="${CORE_DIR}/target/scala-3.5.2/sfc-abm.jar"
SEEDS=30

BDP_LEVELS=(0 250 500 750 1000 1250 1500 1750 2000 2250 2500 2750 3000 3250 3500 3750 4000 4250 4500 4750 5000)
SIGMA_MULTS=(0.1 0.2 0.5 0.75 1.0 1.5 2.0 3.0 5.0 10.0)
REGIMES=(pln eur)

TOTAL=$(( ${#BDP_LEVELS[@]} * ${#SIGMA_MULTS[@]} * ${#REGIMES[@]} * SEEDS ))

echo "============================================="
echo "  Campaign 1: Phase Diagram"
echo "============================================="
echo "Core:       ${CORE_DIR}"
echo "JAR:        ${JAR}"
echo "Output:     ${RESULTS_DIR}/c1_phase/"
echo "Seeds:      ${SEEDS}"
echo "BDP levels: ${#BDP_LEVELS[@]}"
echo "Sigma mults: ${#SIGMA_MULTS[@]}"
echo "Regimes:    ${#REGIMES[@]} (pln, eur)"
echo "Topology:   WS (default), N=10000"
echo "Total runs: $(( ${#BDP_LEVELS[@]} * ${#SIGMA_MULTS[@]} * ${#REGIMES[@]} )) points x ${SEEDS} seeds = ${TOTAL} simulations"
echo ""

if [[ ! -f "${JAR}" ]]; then
    echo "ERROR: JAR not found at ${JAR}"
    echo "Build it first: cd ${CORE_DIR} && sbt assembly"
    exit 1
fi

cd "${CORE_DIR}"

for regime in "${REGIMES[@]}"; do
    echo "--- Regime: ${regime} ---"
    for mult in "${SIGMA_MULTS[@]}"; do
        # Replace dots with underscores for filename safety
        mult_safe="${mult//./_}"
        echo "  SIGMA_MULT=${mult}"
        for bdp in "${BDP_LEVELS[@]}"; do
            prefix="c1_${regime}_sm${mult_safe}_bdp${bdp}"
            echo -n "    BDP=${bdp} ... "
            TOPOLOGY=ws SIGMA_MULT="${mult}" FIRMS_COUNT=10000 \
                java -jar "${JAR}" "${bdp}" "${SEEDS}" "${prefix}" "${regime}" > /dev/null 2>&1
            mv "mc/${prefix}_terminal.csv" "${RESULTS_DIR}/c1_phase/${regime}/"
            rm -f "mc/${prefix}_timeseries.csv"
            echo "done"
        done
    done
done

echo ""
echo "=== Campaign 1 complete ==="
echo "PLN results: ${RESULTS_DIR}/c1_phase/pln/ ($(ls "${RESULTS_DIR}/c1_phase/pln/"*.csv 2>/dev/null | wc -l) files)"
echo "EUR results: ${RESULTS_DIR}/c1_phase/eur/ ($(ls "${RESULTS_DIR}/c1_phase/eur/"*.csv 2>/dev/null | wc -l) files)"
