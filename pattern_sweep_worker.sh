#!/bin/bash
set -e

JOB_ID=$1
NUM_JOBS=$2

if [ -z "$JOB_ID" ] || [ -z "$NUM_JOBS" ]; then
    echo "usage: ./pattern_sweep_worker.sh <job_id> <num_jobs>"
    exit 1
fi

BENCH_DIR=~/bronko_benchmark/phastsim-run
REPO_DIR=~/bronko_benchmark/bronko-test
BIN=$REPO_DIR/target/release/bronko
GENOMES_DIR=$BENCH_DIR/genomes_50
MANIFEST=$BENCH_DIR/genomes_50_manifest.txt
PATTERNS=$BENCH_DIR/patterns_500.txt
REF=$BENCH_DIR/reference_single.fasta
COMPARE_SCRIPT=$BENCH_DIR/compare_bronko_vcf.py

OUT_DIR=/tmp/pattern_sweep_job_${JOB_ID}
RESULTS_DIR=$REPO_DIR/sweep_results
RESULTS_CSV=$RESULTS_DIR/pattern_sweep_results_job${JOB_ID}.csv

mkdir -p "$RESULTS_DIR"
cd $BENCH_DIR

if [ ! -f "$RESULTS_CSV" ]; then
    echo "genome_id,pattern_idx,pattern,time_s,mem_gb,precision,recall,f1" > $RESULTS_CSV
fi

mapfile -t GENOME_IDS < "$MANIFEST"
mapfile -t PATTERN_LINES < "$PATTERNS"

NUM_GENOMES=${#GENOME_IDS[@]}
NUM_PATTERNS=${#PATTERN_LINES[@]}
TOTAL=$((NUM_GENOMES * NUM_PATTERNS))

echo "job ${JOB_ID}/${NUM_JOBS}: ${NUM_GENOMES} genomes x ${NUM_PATTERNS} patterns = ${TOTAL} combinations, processing every ${NUM_JOBS}th starting at ${JOB_ID}"

# resumability: skip combinations already recorded in this job's CSV (survives job restarts)
declare -A DONE
if [ -f "$RESULTS_CSV" ]; then
    while IFS=, read -r g p rest; do
        DONE["${g}_${p}"]=1
    done < <(tail -n +2 "$RESULTS_CSV")
fi

for ((k=JOB_ID; k<TOTAL; k+=NUM_JOBS)); do
    genome_idx=$((k / NUM_PATTERNS))
    pattern_idx=$((k % NUM_PATTERNS))

    genome_id="${GENOME_IDS[$genome_idx]}"
    pattern_line="${PATTERN_LINES[$pattern_idx]}"
    pattern="${pattern_line#*$'\t'}"

    if [ -n "${DONE[${genome_id}_${pattern_idx}]}" ]; then
        continue
    fi

    R1="${GENOMES_DIR}/${genome_id}_r1.fq"
    R2="${GENOMES_DIR}/${genome_id}_r2.fq"
    TRUTH="${GENOMES_DIR}/${genome_id}_ground_truth.csv"

    rm -rf "$OUT_DIR"
    mkdir -p "$OUT_DIR"

    TIME_LOG=$(mktemp)
    if ! /usr/bin/time -v $BIN call -g $REF -1 "$R1" -2 "$R2" -o "$OUT_DIR" -t 10 --bucket-pattern "$pattern" 2> "$TIME_LOG"; then
        echo "FAILED: genome=${genome_id} pattern_idx=${pattern_idx} -- error output:" >&2
        cat "$TIME_LOG" >&2
        rm -f "$TIME_LOG"
        continue
    fi

    t=$(grep "wall clock" "$TIME_LOG" | awk '{print $NF}' | awk -F: '{printf "%.2f", $1*60+$2}')
    m=$(grep "Maximum resident" "$TIME_LOG" | awk '{printf "%.2f", $NF/1024/1024}')
    rm -f "$TIME_LOG"

    vcf=$(ls ${OUT_DIR}/*.vcf 2>/dev/null | head -1)
    if [ -z "$vcf" ]; then
        echo "FAILED: no vcf for genome=${genome_id} pattern_idx=${pattern_idx}" >&2
        continue
    fi

    compare_out=$(python3 "$COMPARE_SCRIPT" "$vcf" "$TRUTH")
    precision=$(echo "$compare_out" | grep "^precision:" | awk '{print $2}')
    recall=$(echo "$compare_out" | grep "^recall:" | awk '{print $2}')
    f1=$(python3 -c "p=$precision; r=$recall; print(f'{2*p*r/(p+r):.4f}' if (p+r)>0 else '0.0000')")

    echo "${genome_id},${pattern_idx},${pattern},${t},${m},${precision},${recall},${f1}" >> "$RESULTS_CSV"
    echo "[job ${JOB_ID}] genome $((genome_idx + 1))/${NUM_GENOMES} (${genome_id}) pattern $((pattern_idx + 1))/${NUM_PATTERNS} [${pattern}]: time=${t}s mem=${m}gb precision=${precision} recall=${recall} f1=${f1}"
done

rm -rf "$OUT_DIR"
echo "job ${JOB_ID} complete"
