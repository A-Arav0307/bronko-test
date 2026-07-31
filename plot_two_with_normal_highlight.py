import csv
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

SURFACE = "#fcfcfb"
PRIMARY_INK = "#0b0b0b"
SECONDARY_INK = "#52514e"
MUTED_INK = "#898781"
GRID = "#e1e0d9"
BASELINE_LINE = "#c3c2b7"
ORANGE = "#e8821e"
BLUE = "#2467c2"

RED_RAMP = LinearSegmentedColormap.from_list(
    "red_seq", ["#f3a6a1", "#e8746c", "#d9463c", "#b8261c", "#7a1510"]
)

SKA_PATTERN_STR = "__________#__________"


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


def find_ska_pattern(rows):
    pattern_col = "pattern" if rows and "pattern" in rows[0] else None
    if pattern_col:
        exact = [r for r in rows if r[pattern_col] == SKA_PATTERN_STR]
        if len(exact) == 1:
            print(f"found split k-mer pattern by exact pattern-string match: {exact[0]}")
            return exact[0]
        if len(exact) > 1:
            print(f"WARNING: {len(exact)} rows matched the split k-mer pattern string exactly, using the first one")
            return exact[0]

    single_hash = [r for r in rows if r.get(pattern_col, "").count("#") == 1] if pattern_col else []
    if len(single_hash) == 1:
        print(f"found split k-mer pattern by single-# fallback match: {single_hash[0]}")
        return single_hash[0]

    raise ValueError(
        f"could not uniquely identify split k-mer pattern row (pattern_col={pattern_col}, "
        f"exact_matches=0, single_hash_matches={len(single_hash)}) - check pattern_sweep_means.csv columns"
    )


def load_normal_mean():
    rows = list(csv.DictReader(open("normal_baseline.csv")))
    n = len(rows)
    time_s = sum(float(r["time_s"]) for r in rows) / n
    mem_gb = sum(float(r["mem_gb"]) for r in rows) / n
    precision = sum(float(r["precision"]) for r in rows) / n
    recall = sum(float(r["recall"]) for r in rows) / n
    f1 = sum(float(r["f1"]) for r in rows) / n
    print(f"normal baseline (bucket-stride=1, n={n} genomes): time={time_s:.2f}s mem={mem_gb:.2f}gb "
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


def scatter_with_highlights(xs, ys, cs, highlights, xlabel, ylabel, title, fname, cbar_label,
                             vmin=None, vmax=None, log_x=False, log_y=False):
    """highlights: list of dicts with keys x, y, label, color"""
    fig, ax = plt.subplots(figsize=(10, 7))
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)

    if vmin is None:
        vmin = min(cs)
    if vmax is None:
        vmax = max(cs)

    sc = ax.scatter(xs, ys, c=cs, cmap=RED_RAMP, s=28, alpha=0.85, edgecolors=SURFACE, linewidths=0.4, zorder=3,
                     vmin=vmin, vmax=vmax)
    cbar = fig.colorbar(sc, ax=ax)
    cbar.set_label(cbar_label, fontsize=10, color=SECONDARY_INK)
    cbar.ax.tick_params(colors=MUTED_INK, labelsize=8)

    for i, h in enumerate(highlights):
        offset = (15, 15 + 25 * i)
        ax.scatter([h["x"]], [h["y"]], color=h["color"], s=240, marker="o",
                   edgecolors=h["color"], linewidths=2.5, zorder=5)
        ax.annotate(h["label"], xy=(h["x"], h["y"]), xytext=offset, textcoords="offset points",
                    fontsize=11, fontweight="bold", color=h["color"],
                    arrowprops=dict(arrowstyle="-", color=h["color"], linewidth=1.2))

    style_axes(ax, xlabel, ylabel, title)
    if log_x:
        ax.set_xscale("log")
    if log_y:
        ax.set_yscale("log")

    plt.tight_layout()
    plt.savefig(fname, dpi=150, facecolor=SURFACE)
    print(f"saved {fname}")
    plt.close(fig)


def main():
    means = load_means()
    normal = load_normal_mean()
    ska = find_ska_pattern(means)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    scatter_with_highlights(
        [m["precision"] for m in means], [m["recall"] for m in means], [m["match_count"] for m in means],
        [
            {"x": normal["precision"], "y": normal["recall"], "label": "default", "color": ORANGE},
            {"x": ska["precision"], "y": ska["recall"], "label": "split k-mer", "color": BLUE},
        ],
        "Mean precision", "Mean recall",
        "500-pattern sweep: recall vs. precision (vs. default bronko)",
        f"sweep_recall_vs_precision_{ts}.png", "Number of match positions (#)"
    )

    scatter_with_highlights(
        [m["time_s"] for m in means], [m["mem_gb"] for m in means], [m["f1"] for m in means],
        [
            {"x": normal["time_s"], "y": normal["mem_gb"], "label": "default", "color": ORANGE},
            {"x": ska["time_s"], "y": ska["mem_gb"], "label": "split k-mer", "color": BLUE},
        ],
        "Mean runtime (s)", "Mean peak memory (GB)",
        "500-pattern sweep: F1 vs. runtime vs. memory (vs. default bronko)",
        f"sweep_f1_vs_runtime_vs_memory_{ts}.png", "Mean F1",
        log_x=True, log_y=True
    )


if __name__ == "__main__":
    main()
