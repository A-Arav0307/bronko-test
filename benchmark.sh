#!/bin/bash

if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ]; then
    echo "usage: ./benchmark.sh <label> <genome_fasta> <reads_fastq> [reads2_fastq] [ground_truth_txt]"
    echo "  reads2_fastq      second paired-end reads (optional, enables paired-end mode)"
    echo "  ground_truth_txt  wgsim mutations file for recall calculation (optional)"
    echo ""
    echo "examples:"
    echo "  ./benchmark.sh 1M genome.fasta reads.fastq"
    echo "  ./benchmark.sh ecoli ecoli.fasta r1.fq r2.fq ground_truth.txt"
    exit 1
fi

LABEL=$1
GENOME=$2
READS=$3
READS2=""
GROUND_TRUTH=""

# parse optional args — detect if 4th arg is a fastq (paired end) or txt (ground truth)
if [ ! -z "$4" ]; then
    if [[ "$4" == *.txt ]]; then
        GROUND_TRUTH=$4
    else
        READS2=$4
    fi
fi
if [ ! -z "$5" ]; then
    GROUND_TRUTH=$5
fi

OLD=~/bronko_benchmark/bronko-test/old_bronko/target/release/bronko
THREADED=~/bronko_benchmark/bronko-test/bronko_threaded/target/release/bronko
NEW=~/bronko_benchmark/bronko-test/target/release/bronko
THREADS=30
RESULTS_CSV=~/bronko_benchmark/results.csv
RUNS=1

if [ ! -f $RESULTS_CSV ]; then
    echo "label,version,run,time_s,peak_memory_gb,variants_called,recall_pct,kmers_perfect,kmers_total,breadth,depth" > $RESULTS_CSV
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

    rm -rf $out_dir && mkdir -p $out_dir

    local times=()
    local last_mem=0

    for i in $(seq 1 $RUNS); do
        echo "  run $i/$RUNS..."
        if [ -z "$READS2" ]; then
            /usr/bin/time -v $binary call -g $GENOME -r $READS -o $out_dir -t $THREADS -k 21 $extra_args 2>/tmp/${version}_log_${i}.txt
        else
            /usr/bin/time -v $binary call -g $GENOME -1 $READS -2 $READS2 -o $out_dir -t $THREADS -k 21 $extra_args 2>/tmp/${version}_log_${i}.txt
        fi
        local t=$(grep "wall clock" /tmp/${version}_log_${i}.txt | awk '{print $NF}' | awk -F: '{printf "%.2f", $1*60+$2}')
        local m=$(grep "Maximum resident" /tmp/${version}_log_${i}.txt | awk '{printf "%.2f", $NF/1024/1024}')
        times+=($t)
        last_mem=$m
    done

    local median=$(get_median "${times[@]}")
    local log=/tmp/${version}_log_${RUNS}.txt

    local kmers_perfect=$(grep "kmers perfectly" $log | grep -oE '[0-9]+/[0-9]+' | head -1 | cut -d'/' -f1)
    local kmers_total=$(grep "kmers perfectly" $log | grep -oE '[0-9]+/[0-9]+' | head -1 | cut -d'/' -f2)
    local breadth=$(grep "breadth of coverage" $log | awk -F'breadth of coverage: ' '{print $2}' | awk -F',' '{print $1}' | tail -1)
    local depth=$(grep "depth of coverage" $log | awk -F'depth of coverage: ' '{print $2}' | awk '{print $1}' | tail -1)
    local variants=$(grep -v "^#" $out_dir/*.vcf 2>/dev/null | wc -l | tr -d ' ')

    local recall="N/A"
    if [ ! -z "$GROUND_TRUTH" ] && [ -f "$GROUND_TRUTH" ]; then
        local total_injected=$(wc -l < $GROUND_TRUTH)
        recall=$(echo "scale=1; $variants * 100 / $total_injected" | bc)%
    fi

    echo "$median"        > /tmp/${version}_median.txt
    echo "$last_mem"      > /tmp/${version}_mem.txt
    echo "$variants"      > /tmp/${version}_variants.txt
    echo "$recall"        > /tmp/${version}_recall.txt
    echo "$breadth"       > /tmp/${version}_breadth.txt
    echo "$depth"         > /tmp/${version}_depth.txt

    echo "$LABEL,$version,1,$median,$last_mem,$variants,$recall,$kmers_perfect,$kmers_total,$breadth,$depth" >> $RESULTS_CSV

    echo "  → time: ${median}s | mem: ${last_mem}gb | variants: $variants | recall: $recall | breadth: $breadth | depth: $depth"
}

run_bronko $OLD      "old"      /tmp/out_old
run_bronko $THREADED "threaded" /tmp/out_threaded
run_bronko $NEW      "stride2"  /tmp/out_stride2

old_median=$(cat /tmp/old_median.txt)
old_mem=$(cat /tmp/old_mem.txt)
old_vars=$(cat /tmp/old_variants.txt)
old_recall=$(cat /tmp/old_recall.txt)
old_breadth=$(cat /tmp/old_breadth.txt)
old_depth=$(cat /tmp/old_depth.txt)

threaded_median=$(cat /tmp/threaded_median.txt)
threaded_mem=$(cat /tmp/threaded_mem.txt)
threaded_vars=$(cat /tmp/threaded_variants.txt)
threaded_recall=$(cat /tmp/threaded_recall.txt)
threaded_breadth=$(cat /tmp/threaded_breadth.txt)
threaded_depth=$(cat /tmp/threaded_depth.txt)

stride2_median=$(cat /tmp/stride2_median.txt)
stride2_mem=$(cat /tmp/stride2_mem.txt)
stride2_vars=$(cat /tmp/stride2_variants.txt)
stride2_recall=$(cat /tmp/stride2_recall.txt)
stride2_breadth=$(cat /tmp/stride2_breadth.txt)
stride2_depth=$(cat /tmp/stride2_depth.txt)

speedup_threaded=$(echo "scale=2; $old_median / $threaded_median" | bc)
speedup_stride=$(echo "scale=2; $old_median / $stride2_median" | bc)
mem_save_threaded=$(echo "scale=1; (1 - $threaded_mem / $old_mem) * 100" | bc)
mem_save_stride=$(echo "scale=1; (1 - $stride2_mem / $old_mem) * 100" | bc)

echo ""
echo "========================================================"
echo "RESULTS SUMMARY — ${LABEL}"
echo "========================================================"
printf "%-12s %-10s %-12s %-10s %-10s %-10s %-10s\n" "version" "time(s)" "mem(gb)" "variants" "recall" "breadth" "depth"
printf "%-12s %-10s %-12s %-10s %-10s %-10s %-10s\n" "old"      "$old_median"      "$old_mem"      "$old_vars"      "$old_recall"      "$old_breadth"      "$old_depth"
printf "%-12s %-10s %-12s %-10s %-10s %-10s %-10s\n" "threaded" "$threaded_median" "$threaded_mem" "$threaded_vars" "$threaded_recall" "$threaded_breadth" "$threaded_depth"
printf "%-12s %-10s %-12s %-10s %-10s %-10s %-10s\n" "stride2"  "$stride2_median"  "$stride2_mem"  "$stride2_vars"  "$stride2_recall"  "$stride2_breadth"  "$stride2_depth"
echo ""
echo "Speedup old → threaded: ${speedup_threaded}x  (mem saved: ${mem_save_threaded}%)"
echo "Speedup old → stride2:  ${speedup_stride}x  (mem saved: ${mem_save_stride}%)"
echo ""
echo "results saved to $RESULTS_CSV"
