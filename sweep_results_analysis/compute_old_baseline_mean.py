import glob
import csv

rows = []
for path in glob.glob("old_baseline_results/old_baseline_job*.csv"):
    with open(path) as f:
        rows.extend(csv.DictReader(f))

if not rows:
    print("no results yet")
else:
    n = len(rows)
    mean_time = sum(float(r["time_s"]) for r in rows) / n
    mean_mem = sum(float(r["mem_gb"]) for r in rows) / n
    mean_prec = sum(float(r["precision"]) for r in rows) / n
    mean_recall = sum(float(r["recall"]) for r in rows) / n
    mean_f1 = sum(float(r["f1"]) for r in rows) / n
    print(f"old_bronko baseline, {n}/49 genomes so far:")
    print(f"  mean time:      {mean_time:.2f}s")
    print(f"  mean mem:       {mean_mem:.2f}gb")
    print(f"  mean precision: {mean_prec:.4f}")
    print(f"  mean recall:    {mean_recall:.4f}")
    print(f"  mean f1:        {mean_f1:.4f}")
