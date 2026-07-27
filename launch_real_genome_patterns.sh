#!/bin/bash
set -e

REPO_DIR=~/bronko_benchmark/bronko-test
BENCH_DIR=~/bronko_benchmark/phastsim-run-round2
LOG_DIR=$BENCH_DIR/real_genome_pattern_logs
mkdir -p "$LOG_DIR"

declare -A PATTERNS
PATTERNS[default]=""
PATTERNS[ska_pattern]="__________#__________"
PATTERNS[idx336]="#_#_______#_______#_#"
PATTERNS[idx408]="#__#______#______#__#"
PATTERNS[idx216]="##________#________##"
PATTERNS[idx28]="#___#_____#_____#___#"
PATTERNS[idx40]="#####_____#_____#####"
PATTERNS[idx42]="####_#____#____#_####"
PATTERNS[idx44]="####__#___#___#__####"
PATTERNS[idx56]="###_#_#___#___#_#_###"
PATTERNS[idx54]="###_##____#____##_###"
PATTERNS[idx100]="##_##_#___#___#_##_##"

echo "launching ${#PATTERNS[@]} pattern workers, each processing all 50 real genomes..."
for label in "${!PATTERNS[@]}"; do
    pattern="${PATTERNS[$label]}"
    nohup bash "${REPO_DIR}/real_genome_pattern_worker.sh" "$label" "$pattern" > "${LOG_DIR}/${label}.log" 2>&1 &
    echo "  started ${label} (pid $!) -> ${LOG_DIR}/${label}.log"
done

echo ""
echo "check progress:  tail -f ${LOG_DIR}/<label>.log"
echo "check if running: ps aux | grep real_genome_pattern_worker | grep -v grep"
echo "results land in:  ${REPO_DIR}/real_genome_results/variants_<label>.csv"
