import csv
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

SURFACE = "#fcfcfb"
PRIMARY_INK = "#0b0b0b"
SECONDARY_INK = "#52514e"
MUTED_INK = "#898781"
GRID = "#e1e0d9"
BASELINE_LINE = "#c3c2b7"
HIGHLIGHT = "#e34948"

BLUE_RAMP = LinearSegmentedColormap.from_list(
    "blue_seq", ["#86b6ef", "#5598e7", "#2a78d6", "#1c5cab", "#0d366b"]
)


def load_means():
    rows = list(csv.DictReader(open("pattern_sweep_means.csv")))
    for r in rows:
        r["time_s"] = float(r["time_s"])
        r["mem_gb"] = float(r["mem_gb"])
        r["precision"] = float(r["precision"])
        r["recall"] = float(r["recall"])
        r["f1"] = float(r["f1"])
        r["match_count"] = int(r["match_count"])
    return rows


def load_old_bronko_mean():
    rows = list(csv.DictReader(open("old_bronko_baseline.csv")))
    n = len(rows)
    time_s = sum(float(r["time_s"]) for r in rows) / n
    mem_gb = sum(float(r["mem_gb"]) for r in rows) / n
    precision = sum(float(r["precision"]) for r in rows) / n
    recall = sum(float(r["recall"]) for r in rows) / n
    f1 = sum(float(r["f1"]) for r in rows) / n
    print(f"old_bronko baseline (n={n} genomes): time={time_s:.2f}s mem={mem_gb:.2f}gb "
          f"precision={precision:.4f} recall={recall:.4f} f1={f1:.4f}")
    return dict(time_s=time_s, mem_gb=mem_gb, precision=precision, recall=recall, f1=f1)


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


def scatter_with_old_bronko(xs, ys, cs, old_x, old_y, xlabel, ylabel, title, fname, cbar_label):
    fig, ax = plt.subplots(figsize=(10, 7))
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)

    sc = ax.scatter(xs, ys, c=cs, cmap=BLUE_RAMP, s=28, alpha=0.85, edgecolors=SURFACE, linewidths=0.4, zorder=3)
    cbar = fig.colorbar(sc, ax=ax)
    cbar.set_label(cbar_label, fontsize=10, color=SECONDARY_INK)
    cbar.ax.tick_params(colors=MUTED_INK, labelsize=8)

    ax.scatter([old_x], [old_y], color=HIGHLIGHT, s=220, marker="o",
               edgecolors=PRIMARY_INK, linewidths=1.5, zorder=5, label="old bronko (pre-optimization, no bucket pattern)")
    ax.annotate("old bronko", xy=(old_x, old_y), xytext=(15, 15), textcoords="offset points",
                fontsize=10, fontweight="bold", color=HIGHLIGHT,
                arrowprops=dict(arrowstyle="-", color=HIGHLIGHT, linewidth=1.2))

    style_axes(ax, xlabel, ylabel, title)
    legend = ax.legend(loc="best", frameon=True, fontsize=9, labelcolor=PRIMARY_INK)
    legend.get_frame().set_facecolor(SURFACE)
    legend.get_frame().set_edgecolor(BASELINE_LINE)

    plt.tight_layout()
    plt.savefig(fname, dpi=150, facecolor=SURFACE)
    print(f"saved {fname}")
    plt.close(fig)


def main():
    means = load_means()
    old = load_old_bronko_mean()

    scatter_with_old_bronko(
        [m["time_s"] for m in means], [m["mem_gb"] for m in means], [m["match_count"] for m in means],
        old["time_s"], old["mem_gb"],
        "Mean runtime (s)", "Mean peak memory (GB)",
        "500-pattern sweep: runtime vs. memory (vs. old bronko)",
        "sweep_runtime_vs_memory_with_old.png", "Number of match positions (#)"
    )

    scatter_with_old_bronko(
        [m["time_s"] for m in means], [m["recall"] for m in means], [m["match_count"] for m in means],
        old["time_s"], old["recall"],
        "Mean runtime (s)", "Mean recall",
        "500-pattern sweep: recall vs. runtime (vs. old bronko)",
        "sweep_recall_vs_runtime_with_old.png", "Number of match positions (#)"
    )

    scatter_with_old_bronko(
        [m["precision"] for m in means], [m["recall"] for m in means], [m["match_count"] for m in means],
        old["precision"], old["recall"],
        "Mean precision", "Mean recall",
        "500-pattern sweep: recall vs. precision (vs. old bronko)",
        "sweep_recall_vs_precision_with_old.png", "Number of match positions (#)"
    )

    scatter_with_old_bronko(
        [m["time_s"] for m in means], [m["mem_gb"] for m in means], [m["f1"] for m in means],
        old["time_s"], old["mem_gb"],
        "Mean runtime (s)", "Mean peak memory (GB)",
        "500-pattern sweep: F1 vs. runtime vs. memory (vs. old bronko)",
        "sweep_f1_vs_runtime_vs_memory_with_old.png", "Mean F1"
    )


if __name__ == "__main__":
    main()
