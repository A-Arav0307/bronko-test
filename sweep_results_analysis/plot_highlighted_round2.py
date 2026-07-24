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

BLUE_RAMP = LinearSegmentedColormap.from_list("blue_seq", ["#86b6ef", "#5598e7", "#2a78d6", "#1c5cab", "#0d366b"])

# idx -> (manual offset dx,dy in points, human label) - top 5 by recall-weighted tradeoff
HIGHLIGHTS = {
    "500": ((-160, -60), "#1 best tradeoff - ska_pattern"),
    "8":   ((-160, 60), "#2"),
    "37":  ((40, -110), "#4"),
    "3":   ((140, 40), "#3 - highest recall of the 5"),
    "36":  ((140, -60), "#5"),
}

def truncate(p, n=18):
    return p if len(p) <= n else p[:n] + "…"

rows = list(csv.DictReader(open("pattern_sweep_means.csv")))
for r in rows:
    r["time_s"] = float(r["time_s"])
    r["mem_gb"] = float(r["mem_gb"])
    r["recall"] = float(r["recall"])
    r["match_count"] = r["pattern"].count("#")

fig, ax = plt.subplots(figsize=(13, 8.5))
fig.patch.set_facecolor(SURFACE)
ax.set_facecolor(SURFACE)

others = [r for r in rows if r["pattern_idx"] not in HIGHLIGHTS]
highlighted = [r for r in rows if r["pattern_idx"] in HIGHLIGHTS]

sc = ax.scatter([r["time_s"] for r in others], [r["recall"] for r in others],
                c=[r["match_count"] for r in others], cmap=BLUE_RAMP, s=22, alpha=0.55,
                edgecolors=SURFACE, linewidths=0.3, zorder=2)
cbar = fig.colorbar(sc, ax=ax)
cbar.set_label("Number of match positions (#)", fontsize=10, color=SECONDARY_INK)
cbar.ax.tick_params(colors=MUTED_INK, labelsize=8)

ax.scatter([r["time_s"] for r in highlighted], [r["recall"] for r in highlighted],
           color=HIGHLIGHT, s=170, edgecolors=SURFACE, linewidths=1.5, zorder=4,
           label="Top 5 by recall-weighted tradeoff")

for r in highlighted:
    (dx, dy), tag = HIGHLIGHTS[r["pattern_idx"]]
    label = f"{tag}\n{truncate(r['pattern'])}\nrecall={r['recall']:.3f}  {r['time_s']:.1f}s  {r['mem_gb']:.1f}gb"
    ax.annotate(label, xy=(r["time_s"], r["recall"]), xytext=(dx, dy), textcoords="offset points",
                fontsize=9, family="monospace", color=PRIMARY_INK,
                ha="left" if dx > 0 else "right", va="center",
                bbox=dict(boxstyle="round,pad=0.3", facecolor=SURFACE, edgecolor=HIGHLIGHT, linewidth=0.8),
                arrowprops=dict(arrowstyle="-", color=HIGHLIGHT, linewidth=0.8, shrinkA=0, shrinkB=8))

ax.set_xlabel("Mean runtime (s)", fontsize=11, color=SECONDARY_INK)
ax.set_ylabel("Mean recall", fontsize=11, color=SECONDARY_INK)
ax.set_title("Round 2, 501-pattern sweep: recall vs. runtime (top 5 tradeoff patterns highlighted)", fontsize=13, color=PRIMARY_INK, pad=14)

ax.grid(True, linestyle="--", linewidth=0.7, color=GRID, zorder=0)
for spine in ["top", "right"]:
    ax.spines[spine].set_visible(False)
for spine in ["left", "bottom"]:
    ax.spines[spine].set_color(BASELINE_LINE)
ax.tick_params(axis="both", colors=MUTED_INK, labelsize=9)

legend = ax.legend(loc="lower right", frameon=True, fontsize=10, labelcolor=PRIMARY_INK)
legend.get_frame().set_facecolor(SURFACE)
legend.get_frame().set_edgecolor(BASELINE_LINE)

ax.margins(x=0.3, y=0.3)
plt.tight_layout()
plt.savefig("sweep_recall_vs_runtime_highlighted_round2.png", dpi=150, facecolor=SURFACE)
print("saved sweep_recall_vs_runtime_highlighted_round2.png")
