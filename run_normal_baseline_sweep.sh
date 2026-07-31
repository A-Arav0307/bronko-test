#!/bin/bash
set -e

BENCH_DIR=~/bronko_benchmark/phastsim-run-round2
REPO_DIR=~/bronko_benchmark/bronko-test
BIN=$REPO_DIR/target/release/bronko
GENOMES_DIR=$BENCH_DIR/genomes_50
MANIFEST=$BENCH_DIR/genomes_50_manifest.txt
REF=$BENCH_DIR/reference_single.fasta
COMPARE_SCRIPT=$BENCH_DIR/compare_bronko_vcf.py

RESULTS_CSV=$REPO_DIR/sweep_results_round2/normal_baseline.csv
echo "genome_id,time_s,mem_gb,precision,recall,f1" > $RESULTS_CSV

while read -r genome_id; do
    OUT_DIR=/tmp/normal_baseline_${genome_id}
    R1="${GENOMES_DIR}/${genome_id}_r1.fq"
    R2="${GENOMES_DIR}/${genome_id}_r2.fq"
    TRUTH="${GENOMES_DIR}/${genome_id}_ground_truth.csv"

    rm -rf "$OUT_DIR"
    mkdir -p "$OUT_DIR"

    TIME_LOG=$(mktemp)
    if ! /usr/bin/time -v $BIN call -g $REF -1 "$R1" -2 "$R2" -o "$OUT_DIR" -t 10 --use-full-kmer --bucket-stride 1 2> "$TIME_LOG"; then
        echo "FAILED: genome=${genome_id}" >&2
        cat "$TIME_LOG" >&2
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
    echo "done: ${genome_id}  time=${t}s mem=${m}gb precision=${precision} recall=${recall} f1=${f1}"
    rm -rf "$OUT_DIR"
done < "$MANIFEST"

echo "wrote $RESULTS_CSV"
