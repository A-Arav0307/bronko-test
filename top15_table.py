import csv

rows = list(csv.DictReader(open("pattern_sweep_means.csv")))
print("columns found:", list(rows[0].keys()))

has_score = "score" in rows[0]

for r in rows:
    r["time_s"] = float(r["time_s"])
    r["mem_gb"] = float(r["mem_gb"])
    r["precision"] = float(r["precision"])
    r["recall"] = float(r["recall"])
    r["f1"] = float(r["f1"])
    if has_score:
        r["score"] = float(r["score"])

sort_key = "score" if has_score else "f1"
rows.sort(key=lambda r: r[sort_key], reverse=True)

top15 = rows[:15]

idx_col = "idx" if "idx" in rows[0] else ("pattern_id" if "pattern_id" in rows[0] else None)
pattern_col = "pattern" if "pattern" in rows[0] else None

print(f"\nsorted by: {sort_key} (has_score={has_score})\n")
header = f"{'idx':>5} | {'pattern':40} | {'score' if has_score else 'f1(as score)':>12} | {'precision':>9} | {'recall':>7} | {'F1':>6} | {'time':>7} | {'mem':>7}"
print(header)
print("-" * len(header))
for r in top15:
    idx = r[idx_col] if idx_col else "?"
    pattern = r[pattern_col] if pattern_col else "?"
    score_val = r["score"] if has_score else r["f1"]
    print(f"{idx:>5} | {pattern:40} | {score_val:>12.4f} | {r['precision']:>9.4f} | {r['recall']:>7.4f} | {r['f1']:>6.4f} | {r['time_s']:>6.2f}s | {r['mem_gb']:>5.2f}gb")
