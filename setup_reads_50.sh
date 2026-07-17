#!/bin/bash
set -e

GENOMES_DIR=genomes_50
MANIFEST=genomes_50_manifest.txt

while IFS= read -r genome_id; do
    fasta="${GENOMES_DIR}/${genome_id}.fasta"
    r1="${GENOMES_DIR}/${genome_id}_r1.fq"
    r2="${GENOMES_DIR}/${genome_id}_r2.fq"

    if [ -f "$r1" ] && [ -f "$r2" ]; then
        echo "skipping ${genome_id}, reads already exist"
        continue
    fi

    echo "simulating reads for ${genome_id}..."
    wgsim -e 0.001 -r 0 -R 0 -X 0 -N 1000000 -1 150 -2 150 "$fasta" "$r1" "$r2" > /dev/null
done < "$MANIFEST"

echo "done simulating reads for all genomes in ${MANIFEST}"
