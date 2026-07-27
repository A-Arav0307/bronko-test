import matplotlib.pyplot as plt

SURFACE = "#fcfcfb"
PRIMARY_INK = "#0b0b0b"
SECONDARY_INK = "#52514e"
MUTED_INK = "#898781"
GRID = "#e1e0d9"
BASELINE_LINE = "#c3c2b7"
HIGHLIGHT = "#e34948"
BAR_COLOR = "#5598e7"

# label -> (pattern string, parsnp overlap count, pct of parsnp's 1,403,074 total calls)
DATA = {
    "idx42":       ("####_#____#____#_####", 1013923, 0.723),
    "idx54":       ("###_##____#____##_###", 1012824, 0.722),
    "idx40":       ("#####_____#_____#####", 1012113, 0.721),
    "idx56":       ("###_#_#___#___#_#_###", 1011452, 0.721),
    "idx44":       ("####__#___#___#__####", 1009952, 0.720),
    "idx100":      ("##_##_#___#___#_##_##", 993551, 0.708),
    "default":     ("(no pattern - full density)", 990594, 0.706),
    "idx336":      ("#_#_______#_______#_#", 935347, 0.667),
    "idx216":      ("##________#________##", 918454, 0.655),
    "idx408":      ("#__#______#______#__#", 904344, 0.645),
    "idx28":       ("#___#_____#_____#___#", 900314, 0.642),
    "ska_pattern": ("__________#__________", 742523, 0.529),
}

rows = sorted(DATA.items(), key=lambda kv: -kv[1][2])
labels = [f"{k}: {v[0]}" for k, v in rows]
pcts = [v[2] * 100 for k, v in rows]
best_idx = 0

fig, ax = plt.subplots(figsize=(11, 7))
fig.patch.set_facecolor(SURFACE)
ax.set_facecolor(SURFACE)

colors = [HIGHLIGHT if i == best_idx else BAR_COLOR for i in range(len(rows))]
y_pos = range(len(rows))
bars = ax.barh(y_pos, pcts, color=colors, height=0.65, zorder=3)

ax.set_yticks(y_pos)
ax.set_yticklabels(labels, fontsize=10, family="monospace", color=PRIMARY_INK)
ax.invert_yaxis()

for i, (bar, pct) in enumerate(zip(bars, pcts)):
    ax.text(pct + 0.8, bar.get_y() + bar.get_height() / 2, f"{pct:.1f}%",
            va="center", fontsize=10, color=PRIMARY_INK, fontweight="bold" if i == best_idx else "normal")

ax.set_xlabel("% of parsnp's real-genome variant calls also found by bronko", fontsize=11, color=SECONDARY_INK)
ax.set_title("Which bucket pattern agrees most with parsnp on real genomes?", fontsize=13, color=PRIMARY_INK, pad=14)
ax.set_xlim(0, 85)

ax.grid(True, axis="x", linestyle="--", linewidth=0.7, color=GRID, zorder=0)
for spine in ["top", "right"]:
    ax.spines[spine].set_visible(False)
for spine in ["left", "bottom"]:
    ax.spines[spine].set_color(BASELINE_LINE)
ax.tick_params(axis="both", colors=MUTED_INK, labelsize=9)

plt.tight_layout()
plt.savefig("parsnp_agreement_ranking.png", dpi=150, facecolor=SURFACE)
print("saved parsnp_agreement_ranking.png")
