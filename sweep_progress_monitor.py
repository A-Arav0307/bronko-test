import time
import glob
import subprocess
import csv
import os

REPO_DIR = os.path.expanduser("~/bronko_benchmark/bronko-test")
RESULTS_DIR = os.path.join(REPO_DIR, "sweep_results")
STATE_FILE = os.path.join(RESULTS_DIR, ".genomes_pushed.txt")
NUM_PATTERNS = 500
CHECK_INTERVAL = 60  # seconds


def load_pushed():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return set(line.strip() for line in f if line.strip())
    return set()


def save_pushed(pushed):
    with open(STATE_FILE, "w") as f:
        f.write("\n".join(sorted(pushed)) + "\n")


def count_patterns_per_genome():
    counts = {}
    for path in glob.glob(os.path.join(RESULTS_DIR, "pattern_sweep_results_job*.csv")):
        with open(path) as f:
            reader = csv.DictReader(f)
            for row in reader:
                g = row["genome_id"]
                counts[g] = counts.get(g, 0) + 1
    return counts


def git_push_milestone(newly_completed):
    os.chdir(REPO_DIR)
    subprocess.run(["git", "add", "sweep_results/"], check=False)
    msg = f"milestone: {len(newly_completed)} genome(s) fully completed all {NUM_PATTERNS} patterns: {', '.join(sorted(newly_completed))}"
    subprocess.run(["git", "commit", "-m", msg], check=False)
    subprocess.run(["git", "pull", "--rebase", "origin", "500-pattern-sweep"], check=False)
    result = subprocess.run(["git", "push", "origin", "500-pattern-sweep"], check=False)
    if result.returncode == 0:
        print(f"pushed milestone: {sorted(newly_completed)}")
    else:
        print(f"WARNING: milestone push failed for {sorted(newly_completed)}, will retry next cycle")


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    pushed = load_pushed()
    print(f"monitoring genome completion, already-pushed: {len(pushed)}")
    while True:
        counts = count_patterns_per_genome()
        complete_now = {g for g, c in counts.items() if c >= NUM_PATTERNS}
        newly_completed = complete_now - pushed

        if newly_completed:
            git_push_milestone(newly_completed)
            pushed |= newly_completed
            save_pushed(pushed)

        print(f"[monitor] {len(complete_now)}/50 genomes fully complete, {len(counts)} genomes with any data so far")

        if len(complete_now) >= 50:
            print("[monitor] all 50 genomes complete, exiting monitor")
            break

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
