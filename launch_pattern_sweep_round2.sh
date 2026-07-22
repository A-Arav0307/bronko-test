#!/bin/bash
set -e

# same sharding scheme as launch_pattern_sweep.sh, pointed at round 2's data/results.
# usage: ./launch_pattern_sweep_round2.sh <server_id> <num_servers> <jobs_per_server>
# today, with one server: ./launch_pattern_sweep_round2.sh 0 1 10

SERVER_ID=${1:-0}
NUM_SERVERS=${2:-1}
JOBS_PER_SERVER=${3:-10}

TOTAL_JOBS=$((NUM_SERVERS * JOBS_PER_SERVER))
START_JOB=$((SERVER_ID * JOBS_PER_SERVER))
END_JOB=$((START_JOB + JOBS_PER_SERVER - 1))

BENCH_DIR=~/bronko_benchmark/phastsim-run-round2
REPO_DIR=~/bronko_benchmark/bronko-test
LOG_DIR=$BENCH_DIR/pattern_sweep_logs
mkdir -p "$LOG_DIR"

cd $BENCH_DIR

echo "server ${SERVER_ID}/${NUM_SERVERS}: launching global job_ids ${START_JOB}-${END_JOB} (of ${TOTAL_JOBS} total)"
for ((job_id=START_JOB; job_id<=END_JOB; job_id++)); do
    nohup bash "${REPO_DIR}/pattern_sweep_worker_round2.sh" "$job_id" "$TOTAL_JOBS" > "${LOG_DIR}/job${job_id}.log" 2>&1 &
    echo "  started job ${job_id} (pid $!) -> ${LOG_DIR}/job${job_id}.log"
done

if [ "$SERVER_ID" -eq 0 ]; then
    echo "launching genome-completion monitor (server 0 only)..."
    nohup python3 "${REPO_DIR}/sweep_progress_monitor_round2.py" > "${LOG_DIR}/monitor.log" 2>&1 &
    echo "  started monitor (pid $!) -> ${LOG_DIR}/monitor.log"
fi

echo ""
echo "server ${SERVER_ID} launched ${JOBS_PER_SERVER} worker jobs (global ids ${START_JOB}-${END_JOB})."
echo "live dashboard: bash ${REPO_DIR}/sweep_status_round2.sh ${TOTAL_JOBS}"
echo "watch a single job's raw log: tail -f ${LOG_DIR}/job${START_JOB}.log"
echo "check if still running:       ps aux | grep -E 'pattern_sweep_worker_round2|sweep_progress_monitor_round2'"
