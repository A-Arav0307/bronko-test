#!/bin/bash
set -e

BENCH_DIR=~/bronko_benchmark/phastsim-run-round2
REPO_DIR=~/bronko_benchmark/bronko-test
BIN=$REPO_DIR/target/release/bronko
GENOMES_DIR=~/bronko_benchmark/genomes_round2
READS_DIR=$BENCH_DIR/real_genome_reads
REF=$BENCH_DIR/reference_single_chromosome_only.fasta

RAW_DIR=$REPO_DIR/real_genome_raw_output
mkdir -p "$RAW_DIR"

label="true_full_density"
extra_args="--bucket-stride 1"
label_dir="$RAW_DIR/$label"
mkdir -p "$label_dir"

echo "=== running ${label} (args: ${extra_args}) ==="

for genome_fna in $GENOMES_DIR/*.fna; do
    genome_id=$(basename "$genome_fna")
    out_dir="$label_dir/$genome_id"

    if [ -d "$out_dir" ] && [ -n "$(ls -A "$out_dir" 2>/dev/null)" ]; then
        echo "[${label}] skip (already done): ${genome_id}"
        continue
    fi

    mkdir -p "$out_dir"
    R1="${READS_DIR}/${genome_id}_r1.fq"
    R2="${READS_DIR}/${genome_id}_r2.fq"

    if ! $BIN call -g $REF -1 "$R1" -2 "$R2" -o "$out_dir" -t 10 --use-full-kmer --pileup $extra_args 2> "$out_dir/stderr.log"; then
        echo "FAILED: label=${label} genome=${genome_id}" >&2
        cat "$out_dir/stderr.log" >&2
        continue
    fi

    echo "[${label}] done: ${genome_id}"
done

echo "raw VCF + pileup output saved under: $RAW_DIR/${label}/<genome_id>/"
