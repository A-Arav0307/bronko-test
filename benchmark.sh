#!/bin/bash

if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ]; then
    echo "usage: ./benchmark.sh <label> <genome_fasta> <reads_fastq>"
    echo "example: ./benchmark.sh 1000000 /path/to/genome.fasta /path/to/reads.fastq"
    exit 1
fi

LABEL=$1
GENOME=$2
READS=$3
OLD=~/bronko_benchmark/bronko-test/old_bronko/target/release/bronko
NEW=~/bronko_benchmark/bronko-test/target/release/bronko
THREADS=30
RESULTS_CSV=~/bronko_benchmark/results.csv
RUNS=1

if [ ! -f $RESULTS_CSV ]; then
    echo "label,version,run,time_s,peak_memory_gb" > $RESULTS_CSV
fi

get_median() {
    local arr=("$@")
    local sorted=($(printf '%s\n' "${arr[@]}" | sort -n))
    local mid=$(( ${#sorted[@]} / 2 ))
    echo "${sorted[$mid]}"
}

run_bronko() {
    local binary=$1
    local version=$2
    local out_dir=$3
    local extra_args=${4:-""}

    echo "==============================="
    echo "running ${version} on ${LABEL} (${RUNS} runs)..."
    echo "==============================="

    local times=()
    local last_mem=0

    for i in $(seq 1 $RUNS); do
        echo "  run $i/$RUNS..."
        /usr/bin/time -v $binary call -g $GENOME -r $READS -o $out_dir -t $THREADS -k 21 $extra_args 2>/tmp/${version}_time_${i}.txt
        local t=$(grep "wall clock" /tmp/${version}_time_${i}.txt | awk '{print $NF}' | awk -F: '{printf "%.2f", $1*60+$2}')
        local m=$(grep "Maximum resident" /tmp/${version}_time_${i}.txt | awk '{printf "%.2f", $NF/1024/1024}')
        times+=($t)
        last_mem=$m
        echo "$LABEL,$version,$i,$t,$m" >> $RESULTS_CSV
    done

    local median=$(get_median "${times[@]}")
    echo "  → median: ${median}s, peak mem: ${last_mem}gb"

    echo "$median" > /tmp/${version}_median.txt
    echo "$last_mem" > /tmp/${version}_mem.txt
}

run_bronko $OLD "old" /tmp/out_old
run_bronko $NEW "nostride" /tmp/out_nostride "--bucket-stride 1"
run_bronko $NEW "stride2" /tmp/out_stride2

old_median=$(cat /tmp/old_median.txt)
old_mem=$(cat /tmp/old_mem.txt)
nostride_median=$(cat /tmp/nostride_median.txt)
nostride_mem=$(cat /tmp/nostride_mem.txt)
stride2_median=$(cat /tmp/stride2_median.txt)
stride2_mem=$(cat /tmp/stride2_mem.txt)

echo ""
echo "==============================="
echo "RESULTS SUMMARY — ${LABEL}"
echo "==============================="
printf "%-12s %-12s %-15s\n" "version" "median(s)" "peak_mem(gb)"
printf "%-12s %-12s %-15s\n" "old" "$old_median" "$old_mem"
printf "%-12s %-12s %-15s\n" "nostride" "$nostride_median" "$nostride_mem"
printf "%-12s %-12s %-15s\n" "stride2" "$stride2_median" "$stride2_mem"

speedup_nostride=$(echo "scale=2; $old_median / $nostride_median" | bc)
speedup_stride=$(echo "scale=2; $old_median / $stride2_median" | bc)
echo ""
echo "Speedup old → nostride: ${speedup_nostride}x"
echo "Speedup old → stride2:  ${speedup_stride}x"

echo ""
echo "==============================="
echo "correctness check (variant counts)..."
echo "==============================="
old_vars=$(grep -v "^#" /tmp/out_old/*.vcf 2>/dev/null | wc -l)
nostride_vars=$(grep -v "^#" /tmp/out_nostride/*.vcf 2>/dev/null | wc -l)
stride2_vars=$(grep -v "^#" /tmp/out_stride2/*.vcf 2>/dev/null | wc -l)
echo "old variants called:      $old_vars"
echo "nostride variants called: $nostride_vars"
echo "stride2 variants called:  $stride2_vars"

echo ""
echo "results saved to $RESULTS_CSV"
