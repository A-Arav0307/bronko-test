#!/bin/bash
set -e

# add new patterns here to test them - '#' = keep, '_' = skip, repeats cyclically
# format: "label=pattern" (label is used for the output dir name, keep it short/safe)
PATTERNS=(
    "hash_underscore=#_"
    "hh_underscore=##_"
    "random_gap1to3_seed42=#__###__#_####__##__#__#__##__#_######__#__##__##__#__#__#__"
)

BENCH_DIR=~/bronko_benchmark/phastsim-run
OLD_BIN=~/bronko_benchmark/bronko-test/old_bronko/target/release/bronko
THREADED_BIN=~/bronko_benchmark/bronko-test/bronko_threaded/target/release/bronko
PATTERN_BIN=~/bronko_benchmark/bronko-test/target/release/bronko

GENOME=$BENCH_DIR/reference_single.fasta
R1=$BENCH_DIR/single_genome_r1.fq
R2=$BENCH_DIR/single_genome_r2.fq
TRUTH=$BENCH_DIR/single_genome_ground_truth.csv

cd $BENCH_DIR

SUMMARY=$BENCH_DIR/pattern_test_summary.csv
echo "label,time_s,mem_gb,precision,recall" > $SUMMARY

run_and_measure() {
    local label=$1
    local binary=$2
    shift 2
    local extra_args=("$@")

    local out_dir="single_genome_wgsim_out_${label}"
    local time_log="time_${label}.log"

    echo "==============================="
    echo "running ${label}..."
    echo "==============================="

    /usr/bin/time -v $binary call -g $GENOME -1 $R1 -2 $R2 -o $out_dir -t 30 "${extra_args[@]}" 2> $time_log

    local t=$(grep "wall clock" $time_log | awk '{print $NF}' | awk -F: '{printf "%.2f", $1*60+$2}')
    local m=$(grep "Maximum resident" $time_log | awk '{printf "%.2f", $NF/1024/1024}')

    local compare_out=$(python3 compare_bronko_vcf.py ${out_dir}/*.vcf $TRUTH)
    local precision=$(echo "$compare_out" | grep "^precision:" | awk '{print $2}')
    local recall=$(echo "$compare_out" | grep "^recall:" | awk '{print $2}')

    echo "$compare_out"
    echo "$label,$t,$m,$precision,$recall" >> $SUMMARY
    echo "  -> time: ${t}s | mem: ${m}gb | precision: $precision | recall: $recall"
    echo ""
}

# --- fixed baselines: same as "how it was before" ---
run_and_measure "old" $OLD_BIN
run_and_measure "threaded" $THREADED_BIN

# --- pattern sweep on the current (bucket-pattern-experiment) binary ---
for entry in "${PATTERNS[@]}"; do
    label="${entry%%=*}"
    pattern="${entry#*=}"
    echo "pattern for '${label}': ${pattern}"
    run_and_measure "pattern_${label}" $PATTERN_BIN --bucket-pattern "$pattern"
done

echo "==============================="
echo "ALL RESULTS"
echo "==============================="
column -s, -t $SUMMARY
