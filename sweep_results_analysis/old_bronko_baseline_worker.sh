#!/bin/bash
set -e

JOB_ID=$1
NUM_JOBS=$2

if [ -z "$JOB_ID" ] || [ -z "$NUM_JOBS" ]; then
    echo "usage: ./old_bronko_baseline_worker.sh <job_id> <num_jobs>"
    exit 1
fi

BENCH_DIR=~/bronko_benchmark/phastsim-run
REPO_DIR=~/bronko_benchmark/bronko-test
BIN=$REPO_DIR/old_bronko/target/release/bronko
GENOMES_DIR=$BENCH_DIR/genomes_50
MANIFEST=$BENCH_DIR/genomes_50_manifest.txt
REF=$BENCH_DIR/reference_single.fasta
COMPARE_SCRIPT=$BENCH_DIR/compare_bronko_vcf.py

OUT_DIR=/tmp/old_baseline_job_${JOB_ID}
RESULTS_DIR=$REPO_DIR/old_baseline_results
RESULTS_CSV=$RESULTS_DIR/old_baseline_job${JOB_ID}.csv

mkdir -p "$RESULTS_DIR"
cd $BENCH_DIR

if [ ! -f "$RESULTS_CSV" ]; then
    echo "genome_id,time_s,mem_gb,precision,recall,f1" > $RESULTS_CSV
fi

mapfile -t GENOME_IDS < "$MANIFEST"
NUM_GENOMES=${#GENOME_IDS[@]}

declare -A DONE
if [ -f "$RESULTS_CSV" ]; then
    while IFS=, read -r g rest; do
        DONE["$g"]=1
    done < <(tail -n +2 "$RESULTS_CSV")
fi

for ((i=JOB_ID; i<NUM_GENOMES; i+=NUM_JOBS)); do
    genome_id="${GENOME_IDS[$i]}"
    if [ -n "${DONE[$genome_id]}" ]; then
        continue
    fi

    R1="${GENOMES_DIR}/${genome_id}_r1.fq"
    R2="${GENOMES_DIR}/${genome_id}_r2.fq"
    TRUTH="${GENOMES_DIR}/${genome_id}_ground_truth.csv"

    rm -rf "$OUT_DIR"
    mkdir -p "$OUT_DIR"

    TIME_LOG=$(mktemp)
    if ! /usr/bin/time -v $BIN call -g $REF -1 "$R1" -2 "$R2" -o "$OUT_DIR" -t 10 2> "$TIME_LOG"; then
        echo "FAILED: genome=${genome_id}" >&2
        rm -f "$TIME_LOG"
        continue
    fi

    t=$(grep "wall clock" "$TIME_LOG" | awk '{print $NF}' | awk -F: '{printf "%.2f", $1*60+$2}')
    m=$(grep "Maximum resident" "$TIME_LOG" | awk '{printf "%.2f", $NF/1024/1024}')
    rm -f "$TIME_LOG"

    vcf=$(ls ${OUT_DIR}/*.vcf 2>/dev/null | head -1)
    if [ -z "$vcf" ]; then
        echo "FAILED: no vcf for genome=${genome_id}" >&2
        continue
    fi

    compare_out=$(python3 "$COMPARE_SCRIPT" "$vcf" "$TRUTH")
    precision=$(echo "$compare_out" | grep "^precision:" | awk '{print $2}')
    recall=$(echo "$compare_out" | grep "^recall:" | awk '{print $2}')
    f1=$(python3 -c "p=$precision; r=$recall; print(f'{2*p*r/(p+r):.4f}' if (p+r)>0 else '0.0000')")

    echo "${genome_id},${t},${m},${precision},${recall},${f1}" >> "$RESULTS_CSV"
    echo "[job ${JOB_ID}] genome $((i + 1))/${NUM_GENOMES} (${genome_id}): time=${t}s mem=${m}gb precision=${precision} recall=${recall} f1=${f1}"
done

rm -rf "$OUT_DIR"
echo "job ${JOB_ID} complete"
