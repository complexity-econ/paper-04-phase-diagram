#!/usr/bin/env bash
set -euo pipefail

# Campaign 2: Topology Universality — 11 BDP x 4 topologies x 2 regimes x 30 seeds = 2,640 simulations
# Tests whether critical behaviour is universal across network structures.
# Fixed: N=10,000, SIGMA_MULT=1.0.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CORE_DIR="$(cd "${SCRIPT_DIR}/../../../core" && pwd)"
RESULTS_DIR="$(cd "${SCRIPT_DIR}/../results" && pwd)"
JAR="${CORE_DIR}/target/scala-3.5.2/sfc-abm.jar"
SEEDS=30

BDP_LEVELS=(0 500 1000 1500 2000 2500 3000 3500 4000 4500 5000)
TOPOLOGIES=(ws er ba lattice)
REGIMES=(pln eur)

TOTAL=$(( ${#BDP_LEVELS[@]} * ${#TOPOLOGIES[@]} * ${#REGIMES[@]} * SEEDS ))

echo "============================================="
echo "  Campaign 2: Topology Universality"
echo "============================================="
echo "Core:       ${CORE_DIR}"
echo "JAR:        ${JAR}"
echo "Output:     ${RESULTS_DIR}/c2_topology/"
echo "Seeds:      ${SEEDS}"
echo "BDP levels: ${#BDP_LEVELS[@]}"
echo "Topologies: ${#TOPOLOGIES[@]} (ws, er, ba, lattice)"
echo "Regimes:    ${#REGIMES[@]} (pln, eur)"
echo "Fixed:      N=10000, SIGMA_MULT=1.0"
echo "Total runs: $(( ${#BDP_LEVELS[@]} * ${#TOPOLOGIES[@]} * ${#REGIMES[@]} )) points x ${SEEDS} seeds = ${TOTAL} simulations"
echo ""

if [[ ! -f "${JAR}" ]]; then
    echo "ERROR: JAR not found at ${JAR}"
    echo "Build it first: cd ${CORE_DIR} && sbt assembly"
    exit 1
fi

cd "${CORE_DIR}"

for topo in "${TOPOLOGIES[@]}"; do
    for regime in "${REGIMES[@]}"; do
        echo "--- Topology: ${topo}, Regime: ${regime} ---"
        for bdp in "${BDP_LEVELS[@]}"; do
            prefix="c2_${topo}_${regime}_bdp${bdp}"
            echo -n "  BDP=${bdp} ... "
            TOPOLOGY="${topo}" SIGMA_MULT=1.0 FIRMS_COUNT=10000 \
                java -jar "${JAR}" "${bdp}" "${SEEDS}" "${prefix}" "${regime}" > /dev/null 2>&1
            mv "mc/${prefix}_terminal.csv" "${RESULTS_DIR}/c2_topology/${topo}/${regime}/"
            rm -f "mc/${prefix}_timeseries.csv"
            echo "done"
        done
    done
done

echo ""
echo "=== Campaign 2 complete ==="
for topo in "${TOPOLOGIES[@]}"; do
    for regime in "${REGIMES[@]}"; do
        count=$(ls "${RESULTS_DIR}/c2_topology/${topo}/${regime}/"*.csv 2>/dev/null | wc -l)
        echo "${topo}/${regime}: ${count} files"
    done
done
