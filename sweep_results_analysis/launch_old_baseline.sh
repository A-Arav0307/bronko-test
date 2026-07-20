#!/bin/bash
set -e

NUM_JOBS=${1:-10}
BENCH_DIR=~/bronko_benchmark/phastsim-run
REPO_DIR=~/bronko_benchmark/bronko-test
LOG_DIR=$BENCH_DIR/old_baseline_logs
mkdir -p "$LOG_DIR"

cd $BENCH_DIR

echo "launching ${NUM_JOBS} old_bronko baseline jobs..."
for ((job_id=0; job_id<NUM_JOBS; job_id++)); do
    nohup bash "${REPO_DIR}/sweep_results_analysis/old_bronko_baseline_worker.sh" "$job_id" "$NUM_JOBS" > "${LOG_DIR}/job${job_id}.log" 2>&1 &
    echo "  started job ${job_id} (pid $!) -> ${LOG_DIR}/job${job_id}.log"
done

echo ""
echo "check progress: cat ${REPO_DIR}/old_baseline_results/old_baseline_job*.csv | grep -v genome_id | wc -l   (out of 49)"
echo "watch a job live: tail -f ${LOG_DIR}/job0.log"
