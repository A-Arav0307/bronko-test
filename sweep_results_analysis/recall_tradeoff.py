import csv

MIN_GENOMES = 4

rows = list(csv.DictReader(open("pattern_sweep_means.csv")))
for r in rows:
    r["time_s"] = float(r["time_s"])
    r["mem_gb"] = float(r["mem_gb"])
    r["recall"] = float(r["recall"])
    r["n_genomes"] = int(r["n_genomes"])

before = len(rows)
rows = [r for r in rows if r["n_genomes"] >= MIN_GENOMES]
print(f"filtered to patterns with n_genomes >= {MIN_GENOMES}: {len(rows)} of {before} patterns\n")

print("=== top 10 by raw recall alone ===\n")
by_recall = sorted(rows, key=lambda r: -r["recall"])
for r in by_recall[:10]:
    print(f"  idx={r['pattern_idx']:>4} n_genomes={r['n_genomes']:>3} recall={r['recall']:.4f} time={r['time_s']:>6.2f}s mem={r['mem_gb']:>5.2f}gb  pattern={r['pattern'][:30]}")

def norm(vals, higher_is_better):
    lo, hi = min(vals), max(vals)
    span = hi - lo if hi != lo else 1
    if higher_is_better:
        return [(v - lo) / span for v in vals]
    else:
        return [(hi - v) / span for v in vals]

times = norm([r["time_s"] for r in rows], higher_is_better=False)
mems = norm([r["mem_gb"] for r in rows], higher_is_better=False)
recs = norm([r["recall"] for r in rows], higher_is_better=True)

for i, r in enumerate(rows):
    r["tradeoff_score"] = (recs[i] * 2 + times[i] + mems[i]) / 4

rows.sort(key=lambda r: -r["tradeoff_score"])
print(f"\n=== top 5 by recall-weighted tradeoff (recall counts 2x vs time/mem) ===\n")
for r in rows[:5]:
    print(f"  idx={r['pattern_idx']:>4} n_genomes={r['n_genomes']:>3} score={r['tradeoff_score']:.3f} recall={r['recall']:.4f} time={r['time_s']:>6.2f}s mem={r['mem_gb']:>5.2f}gb  pattern={r['pattern'][:30]}")
