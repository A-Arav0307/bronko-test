#!/bin/bash
set -e

BENCH_DIR=~/bronko_benchmark
MANIFEST=$BENCH_DIR/genome_lengths.csv
echo "label,length_bp" > $MANIFEST

gen_random_genome() {
    python3 -c "
import random
random.seed($3)
with open('$2', 'w') as f:
    f.write('>random_$1\n')
    f.write(''.join(random.choice('ACGT') for _ in range($1)) + '\n')
"
}

sim_reads() {
    wgsim -N 2000000 -1 150 -2 150 -e 0.001 -r 0.01 -R 0 -X 0 $1 $2 $3 > $4
}

genome_len() {
    grep -v '^>' $1 | tr -d '\n' | wc -c
}

if [ ! -f $BENCH_DIR/random1m.fasta ]; then
    echo "generating random 1M genome..."
    gen_random_genome 1000000 $BENCH_DIR/random1m.fasta 1
    sim_reads $BENCH_DIR/random1m.fasta $BENCH_DIR/random1m_r1.fq $BENCH_DIR/random1m_r2.fq $BENCH_DIR/random1m_ground_truth.txt
fi

if [ ! -f $BENCH_DIR/random2.5m.fasta ]; then
    echo "generating random 2.5M genome..."
    gen_random_genome 2500000 $BENCH_DIR/random2.5m.fasta 2
    sim_reads $BENCH_DIR/random2.5m.fasta $BENCH_DIR/random2.5m_r1.fq $BENCH_DIR/random2.5m_r2.fq $BENCH_DIR/random2.5m_ground_truth.txt
fi

if [ ! -f $BENCH_DIR/genome7m.fasta ]; then
    echo "downloading 7M reference genome (GCF_000283295.1)..."
    datasets download genome accession GCF_000283295.1 --include genome --filename $BENCH_DIR/gcf_7m.zip
    unzip -o $BENCH_DIR/gcf_7m.zip -d $BENCH_DIR/gcf_7m_dir
    find $BENCH_DIR/gcf_7m_dir -name "*.fna" -exec cp {} $BENCH_DIR/genome7m.fasta \;
    sim_reads $BENCH_DIR/genome7m.fasta $BENCH_DIR/genome7m_r1.fq $BENCH_DIR/genome7m_r2.fq $BENCH_DIR/genome7m_ground_truth.txt
fi

echo "1M,$(genome_len $BENCH_DIR/random1m.fasta)" >> $MANIFEST
echo "2.5M,$(genome_len $BENCH_DIR/random2.5m.fasta)" >> $MANIFEST
echo "4M,$(genome_len $BENCH_DIR/ecoli.fasta)" >> $MANIFEST
echo "7M,$(genome_len $BENCH_DIR/genome7m.fasta)" >> $MANIFEST
echo "12M,$(genome_len $BENCH_DIR/yeast.fasta)" >> $MANIFEST

cd $BENCH_DIR/bronko-test
./benchmark.sh 1M   $BENCH_DIR/random1m.fasta   $BENCH_DIR/random1m_r1.fq   $BENCH_DIR/random1m_r2.fq   $BENCH_DIR/random1m_ground_truth.txt
./benchmark.sh 2.5M $BENCH_DIR/random2.5m.fasta $BENCH_DIR/random2.5m_r1.fq $BENCH_DIR/random2.5m_r2.fq $BENCH_DIR/random2.5m_ground_truth.txt
./benchmark.sh 4M   $BENCH_DIR/ecoli.fasta      $BENCH_DIR/ecoli_r1.fq     $BENCH_DIR/ecoli_r2.fq     $BENCH_DIR/ecoli_ground_truth.txt
./benchmark.sh 7M   $BENCH_DIR/genome7m.fasta   $BENCH_DIR/genome7m_r1.fq  $BENCH_DIR/genome7m_r2.fq  $BENCH_DIR/genome7m_ground_truth.txt
./benchmark.sh 12M  $BENCH_DIR/yeast.fasta      $BENCH_DIR/yeast_r1.fq     $BENCH_DIR/yeast_r2.fq     $BENCH_DIR/yeast_ground_truth.txt

echo "sweep complete."
