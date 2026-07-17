#!/bin/bash
set -e

NUM_JOBS=${1:-10}
BENCH_DIR=~/bronko_benchmark/phastsim-run
REPO_DIR=~/bronko_benchmark/bronko-test
LOG_DIR=$BENCH_DIR/pattern_sweep_logs
mkdir -p "$LOG_DIR"

cd $BENCH_DIR

echo "launching ${NUM_JOBS} background worker jobs..."
for ((job_id=0; job_id<NUM_JOBS; job_id++)); do
    nohup bash pattern_sweep_worker.sh "$job_id" "$NUM_JOBS" > "${LOG_DIR}/job${job_id}.log" 2>&1 &
    echo "  started job ${job_id} (pid $!) -> ${LOG_DIR}/job${job_id}.log"
done

echo "launching genome-completion monitor..."
nohup python3 "${REPO_DIR}/sweep_progress_monitor.py" > "${LOG_DIR}/monitor.log" 2>&1 &
echo "  started monitor (pid $!) -> ${LOG_DIR}/monitor.log"

echo ""
echo "all ${NUM_JOBS} worker jobs + monitor launched in background."
echo "live dashboard (what genome/pattern each job is on): bash sweep_status.sh"
echo "  or refresh automatically:                          watch -n 5 bash sweep_status.sh"
echo "watch a single job's raw log:                        tail -f ${LOG_DIR}/job0.log"
echo "watch the completion monitor:                        tail -f ${LOG_DIR}/monitor.log"
echo "check if still running:                              ps aux | grep -E 'pattern_sweep_worker|sweep_progress_monitor'"
