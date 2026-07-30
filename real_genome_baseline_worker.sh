#!/bin/bash
set -e

JOB_ID=$1
NUM_JOBS=$2

if [ -z "$JOB_ID" ] || [ -z "$NUM_JOBS" ]; then
    echo "usage: ./real_genome_baseline_worker.sh <job_id> <num_jobs>"
    exit 1
fi

BENCH_DIR=~/bronko_benchmark/phastsim-run-round2
REPO_DIR=~/bronko_benchmark/bronko-test
BIN=$REPO_DIR/target/release/bronko
GENOMES_DIR=~/bronko_benchmark/genomes_round2
READS_DIR=$BENCH_DIR/real_genome_reads
REF=$BENCH_DIR/reference_single_chromosome_only.fasta

OUT_DIR=/tmp/real_baseline_job_${JOB_ID}
RESULTS_DIR=$REPO_DIR/real_genome_results
RESULTS_CSV=$RESULTS_DIR/variants_true_full_density_job${JOB_ID}.csv

mkdir -p "$RESULTS_DIR"
echo "genome_id,pos,ref,alt" > $RESULTS_CSV

mapfile -t GENOME_FILES < <(ls $GENOMES_DIR/*.fna)
NUM_GENOMES=${#GENOME_FILES[@]}

for ((idx=JOB_ID; idx<NUM_GENOMES; idx+=NUM_JOBS)); do
    genome_fna="${GENOME_FILES[$idx]}"
    genome_id=$(basename "$genome_fna")

    R1="${READS_DIR}/${genome_id}_r1.fq"
    R2="${READS_DIR}/${genome_id}_r2.fq"

    rm -rf "$OUT_DIR"
    mkdir -p "$OUT_DIR"

    if ! $BIN call -g $REF -1 "$R1" -2 "$R2" -o "$OUT_DIR" -t 10 --use-full-kmer --bucket-stride 1 2> /tmp/real_baseline_${JOB_ID}_${genome_id}.log; then
        echo "FAILED: job=${JOB_ID} genome=${genome_id}" >&2
        cat /tmp/real_baseline_${JOB_ID}_${genome_id}.log >&2
        continue
    fi

    vcf=$(ls ${OUT_DIR}/*.vcf 2>/dev/null | head -1)
    if [ -z "$vcf" ]; then
        echo "FAILED: no vcf for job=${JOB_ID} genome=${genome_id}" >&2
        continue
    fi

    python3 -c "
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
    echo "[job ${JOB_ID}] done: ${genome_id}"
    rm -f /tmp/real_baseline_${JOB_ID}_${genome_id}.log
done

rm -rf "$OUT_DIR"
echo "job ${JOB_ID} complete"
