#!/bin/bash
# live status of the pattern sweep - run once, or `watch -n 5 ./sweep_status.sh` for a live dashboard

BENCH_DIR=~/bronko_benchmark/phastsim-run
LOG_DIR=$BENCH_DIR/pattern_sweep_logs
RESULTS_DIR=~/bronko_benchmark/bronko-test/sweep_results
NUM_JOBS=${1:-10}

truncate() {
    local s=$1
    local n=$2
    if [ ${#s} -gt $n ]; then
        echo "${s:0:$n}…"
    else
        echo "$s"
    fi
}

echo "==============================="
echo "per-job current position"
echo "==============================="
printf "%-6s %-10s %-28s %-10s %-24s %s\n" "JOB" "GENOME#" "GENOME ID" "PATTERN#" "PATTERN" "LAST RESULT"
for ((job_id=0; job_id<NUM_JOBS; job_id++)); do
    log="${LOG_DIR}/job${job_id}.log"
    if [ ! -f "$log" ]; then
        printf "%-6s %-10s %-28s %-10s %-24s %s\n" "$job_id" "-" "(no log yet)" "-" "-" "-"
        continue
    fi
    last_line=$(grep "^\[job ${job_id}\] genome" "$log" | tail -1)
    if [ -z "$last_line" ]; then
        printf "%-6s %-10s %-28s %-10s %-24s %s\n" "$job_id" "-" "(starting...)" "-" "-" "-"
        continue
    fi
    genome_num=$(echo "$last_line"    | sed -E 's/^\[job [0-9]+\] genome ([0-9]+\/[0-9]+) \(([^)]+)\) pattern ([0-9]+\/[0-9]+) \[([^]]*)\]: (.*)$/\1/')
    genome_id=$(echo "$last_line"     | sed -E 's/^\[job [0-9]+\] genome ([0-9]+\/[0-9]+) \(([^)]+)\) pattern ([0-9]+\/[0-9]+) \[([^]]*)\]: (.*)$/\2/')
    pattern_num=$(echo "$last_line"   | sed -E 's/^\[job [0-9]+\] genome ([0-9]+\/[0-9]+) \(([^)]+)\) pattern ([0-9]+\/[0-9]+) \[([^]]*)\]: (.*)$/\3/')
    pattern_str=$(echo "$last_line"   | sed -E 's/^\[job [0-9]+\] genome ([0-9]+\/[0-9]+) \(([^)]+)\) pattern ([0-9]+\/[0-9]+) \[([^]]*)\]: (.*)$/\4/')
    metrics=$(echo "$last_line"       | sed -E 's/^\[job [0-9]+\] genome ([0-9]+\/[0-9]+) \(([^)]+)\) pattern ([0-9]+\/[0-9]+) \[([^]]*)\]: (.*)$/\5/')
    printf "%-6s %-10s %-28s %-10s %-24s %s\n" "$job_id" "$genome_num" "$(truncate "$genome_id" 27)" "$pattern_num" "$(truncate "$pattern_str" 23)" "$metrics"
done

echo ""
echo "==============================="
echo "overall progress"
echo "==============================="
if [ -d "$RESULTS_DIR" ]; then
    num_genomes=$(wc -l < "${BENCH_DIR}/genomes_50_manifest.txt" 2>/dev/null || echo "?")
    total_expected=$((num_genomes * 500))
    total_done=$(cat ${RESULTS_DIR}/pattern_sweep_results_job*.csv 2>/dev/null | grep -v "^genome_id" | wc -l)
    echo "total combinations completed: ${total_done} / ${total_expected} (${num_genomes} genomes x 500 patterns)"

    echo ""
    echo "genomes with all 500 patterns done:"
    cat ${RESULTS_DIR}/pattern_sweep_results_job*.csv 2>/dev/null | grep -v "^genome_id" | cut -d, -f1 | sort | uniq -c | awk '$1 >= 500 {print "  " $2 " (" $1 "/500)"}'

    echo ""
    echo "genomes still in progress:"
    cat ${RESULTS_DIR}/pattern_sweep_results_job*.csv 2>/dev/null | grep -v "^genome_id" | cut -d, -f1 | sort | uniq -c | awk '$1 < 500 {print "  " $2 " (" $1 "/500)"}'
else
    echo "no results directory found yet at ${RESULTS_DIR}"
fi
