import time
import glob
import csv
import os

REPO_DIR = os.path.expanduser("~/bronko_benchmark/bronko-test")
BENCH_DIR = os.path.expanduser("~/bronko_benchmark/phastsim-run")
RESULTS_DIR = os.path.join(REPO_DIR, "sweep_results")
STATE_FILE = os.path.join(RESULTS_DIR, ".genomes_seen_complete.txt")
MANIFEST = os.path.join(BENCH_DIR, "genomes_50_manifest.txt")
NUM_PATTERNS = 500
CHECK_INTERVAL = 60  # seconds


def total_genome_count():
    with open(MANIFEST) as f:
        return len([line for line in f if line.strip()])


def load_seen():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return set(line.strip() for line in f if line.strip())
    return set()


def save_seen(seen):
    with open(STATE_FILE, "w") as f:
        f.write("\n".join(sorted(seen)) + "\n")


def count_patterns_per_genome():
    counts = {}
    for path in glob.glob(os.path.join(RESULTS_DIR, "pattern_sweep_results_job*.csv")):
        with open(path) as f:
            reader = csv.DictReader(f)
            for row in reader:
                g = row["genome_id"]
                counts[g] = counts.get(g, 0) + 1
    return counts


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    num_genomes = total_genome_count()
    seen = load_seen()
    print(f"monitoring genome completion ({num_genomes} genomes total), already logged complete: {len(seen)}")
    while True:
        counts = count_patterns_per_genome()
        complete_now = {g for g, c in counts.items() if c >= NUM_PATTERNS}
        newly_completed = complete_now - seen

        if newly_completed:
            print(f"[monitor] newly complete: {sorted(newly_completed)}")
            seen |= newly_completed
            save_seen(seen)

        print(f"[monitor] {len(complete_now)}/{num_genomes} genomes fully complete, {len(counts)} genomes with any data so far")

        if len(complete_now) >= num_genomes:
            print(f"[monitor] all {num_genomes} genomes complete, exiting monitor")
            break

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
