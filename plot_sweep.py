import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
from scipy.interpolate import PchipInterpolator

df = pd.read_csv("/Users/aaravgupta/Documents/bronko/sweep_summary.csv")

VERSIONS = ["old", "threaded", "stride2"]
LABELS = {"old": "original bronko", "threaded": "threaded (locking fix)", "stride2": "stride (current)"}
COLORS = {"old": "#2a78d6", "threaded": "#1baf7a", "stride2": "#eda100"}

SURFACE = "#fcfcfb"
PRIMARY_INK = "#0b0b0b"
SECONDARY_INK = "#52514e"
MUTED_INK = "#898781"
GRID = "#e1e0d9"
BASELINE = "#c3c2b7"

def bp_formatter(x, _pos):
    if x >= 1_000_000:
        v = x / 1_000_000
        return f"{v:.0f}M" if v == int(v) else f"{v:.1f}M"
    return f"{x/1000:.0f}K"

def plot_metric(col, ylabel, title, fname, legend_loc):
    fig, ax = plt.subplots(figsize=(9, 5.5))
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)

    for version in VERSIONS:
        sub = df[df["version"] == version].sort_values("length_bp")
        x = sub["length_bp"].to_numpy()
        y = sub[col].to_numpy()

        x_smooth = np.linspace(x.min(), x.max(), 300)
        y_smooth = PchipInterpolator(x, y)(x_smooth)

        ax.plot(x_smooth, y_smooth, "-", color=COLORS[version], linewidth=2,
                zorder=2, label=LABELS[version])
        ax.scatter(x, y, color=COLORS[version], s=64, zorder=3,
                   edgecolors=SURFACE, linewidths=1.5)

    ax.set_xlabel("Genome length (bp)", fontsize=11, color=SECONDARY_INK)
    ax.set_ylabel(ylabel, fontsize=11, color=SECONDARY_INK)
    ax.set_title(title, fontsize=13, color=PRIMARY_INK, pad=14)

    ax.xaxis.set_major_formatter(mticker.FuncFormatter(bp_formatter))
    ax.set_xticks(sorted(df["length_bp"].unique()))
    ax.tick_params(axis="both", colors=MUTED_INK, labelsize=9)

    ax.grid(True, axis="y", linestyle="--", linewidth=0.7, color=GRID, zorder=0)
    ax.grid(False, axis="x")
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    for spine in ["left", "bottom"]:
        ax.spines[spine].set_color(BASELINE)

    legend = ax.legend(loc=legend_loc, frameon=True, fontsize=10, labelcolor=PRIMARY_INK)
    legend.get_frame().set_facecolor(SURFACE)
    legend.get_frame().set_edgecolor(BASELINE)

    ax.set_ylim(bottom=0)
    ax.margins(x=0.08)

    plt.tight_layout()
    plt.savefig(f"/Users/aaravgupta/Documents/bronko/{fname}", dpi=150, facecolor=SURFACE)
    print(f"saved {fname}")

plot_metric("time_s", "Runtime (s)", "bronko runtime vs. genome length",
            "runtime_vs_length.png", legend_loc="upper left")
plot_metric("peak_memory_gb", "Peak memory (GB)", "bronko peak memory vs. genome length",
            "memory_vs_length.png", legend_loc="upper left")
