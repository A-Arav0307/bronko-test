#!/bin/bash
set -e

LABEL=$1
PATTERN=$2   # empty string means no --bucket-pattern/--specify-pattern at all (default baseline)

if [ -z "$LABEL" ]; then
    echo "usage: ./real_genome_pattern_worker.sh <label> [pattern]"
    exit 1
fi

BENCH_DIR=~/bronko_benchmark/phastsim-run-round2
REPO_DIR=~/bronko_benchmark/bronko-test
BIN=$REPO_DIR/target/release/bronko
GENOMES_DIR=~/bronko_benchmark/genomes_round2
READS_DIR=$BENCH_DIR/real_genome_reads
REF=$BENCH_DIR/reference_single_chromosome_only.fasta

OUT_DIR=/tmp/real_pattern_${LABEL}
RESULTS_DIR=$REPO_DIR/real_genome_results
RESULTS_CSV=$RESULTS_DIR/variants_${LABEL}.csv

mkdir -p "$RESULTS_DIR"

if [ ! -f "$RESULTS_CSV" ]; then
    echo "genome_id,pos,ref,alt" > $RESULTS_CSV
fi

declare -A DONE
if [ -f "$RESULTS_CSV" ]; then
    while IFS=, read -r g rest; do
        DONE["${g}"]=1
    done < <(tail -n +2 "$RESULTS_CSV" | cut -d, -f1 | sort -u | awk '{print $0","}')
fi

# figure out which genomes are already fully done (appear at all in output = at least attempted;
# since a genome with 0 variants would leave no rows, track completion via a separate marker file)
MARKER_DIR=$RESULTS_DIR/.done_${LABEL}
mkdir -p "$MARKER_DIR"

for genome_fna in $GENOMES_DIR/*.fna; do
    genome_id=$(basename "$genome_fna")

    if [ -f "$MARKER_DIR/$genome_id" ]; then
        continue
    fi

    R1="${READS_DIR}/${genome_id}_r1.fq"
    R2="${READS_DIR}/${genome_id}_r2.fq"

    rm -rf "$OUT_DIR"
    mkdir -p "$OUT_DIR"

    if [ -n "$PATTERN" ]; then
        PATTERN_ARG="--bucket-pattern $PATTERN"
    else
        PATTERN_ARG=""
    fi

    if ! $BIN call -g $REF -1 "$R1" -2 "$R2" -o "$OUT_DIR" -t 10 --use-full-kmer $PATTERN_ARG 2> /tmp/real_${LABEL}_${genome_id}.log; then
        echo "FAILED: label=${LABEL} genome=${genome_id}" >&2
        cat /tmp/real_${LABEL}_${genome_id}.log >&2
        continue
    fi

    vcf=$(ls ${OUT_DIR}/*.vcf 2>/dev/null | head -1)
    if [ -z "$vcf" ]; then
        echo "FAILED: no vcf for label=${LABEL} genome=${genome_id}" >&2
        continue
    fi

    # parse this genome's VCF and append (genome_id,pos,ref,alt) rows to the pooled per-pattern CSV
    python3 -c "
import sys, re
genome_id = '$genome_id'
with open('$vcf') as f, open('$RESULTS_CSV', 'a') as out:
    for line in f:
        if line.startswith('#'):
            continue
        fields = line.rstrip('\n').split('\t')
        if len(fields) < 5:
            continue
        _chrom, pos, _id, ref, alt = fields[:5]
        out.write(f'{genome_id},{pos},{ref.upper()},{alt.upper()}\n')
"

    touch "$MARKER_DIR/$genome_id"
    echo "[${LABEL}] done: ${genome_id}"
    rm -f /tmp/real_${LABEL}_${genome_id}.log
done

rm -rf "$OUT_DIR"
echo "label ${LABEL} complete"
