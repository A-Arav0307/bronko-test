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
ABLATION=~/bronko_benchmark/bronko-test/ablation_bronko/target/release/bronko
NEW=~/bronko_benchmark/bronko-test/target/release/bronko
THREADS=30
RESULTS_CSV=~/bronko_benchmark/results.csv
RUNS=5

# create csv with header if it doesn't exist
if [ ! -f $RESULTS_CSV ]; then
    echo "label,version,run,time_s,peak_memory_gb" > $RESULTS_CSV
fi

run_bronko() {
    local binary=$1
    local version=$2
    local out_dir=$3

    echo "==============================="
    echo "running ${version} bronko on ${LABEL} (${RUNS} runs)..."
    echo "==============================="

    local times=()
    local mem=0

    for i in $(seq 1 $RUNS); do
        echo "  run $i/$RUNS..."
        /usr/bin/time -v $binary call -g $GENOME -r $READS -o $out_dir -t $THREADS -k 21 2>/tmp/${version}_time_${i}.txt
        t=$(grep "wall clock" /tmp/${version}_time_${i}.txt | awk '{print $NF}' | awk -F: '{print $1*60+$2}')
        m=$(grep "Maximum resident" /tmp/${version}_time_${i}.txt | awk '{print $NF/1024/1024}')
        times+=($t)
        mem=$m
        echo "$LABEL,$version,$i,$t,$m" >> $RESULTS_CSV
    done

    # compute median
    sorted=($(printf '%s\n' "${times[@]}" | sort -n))
    mid=$(( ${#sorted[@]} / 2 ))
    median=${sorted[$mid]}

    echo "${version} median time: ${median}s, peak memory: ${mem}gb"
    echo "$median $mem"
}

old_result=$(run_bronko $OLD "old" /tmp/out_old)
old_median=$(echo $old_result | awk '{print $1}')
old_mem=$(echo $old_result | awk '{print $2}')

ablation_result=$(run_bronko $ABLATION "ablation" /tmp/out_ablation)
ablation_median=$(echo $ablation_result | awk '{print $1}')
ablation_mem=$(echo $ablation_result | awk '{print $2}')

new_result=$(run_bronko $NEW "new" /tmp/out_new)
new_median=$(echo $new_result | awk '{print $1}')
new_mem=$(echo $new_result | awk '{print $2}')

echo ""
echo "==============================="
echo "RESULTS SUMMARY — ${LABEL}"
echo "==============================="
printf "%-12s %-12s %-15s\n" "version" "median(s)" "peak_mem(gb)"
printf "%-12s %-12s %-15s\n" "old" "$old_median" "$old_mem"
printf "%-12s %-12s %-15s\n" "ablation" "$ablation_median" "$ablation_mem"
printf "%-12s %-12s %-15s\n" "new" "$new_median" "$new_mem"

rc_speedup=$(echo "scale=2; $old_median / $ablation_median" | bc)
dashmap_speedup=$(echo "scale=2; $ablation_median / $new_median" | bc)
total_speedup=$(echo "scale=2; $old_median / $new_median" | bc)

echo ""
echo "RC-only speedup (old → ablation):       ${rc_speedup}x"
echo "DashMap-only speedup (ablation → new):  ${dashmap_speedup}x"
echo "Total speedup (old → new):              ${total_speedup}x"

echo ""
echo "==============================="
echo "correctness check..."
echo "==============================="
diff /tmp/out_old /tmp/out_ablation > /dev/null && echo "old vs ablation: IDENTICAL" || echo "old vs ablation: DIFFER"
diff /tmp/out_ablation /tmp/out_new > /dev/null && echo "ablation vs new: IDENTICAL" || echo "ablation vs new: DIFFER"
diff /tmp/out_old /tmp/out_new > /dev/null && echo "old vs new: IDENTICAL" || echo "old vs new: DIFFER"

echo ""
echo "results saved to $RESULTS_CSV"
