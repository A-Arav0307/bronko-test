#!/bin/bash
set -e

# add new patterns here to test them - '#' = keep, '_' = skip, repeats cyclically
# format: "label=pattern" (label is used for the output dir name, keep it short/safe)
PATTERNS=(
    "hash_underscore=#_"
    "hh_underscore=##_"
    "random_gap1to3_seed42=#__###__#_####__##__#__#__##__#_######__#__##__##__#__#__#__"
    "sparse_1in3=#__"
    "dense_3in4=###_"
    "clustered_2in4=##__"
    "sparse_1in4=#___"
    "random_gap1to2_seed7=#_##_####_#####_#_####_#####_#####_#_###_####_#####_#_#_#_#_"
    "random_gap1to4_seed99=#___#___#_#_#_#_#_##__#___##___#_#___#_#__#___#_#_#___#_#__#"
    "random_gap2to4_seed123=#_#__#_#__#__#_#_#__#___#___#__#__#_#_#_#__#___#__#___#_#_#_"
)

BENCH_DIR=~/bronko_benchmark/phastsim-run
OLD_BIN=~/bronko_benchmark/bronko-test/old_bronko/target/release/bronko
THREADED_BIN=~/bronko_benchmark/bronko-test/bronko_threaded/target/release/bronko
PATTERN_BIN=~/bronko_benchmark/bronko-test/target/release/bronko

GENOME=$BENCH_DIR/reference_single.fasta

# optional: pass a genome ID (matching genomes_50/<id>.fasta from setup_50_genomes.py)
# to test that genome instead of the original single_genome_* files
GENOME_ID=$1

cd $BENCH_DIR

if [ -n "$GENOME_ID" ]; then
    SRC_FASTA="genomes_50/${GENOME_ID}.fasta"
    R1="genomes_50/${GENOME_ID}_r1.fq"
    R2="genomes_50/${GENOME_ID}_r2.fq"
    TRUTH="genomes_50/${GENOME_ID}_ground_truth.csv"

    if [ ! -f "$SRC_FASTA" ]; then
        echo "ERROR: ${SRC_FASTA} not found - has setup_50_genomes.py been run?"
        exit 1
    fi
    if [ ! -f "$R1" ] || [ ! -f "$R2" ]; then
        echo "no reads yet for ${GENOME_ID}, simulating now..."
        wgsim -e 0.001 -r 0 -R 0 -X 0 -N 1000000 -1 150 -2 150 "$SRC_FASTA" "$R1" "$R2" > /dev/null
    fi
    SUMMARY=$BENCH_DIR/pattern_test_summary_${GENOME_ID}.csv
else
    R1=$BENCH_DIR/single_genome_r1.fq
    R2=$BENCH_DIR/single_genome_r2.fq
    TRUTH=$BENCH_DIR/single_genome_ground_truth.csv
    SUMMARY=$BENCH_DIR/pattern_test_summary.csv
fi

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
