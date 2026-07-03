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
    echo "label,version,run,time_s,peak_memory_gb,variants_called,kmers_perfect,kmers_total,kmers_variant,kmers_unmapped,breadth,depth" > $RESULTS_CSV
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
        /usr/bin/time -v $binary call -g $GENOME -r $READS -o $out_dir -t $THREADS -k 21 $extra_args 2>/tmp/${version}_log_${i}.txt
        local t=$(grep "wall clock" /tmp/${version}_log_${i}.txt | awk '{print $NF}' | awk -F: '{printf "%.2f", $1*60+$2}')
        local m=$(grep "Maximum resident" /tmp/${version}_log_${i}.txt | awk '{printf "%.2f", $NF/1024/1024}')
        times+=($t)
        last_mem=$m
    done

    local median=$(get_median "${times[@]}")
    local log=/tmp/${version}_log_${RUNS}.txt

    local kmers_perfect=$(grep "kmers perfectly" $log | grep -oE '[0-9]+/[0-9]+' | head -1 | cut -d'/' -f1)
    local kmers_total=$(grep "kmers perfectly" $log | grep -oE '[0-9]+/[0-9]+' | head -1 | cut -d'/' -f2)
    local kmers_variant=$(grep "had a variant" $log | awk -F',' '{print $2}' | grep -oE '[0-9]+' | head -1)
    local kmers_unmapped=$(grep "unmapped" $log | awk -F',' '{print $3}' | grep -oE '[0-9]+' | head -1)
    local breadth=$(grep "breadth of coverage" $log | awk -F'breadth of coverage: ' '{print $2}' | awk -F',' '{print $1}' | tail -1)
    local depth=$(grep "depth of coverage" $log | awk -F'depth of coverage: ' '{print $2}' | awk '{print $1}' | tail -1)
    local variants=$(grep -v "^#" $out_dir/*.vcf 2>/dev/null | wc -l | tr -d ' ')

    echo "$median"        > /tmp/${version}_median.txt
    echo "$last_mem"      > /tmp/${version}_mem.txt
    echo "$variants"      > /tmp/${version}_variants.txt
    echo "$kmers_perfect" > /tmp/${version}_kperfect.txt
    echo "$kmers_total"   > /tmp/${version}_ktotal.txt
    echo "$kmers_variant" > /tmp/${version}_kvariant.txt
    echo "$kmers_unmapped"> /tmp/${version}_kunmapped.txt
    echo "$breadth"       > /tmp/${version}_breadth.txt
    echo "$depth"         > /tmp/${version}_depth.txt

    echo "$LABEL,$version,1,$median,$last_mem,$variants,$kmers_perfect,$kmers_total,$kmers_variant,$kmers_unmapped,$breadth,$depth" >> $RESULTS_CSV

    echo "  → time: ${median}s | mem: ${last_mem}gb | variants: $variants | mapped: $kmers_perfect/$kmers_total | breadth: $breadth | depth: $depth"
}

run_bronko $OLD "old" /tmp/out_old
run_bronko $NEW "nostride" /tmp/out_nostride "--bucket-stride 1"
run_bronko $NEW "stride2" /tmp/out_stride2

old_median=$(cat /tmp/old_median.txt)
old_mem=$(cat /tmp/old_mem.txt)
old_vars=$(cat /tmp/old_variants.txt)
old_breadth=$(cat /tmp/old_breadth.txt)
old_depth=$(cat /tmp/old_depth.txt)

nostride_median=$(cat /tmp/nostride_median.txt)
nostride_mem=$(cat /tmp/nostride_mem.txt)
nostride_vars=$(cat /tmp/nostride_variants.txt)
nostride_breadth=$(cat /tmp/nostride_breadth.txt)
nostride_depth=$(cat /tmp/nostride_depth.txt)

stride2_median=$(cat /tmp/stride2_median.txt)
stride2_mem=$(cat /tmp/stride2_mem.txt)
stride2_vars=$(cat /tmp/stride2_variants.txt)
stride2_breadth=$(cat /tmp/stride2_breadth.txt)
stride2_depth=$(cat /tmp/stride2_depth.txt)

speedup_nostride=$(echo "scale=2; $old_median / $nostride_median" | bc)
speedup_stride=$(echo "scale=2; $old_median / $stride2_median" | bc)
mem_save_nostride=$(echo "scale=1; (1 - $nostride_mem / $old_mem) * 100" | bc)
mem_save_stride=$(echo "scale=1; (1 - $stride2_mem / $old_mem) * 100" | bc)

echo ""
echo "========================================================"
echo "RESULTS SUMMARY — ${LABEL}"
echo "========================================================"
printf "%-12s %-10s %-12s %-10s %-10s %-10s\n" "version" "time(s)" "mem(gb)" "variants" "breadth" "depth"
printf "%-12s %-10s %-12s %-10s %-10s %-10s\n" "old"      "$old_median"      "$old_mem"      "$old_vars"      "$old_breadth"      "$old_depth"
printf "%-12s %-10s %-12s %-10s %-10s %-10s\n" "nostride" "$nostride_median" "$nostride_mem" "$nostride_vars" "$nostride_breadth" "$nostride_depth"
printf "%-12s %-10s %-12s %-10s %-10s %-10s\n" "stride2"  "$stride2_median"  "$stride2_mem"  "$stride2_vars"  "$stride2_breadth"  "$stride2_depth"
echo ""
echo "Speedup old → nostride: ${speedup_nostride}x  (mem saved: ${mem_save_nostride}%)"
echo "Speedup old → stride2:  ${speedup_stride}x  (mem saved: ${mem_save_stride}%)"
echo ""
echo "results saved to $RESULTS_CSV"
