import csv
import os
from upsetplot import UpSet, from_contents
import matplotlib.pyplot as plt

PARSNP_VCF = os.path.expanduser("~/bronko_benchmark/phastsim-run-round2/parsnp-out/parsnp_variants.vcf")

# best performer (idx42, highest parsnp agreement at 72.3%) gets its real pattern string as the label
LABEL_MAP = {
    "parsnp": "parsnp",
    "ska_pattern": "ska_pattern (worst: 52.9%)",
    "default": "default (no pattern)",
    "idx28": "idx28 (#___#_____#_____#___#)",
    "idx42": "BEST: ####_#____#____#_####",
}
KEYS = ["parsnp", "ska_pattern", "default", "idx28", "idx42"]


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
    contents = {}
    for key in KEYS:
        label = LABEL_MAP[key]
        if key == "parsnp":
            contents[label] = load_parsnp_set(PARSNP_VCF)
        else:
            contents[label] = load_bronko_set(f"variants_{key}.csv")
        print(f"{label}: {len(contents[label])} variants")

    upset_data = from_contents(contents)

    fig = plt.figure(figsize=(14, 7))
    upset = UpSet(upset_data, subset_size="count", show_counts=True, sort_by="cardinality")
    upset.style_subsets(present=LABEL_MAP["idx42"], facecolor="#e34948", label="best real-data agreement")
    upset.plot(fig=fig)
    plt.savefig("real_genome_upset_simplified.png", dpi=150, bbox_inches="tight")
    print("saved real_genome_upset_simplified.png")


if __name__ == "__main__":
    main()
