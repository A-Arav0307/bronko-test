import os
import pandas as pd
import matplotlib.pyplot as plt

BENCH_DIR = os.path.expanduser("~/bronko_benchmark")

results = pd.read_csv(f"{BENCH_DIR}/results.csv")
lengths = pd.read_csv(f"{BENCH_DIR}/genome_lengths.csv")

sizes = ["1M", "2.5M", "4M", "7M", "12M"]
results = results[results["label"].isin(sizes)]
results = results.drop_duplicates(subset=["label", "version"], keep="last")

df = results.merge(lengths, on="label").sort_values("length_bp")

versions = {"old": "original bronko", "threaded": "threaded (locking removed)", "stride2": "stride (current)"}
colors = {"old": "steelblue", "threaded": "seagreen", "stride2": "tomato"}

def plot_metric(col, ylabel, title, fname):
    fig, ax = plt.subplots(figsize=(9, 5))
    for version, label in versions.items():
        sub = df[df["version"] == version].sort_values("length_bp")
        ax.plot(sub["length_bp"], sub[col], "-o", color=colors[version], label=label, linewidth=2)
    ax.set_xlabel("Genome length (bp)")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.35)
    plt.tight_layout()
    plt.savefig(f"{BENCH_DIR}/{fname}", dpi=150)
    print(f"saved {fname}")

plot_metric("time_s", "Runtime (s)", "bronko runtime vs genome length", "runtime_vs_length.png")
plot_metric("peak_memory_gb", "Peak memory (GB)", "bronko memory vs genome length", "memory_vs_length.png")
