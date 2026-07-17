import glob
import csv
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.cm as cm

SURFACE = "#fcfcfb"
PRIMARY_INK = "#0b0b0b"
SECONDARY_INK = "#52514e"
MUTED_INK = "#898781"
GRID = "#e1e0d9"
BASELINE_LINE = "#c3c2b7"

# validated sequential blue ramp from the project's dataviz palette (steps 250-700,
# staying within the 2:1+ contrast band on the light surface)
BLUE_RAMP = LinearSegmentedColormap.from_list(
    "blue_seq", ["#86b6ef", "#5598e7", "#2a78d6", "#1c5cab", "#0d366b"]
)


def load_results():
    rows = []
    for path in glob.glob("pattern_sweep_results_job*.csv"):
        with open(path) as f:
            reader = csv.DictReader(f)
            for r in reader:
                rows.append(r)
    return rows


def aggregate(rows):
    by_pattern = {}
    for r in rows:
        idx = r["pattern_idx"]
        by_pattern.setdefault(idx, {"pattern": r["pattern"], "rows": []})
        by_pattern[idx]["rows"].append(r)

    means = []
    for idx, d in by_pattern.items():
        rs = d["rows"]
        n = len(rs)
        pattern = d["pattern"]
        density = pattern.count("#") / len(pattern)
        mean_time = sum(float(x["time_s"]) for x in rs) / n
        mean_mem = sum(float(x["mem_gb"]) for x in rs) / n
        mean_precision = sum(float(x["precision"]) for x in rs) / n
        mean_recall = sum(float(x["recall"]) for x in rs) / n
        mean_f1 = sum(float(x["f1"]) for x in rs) / n
        means.append(dict(pattern_idx=idx, pattern=pattern, density=density, n_genomes=n,
                           time_s=mean_time, mem_gb=mean_mem, precision=mean_precision,
                           recall=mean_recall, f1=mean_f1))
    means.sort(key=lambda x: x["density"])
    return means


def write_csvs(rows, means):
    with open("pattern_sweep_all_results.csv", "w", newline="") as f:
        if rows:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
    with open("pattern_sweep_means.csv", "w", newline="") as f:
        if means:
            writer = csv.DictWriter(f, fieldnames=means[0].keys())
            writer.writeheader()
            writer.writerows(means)
    print(f"wrote pattern_sweep_all_results.csv ({len(rows)} rows) and pattern_sweep_means.csv ({len(means)} patterns)")


def style_axes(ax, xlabel, ylabel, title):
    ax.set_xlabel(xlabel, fontsize=11, color=SECONDARY_INK)
    ax.set_ylabel(ylabel, fontsize=11, color=SECONDARY_INK)
    ax.set_title(title, fontsize=13, color=PRIMARY_INK, pad=14)
    ax.grid(True, linestyle="--", linewidth=0.7, color=GRID, zorder=0)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    for spine in ["left", "bottom"]:
        ax.spines[spine].set_color(BASELINE_LINE)
    ax.tick_params(axis="both", colors=MUTED_INK, labelsize=9)


def plot_runtime_vs_memory(means):
    fig, ax = plt.subplots(figsize=(10, 7))
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)

    xs = [m["time_s"] for m in means]
    ys = [m["mem_gb"] for m in means]
    cs = [m["density"] for m in means]

    sc = ax.scatter(xs, ys, c=cs, cmap=BLUE_RAMP, s=28, alpha=0.85, edgecolors=SURFACE, linewidths=0.4, zorder=3)
    cbar = fig.colorbar(sc, ax=ax)
    cbar.set_label("Bucket keep density", fontsize=10, color=SECONDARY_INK)
    cbar.ax.tick_params(colors=MUTED_INK, labelsize=8)

    style_axes(ax, "Mean runtime (s)", "Mean peak memory (GB)",
               "500-pattern sweep: mean runtime vs. mean memory (across 50 genomes)")
    plt.tight_layout()
    plt.savefig("sweep_runtime_vs_memory.png", dpi=150, facecolor=SURFACE)
    print("saved sweep_runtime_vs_memory.png")


def plot_f1_vs_runtime_vs_memory(means):
    fig, ax = plt.subplots(figsize=(10, 7))
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)

    xs = [m["time_s"] for m in means]
    ys = [m["mem_gb"] for m in means]
    cs = [m["f1"] for m in means]

    sc = ax.scatter(xs, ys, c=cs, cmap=BLUE_RAMP, s=28, alpha=0.85, edgecolors=SURFACE, linewidths=0.4, zorder=3)
    cbar = fig.colorbar(sc, ax=ax)
    cbar.set_label("Mean F1", fontsize=10, color=SECONDARY_INK)
    cbar.ax.tick_params(colors=MUTED_INK, labelsize=8)

    style_axes(ax, "Mean runtime (s)", "Mean peak memory (GB)",
               "500-pattern sweep: F1 vs. runtime vs. memory (color = mean F1)")
    plt.tight_layout()
    plt.savefig("sweep_f1_vs_runtime_vs_memory.png", dpi=150, facecolor=SURFACE)
    print("saved sweep_f1_vs_runtime_vs_memory.png")


def plot_recall_vs_precision(means):
    fig, ax = plt.subplots(figsize=(10, 7))
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)

    xs = [m["precision"] for m in means]
    ys = [m["recall"] for m in means]
    cs = [m["density"] for m in means]

    sc = ax.scatter(xs, ys, c=cs, cmap=BLUE_RAMP, s=28, alpha=0.85, edgecolors=SURFACE, linewidths=0.4, zorder=3)
    cbar = fig.colorbar(sc, ax=ax)
    cbar.set_label("Bucket keep density", fontsize=10, color=SECONDARY_INK)
    cbar.ax.tick_params(colors=MUTED_INK, labelsize=8)

    style_axes(ax, "Mean precision", "Mean recall",
               "500-pattern sweep: mean recall vs. mean precision (across 50 genomes)")
    plt.tight_layout()
    plt.savefig("sweep_recall_vs_precision.png", dpi=150, facecolor=SURFACE)
    print("saved sweep_recall_vs_precision.png")


def main():
    rows = load_results()
    if not rows:
        print("no results found yet - has the sweep started?")
        return
    means = aggregate(rows)
    write_csvs(rows, means)

    completeness = [m["n_genomes"] for m in means]
    print(f"patterns with data so far: {len(means)}/500, genomes completed per pattern: min={min(completeness)} max={max(completeness)} (of 50)")

    plot_runtime_vs_memory(means)
    plot_f1_vs_runtime_vs_memory(means)
    plot_recall_vs_precision(means)


if __name__ == "__main__":
    main()
