#!/bin/bash
set -e

BENCH_DIR=~/bronko_benchmark
MANIFEST=$BENCH_DIR/genome_lengths.csv
echo "label,length_bp" > $MANIFEST

download_genome() {
    local accession=$1
    local outfile=$2
    local zip=$BENCH_DIR/$(basename $outfile .fasta).zip
    local dir=$BENCH_DIR/$(basename $outfile .fasta)_dir
    datasets download genome accession $accession --include genome --filename $zip
    unzip -o $zip -d $dir
    find $dir -name "*.fna" -exec cp {} $outfile \;
}

sim_reads() {
    wgsim -N 2000000 -1 150 -2 150 -e 0.001 -r 0.01 -R 0 -X 0 $1 $2 $3 > $4
}

genome_len() {
    grep -v '^>' $1 | tr -d '\n' | wc -c
}

build_summary() {
    {
        echo "label,version,length_bp,time_s,peak_memory_gb"
        awk -F, '
            NR==FNR { if (FNR>1) len[$1]=$2; next }
            FNR==1 { next }
            { key=$1 SUBSEP $2; time[key]=$4; mem[key]=$5; if (!(key in seen)) { order[++n]=key; seen[key]=1 } }
            END {
                for (i=1; i<=n; i++) {
                    key=order[i]; split(key, a, SUBSEP); label=a[1]; version=a[2]
                    if (label in len) print label","version","len[label]","time[key]","mem[key]
                }
            }
        ' $MANIFEST $BENCH_DIR/results.csv | sort -t, -k3,3n -k2,2
    } > $BENCH_DIR/sweep_summary.csv
    echo "saved $BENCH_DIR/sweep_summary.csv"
}

if [ ! -f $BENCH_DIR/genome1m.fasta ]; then
    echo "downloading 1M reference genome (Rickettsia prowazekii Madrid E, GCF_000195735.1)..."
    download_genome GCF_000195735.1 $BENCH_DIR/genome1m.fasta
    sim_reads $BENCH_DIR/genome1m.fasta $BENCH_DIR/genome1m_r1.fq $BENCH_DIR/genome1m_r2.fq $BENCH_DIR/genome1m_ground_truth.txt
fi

if [ ! -f $BENCH_DIR/genome2.5m.fasta ]; then
    echo "downloading 2.5M reference genome (Neisseria meningitidis MC58, GCF_000008805.1)..."
    download_genome GCF_000008805.1 $BENCH_DIR/genome2.5m.fasta
    sim_reads $BENCH_DIR/genome2.5m.fasta $BENCH_DIR/genome2.5m_r1.fq $BENCH_DIR/genome2.5m_r2.fq $BENCH_DIR/genome2.5m_ground_truth.txt
fi

if [ ! -f $BENCH_DIR/genome7m.fasta ]; then
    echo "downloading 7M reference genome (GCF_000283295.1)..."
    download_genome GCF_000283295.1 $BENCH_DIR/genome7m.fasta
    sim_reads $BENCH_DIR/genome7m.fasta $BENCH_DIR/genome7m_r1.fq $BENCH_DIR/genome7m_r2.fq $BENCH_DIR/genome7m_ground_truth.txt
fi

echo "1M,$(genome_len $BENCH_DIR/genome1m.fasta)" >> $MANIFEST
echo "2.5M,$(genome_len $BENCH_DIR/genome2.5m.fasta)" >> $MANIFEST
echo "4M,$(genome_len $BENCH_DIR/ecoli.fasta)" >> $MANIFEST
echo "7M,$(genome_len $BENCH_DIR/genome7m.fasta)" >> $MANIFEST
echo "12M,$(genome_len $BENCH_DIR/yeast.fasta)" >> $MANIFEST

cd $BENCH_DIR/bronko-test
./benchmark.sh 1M   $BENCH_DIR/genome1m.fasta   $BENCH_DIR/genome1m_r1.fq   $BENCH_DIR/genome1m_r2.fq   $BENCH_DIR/genome1m_ground_truth.txt
./benchmark.sh 2.5M $BENCH_DIR/genome2.5m.fasta $BENCH_DIR/genome2.5m_r1.fq $BENCH_DIR/genome2.5m_r2.fq $BENCH_DIR/genome2.5m_ground_truth.txt
./benchmark.sh 4M   $BENCH_DIR/ecoli.fasta      $BENCH_DIR/ecoli_r1.fq     $BENCH_DIR/ecoli_r2.fq     $BENCH_DIR/ecoli_ground_truth.txt
./benchmark.sh 7M   $BENCH_DIR/genome7m.fasta   $BENCH_DIR/genome7m_r1.fq  $BENCH_DIR/genome7m_r2.fq  $BENCH_DIR/genome7m_ground_truth.txt
./benchmark.sh 12M  $BENCH_DIR/yeast.fasta      $BENCH_DIR/yeast_r1.fq     $BENCH_DIR/yeast_r2.fq     $BENCH_DIR/yeast_ground_truth.txt

build_summary
echo "sweep complete."
