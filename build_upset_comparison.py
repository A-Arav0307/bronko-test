import csv
import re
import sys
from upsetplot import UpSet, from_contents
import matplotlib.pyplot as plt

PARSNP_VCF = "../phastsim-run-round2/parsnp-out/parsnp_variants.vcf"
RESULTS_DIR = "."

LABELS = ["default", "ska_pattern", "idx336", "idx408", "idx216", "idx28",
          "idx40", "idx42", "idx44", "idx56", "idx54", "idx100"]


def load_parsnp_set(path):
    variants = set()
    with open(path) as f:
        header_cols = None
        for line in f:
            if line.startswith("##"):
                continue
            if line.startswith("#CHROM"):
                header_cols = line.rstrip("\n").split("\t")
                genome_cols = header_cols[9:]
                continue
            fields = line.rstrip("\n").split("\t")
            pos, alt = fields[1], fields[4].upper()
            genotypes = fields[9:]
            for genome_id, gt in zip(genome_cols, genotypes):
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
    print("loading parsnp variant set...")
    contents = {"parsnp": load_parsnp_set(PARSNP_VCF)}
    print(f"  parsnp: {len(contents['parsnp'])} variant calls")

    for label in LABELS:
        path = f"{RESULTS_DIR}/variants_{label}.csv"
        print(f"loading {label}...")
        contents[label] = load_bronko_set(path)
        print(f"  {label}: {len(contents[label])} variant calls")

    print("\nbuilding upset data structure (this can take a while with large sets)...")
    upset_data = from_contents(contents)

    fig = plt.figure(figsize=(20, 10))
    upset = UpSet(upset_data, subset_size="count", show_counts=True, sort_by="cardinality", max_subset_rank=30)
    upset.plot(fig=fig)
    plt.savefig("real_genome_upset.png", dpi=150, bbox_inches="tight")
    print("saved real_genome_upset.png")

    with open("real_genome_set_sizes.csv", "w") as f:
        f.write("label,n_variants\n")
        for label, s in contents.items():
            f.write(f"{label},{len(s)}\n")
    print("saved real_genome_set_sizes.csv")


if __name__ == "__main__":
    main()
