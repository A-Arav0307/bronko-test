import os
import pandas as pd

BENCH_DIR = os.path.expanduser("~/bronko_benchmark")

results = pd.read_csv(f"{BENCH_DIR}/results.csv")
lengths = pd.read_csv(f"{BENCH_DIR}/genome_lengths.csv")

sizes = ["1M", "2.5M", "4M", "7M", "12M"]
results = results[results["label"].isin(sizes)]
results = results.drop_duplicates(subset=["label", "version"], keep="last")

df = results.merge(lengths, on="label").sort_values(["length_bp", "version"])
df = df[["label", "version", "length_bp", "time_s", "peak_memory_gb"]]

out_path = f"{BENCH_DIR}/sweep_summary.csv"
df.to_csv(out_path, index=False)
print(f"saved {out_path}")
print(df.to_string(index=False))
