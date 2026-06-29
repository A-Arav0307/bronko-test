#!/bin/bash

if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ]; then
    echo "usage: ./benchmark.sh <label> <genome_fasta> <reads_fastq>"
    echo "example: ./benchmark.sh 1000000 /path/to/genome.fasta /path/to/reads.fastq"
    echo "example: ./benchmark.sh yeast /path/to/yeast.fasta /path/to/yeast_reads.fastq"
    echo "example: ./benchmark.sh 7mil /path/to/genome.fasta /path/to/7mil_reads.fastq"
    exit 1
fi

LABEL=$1
GENOME=$2
READS=$3
OLD=~/bronko_benchmark/bronko-test/old_bronko/target/release/bronko
NEW=~/bronko_benchmark/bronko-test/target/release/bronko
THREADS=30
RESULTS_CSV=~/bronko_benchmark/results.csv

# create csv with header if it doesn't exist
if [ ! -f $RESULTS_CSV ]; then
    echo "label,version,time_s,peak_memory_gb" > $RESULTS_CSV
fi

echo "==============================="
echo "running OLD bronko on ${LABEL}..."
echo "==============================="
/usr/bin/time -v $OLD call -g $GENOME -r $READS -o /tmp/out_old -t $THREADS -k 21 2>/tmp/old_time.txt
old_time=$(grep "wall clock" /tmp/old_time.txt | awk '{print $NF}' | awk -F: '{print $1*60+$2}')
old_mem=$(grep "Maximum resident" /tmp/old_time.txt | awk '{print $NF/1024/1024}')
echo "OLD bronko time: ${old_time}s, peak memory: ${old_mem}gb"
echo "$LABEL,old,$old_time,$old_mem" >> $RESULTS_CSV

echo ""
echo "==============================="
echo "running NEW bronko on ${LABEL}..."
echo "==============================="
/usr/bin/time -v $NEW call -g $GENOME -r $READS -o /tmp/out_new -t $THREADS -k 21 2>/tmp/new_time.txt
new_time=$(grep "wall clock" /tmp/new_time.txt | awk '{print $NF}' | awk -F: '{print $1*60+$2}')
new_mem=$(grep "Maximum resident" /tmp/new_time.txt | awk '{print $NF/1024/1024}')
echo "NEW bronko time: ${new_time}s, peak memory: ${new_mem}gb"
echo "$LABEL,new,$new_time,$new_mem" >> $RESULTS_CSV

echo ""
echo "==============================="
echo "RESULTS"
echo "==============================="
echo "OLD: ${old_time}s, ${old_mem}gb"
echo "NEW: ${new_time}s, ${new_mem}gb"
speedup=$(echo "scale=2; $old_time / $new_time" | bc)
echo "Speedup: ${speedup}x"

echo ""
echo "results saved to $RESULTS_CSV"
