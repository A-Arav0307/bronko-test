#!/bin/bash
set -e

# multi-server aware launcher. total work is sharded into (NUM_SERVERS x JOBS_PER_SERVER)
# global workers; this invocation launches only the JOBS_PER_SERVER workers belonging to
# SERVER_ID on THIS machine. pattern_sweep_worker.sh doesn't know about servers at all -
# it just gets a global job_id and the global total job count, and shards on that.
#
# usage: ./launch_pattern_sweep.sh <server_id> <num_servers> <jobs_per_server>
#
# today, with one server:      ./launch_pattern_sweep.sh 0 1 10
# later, with 4 servers, run on each machine:
#   server 0: ./launch_pattern_sweep.sh 0 4 10
#   server 1: ./launch_pattern_sweep.sh 1 4 10
#   server 2: ./launch_pattern_sweep.sh 2 4 10
#   server 3: ./launch_pattern_sweep.sh 3 4 10

SERVER_ID=${1:-0}
NUM_SERVERS=${2:-1}
JOBS_PER_SERVER=${3:-10}

TOTAL_JOBS=$((NUM_SERVERS * JOBS_PER_SERVER))
START_JOB=$((SERVER_ID * JOBS_PER_SERVER))
END_JOB=$((START_JOB + JOBS_PER_SERVER - 1))

BENCH_DIR=~/bronko_benchmark/phastsim-run
REPO_DIR=~/bronko_benchmark/bronko-test
LOG_DIR=$BENCH_DIR/pattern_sweep_logs
mkdir -p "$LOG_DIR"

cd $BENCH_DIR

echo "server ${SERVER_ID}/${NUM_SERVERS}: launching global job_ids ${START_JOB}-${END_JOB} (of ${TOTAL_JOBS} total)"
for ((job_id=START_JOB; job_id<=END_JOB; job_id++)); do
    nohup bash "${REPO_DIR}/pattern_sweep_worker.sh" "$job_id" "$TOTAL_JOBS" > "${LOG_DIR}/job${job_id}.log" 2>&1 &
    echo "  started job ${job_id} (pid $!) -> ${LOG_DIR}/job${job_id}.log"
done

# only server 0 runs the completion monitor - it just needs to see the shared
# git repo's results, doesn't matter which physical machine runs it
if [ "$SERVER_ID" -eq 0 ]; then
    echo "launching genome-completion monitor (server 0 only)..."
    nohup python3 "${REPO_DIR}/sweep_progress_monitor.py" > "${LOG_DIR}/monitor.log" 2>&1 &
    echo "  started monitor (pid $!) -> ${LOG_DIR}/monitor.log"
fi

echo ""
echo "server ${SERVER_ID} launched ${JOBS_PER_SERVER} worker jobs (global ids ${START_JOB}-${END_JOB})."
echo "live dashboard (what genome/pattern each job on THIS server is on):"
echo "  bash ${REPO_DIR}/sweep_status.sh ${TOTAL_JOBS}"
echo "  (note: pass the TOTAL job count, ${TOTAL_JOBS}, not just this server's count,"
echo "   so the dashboard checks the right range of job log files)"
echo "watch a single job's raw log: tail -f ${LOG_DIR}/job${START_JOB}.log"
echo "check if still running:       ps aux | grep -E 'pattern_sweep_worker|sweep_progress_monitor'"
