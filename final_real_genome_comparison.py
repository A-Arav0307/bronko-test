import csv
import os
import matplotlib.pyplot as plt
from upsetplot import UpSet, from_contents

PARSNP_VCF = os.path.expanduser("~/bronko_benchmark/phastsim-run-round2/parsnp-out/parsnp_variants.vcf")

# label -> (file suffix, real pattern string / description)
CONFIGS = {
    "default (bucket-stride=2)": ("default", "#_#_#_#_#_#_#_#_#_#_#"),
    "full density (bucket-stride=1)": ("true_full_density", "#####################"),
    "ska_pattern": ("ska_pattern", "__________#__________"),
    "idx336": ("idx336", "#_#_______#_______#_#"),
    "idx408": ("idx408", "#__#______#______#__#"),
    "idx216": ("idx216", "##________#________##"),
    "idx28": ("idx28", "#___#_____#_____#___#"),
    "idx40": ("idx40", "#####_____#_____#####"),
    "idx42": ("idx42", "####_#____#____#_####"),
    "idx44": ("idx44", "####__#___#___#__####"),
    "idx56": ("idx56", "###_#_#___#___#_#_###"),
    "idx54": ("idx54", "###_##____#____##_###"),
    "idx100": ("idx100", "##_##_#___#___#_##_##"),
}

SURFACE = "#fcfcfb"
PRIMARY_INK = "#0b0b0b"
SECONDARY_INK = "#52514e"
MUTED_INK = "#898781"
GRID = "#e1e0d9"
BASELINE_LINE = "#c3c2b7"
HIGHLIGHT = "#e34948"
BAR_COLOR = "#5598e7"


def load_parsnp_set(path):
    variants = set()
    with open(path) as f:
        genome_cols = None
        for line in f:
            if line.startswith("##"):
                continue
            if line.startswith("#CHROM"):
                genome_cols = line.rstrip("\n").split("\t")[9:]
                continue
            fields = line.rstrip("\n").split("\t")
            pos, alt = fields[1], fields[4].upper()
            for genome_id, gt in zip(genome_cols, fields[9:]):
                if genome_id.endswith(".ref"):
                    continue
                if gt.strip() == "1":
                    variants.add((genome_id, pos, alt))
    return variants


def load_bronko_set(path):
    variants = set()
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            variants.add((row["genome_id"], row["pos"], row["alt"]))
    return variants


def main():
    print("loading parsnp...")
    parsnp_set = load_parsnp_set(PARSNP_VCF)
    print(f"  parsnp: {len(parsnp_set)} variants")

    contents = {}
    ranking_rows = []
    for label, (suffix, pattern) in CONFIGS.items():
        path = f"variants_{suffix}.csv"
        s = load_bronko_set(path)
        contents[label] = s
        overlap = len(s & parsnp_set)
        pct = overlap / len(parsnp_set)
        ranking_rows.append((label, pattern, len(s), overlap, pct))
        print(f"  {label} ({pattern}): {len(s)} variants, {overlap} overlap with parsnp ({pct:.3f})")

    # write ranking CSV
    ranking_rows.sort(key=lambda r: -r[4])
    with open("parsnp_agreement_ranking.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["label", "pattern", "n_variants", "parsnp_overlap", "pct_of_parsnp"])
        w.writerows(ranking_rows)
    print("wrote parsnp_agreement_ranking.csv")

    # ranking bar chart
    labels = [f"{r[0]}\n{r[1]}" for r in ranking_rows]
    pcts = [r[4] * 100 for r in ranking_rows]
    best_idx = 0

    fig, ax = plt.subplots(figsize=(12, 8))
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)
    colors = [HIGHLIGHT if i == best_idx else BAR_COLOR for i in range(len(ranking_rows))]
    y_pos = range(len(ranking_rows))
    bars = ax.barh(y_pos, pcts, color=colors, height=0.65, zorder=3)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=9, family="monospace", color=PRIMARY_INK)
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
    plt.close(fig)

    # full upset plot (parsnp + all configs, real pattern strings as labels)
    upset_contents = {"parsnp": parsnp_set}
    for label, (suffix, pattern) in CONFIGS.items():
        upset_contents[f"{label}: {pattern}"] = contents[label]

    upset_data = from_contents(upset_contents)
    fig = plt.figure(figsize=(22, 10))
    upset = UpSet(upset_data, subset_size="count", show_counts=True, sort_by="cardinality", max_subset_rank=30)
    upset.plot(fig=fig)
    plt.savefig("real_genome_upset_final.png", dpi=150, bbox_inches="tight")
    print("saved real_genome_upset_final.png")


if __name__ == "__main__":
    main()
