import csv
import os

PARSNP_VCF = os.path.expanduser("~/bronko_benchmark/phastsim-run-round2/parsnp-out/parsnp_variants.vcf")
LABELS = ["default", "ska_pattern", "idx336", "idx408", "idx216", "idx28",
          "idx40", "idx42", "idx44", "idx56", "idx54", "idx100"]


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
    contents = {"parsnp": load_parsnp_set(PARSNP_VCF)}
    for label in LABELS:
        contents[label] = load_bronko_set(f"variants_{label}.csv")

    all_labels = list(contents.keys())
    other_bronko = [l for l in all_labels if l not in ("parsnp", "ska_pattern")]

    parsnp_set = contents["parsnp"]
    ska_set = contents["ska_pattern"]

    # exact match: in both parsnp and ska, in NONE of the other 10 bronko patterns
    union_others = set().union(*(contents[l] for l in other_bronko))
    exclusive_parsnp_ska = (parsnp_set & ska_set) - union_others
    print(f"parsnp ∩ ska_pattern, excluded from all 10 other patterns: {len(exclusive_parsnp_ska)}")

    # ska_pattern-only (not in parsnp, not in any other bronko pattern)
    ska_only = ska_set - parsnp_set - union_others
    print(f"ska_pattern exclusively (not in parsnp or any other pattern): {len(ska_only)}")

    # parsnp-only (not in any bronko pattern at all)
    union_all_bronko = union_others | ska_set
    parsnp_only = parsnp_set - union_all_bronko
    print(f"parsnp exclusively (not in any bronko pattern): {len(parsnp_only)}")

    # sanity: parsnp vs ska_pattern direct overlap (regardless of others)
    print(f"\nparsnp total: {len(parsnp_set)}")
    print(f"ska_pattern total: {len(ska_set)}")
    print(f"parsnp ∩ ska_pattern (any): {len(parsnp_set & ska_set)}")
    print(f"parsnp ∩ ska_pattern / parsnp: {len(parsnp_set & ska_set) / len(parsnp_set):.3f}")
    print(f"parsnp ∩ ska_pattern / ska_pattern: {len(parsnp_set & ska_set) / len(ska_set):.3f}")

    for label in other_bronko:
        overlap = len(parsnp_set & contents[label])
        print(f"parsnp ∩ {label}: {overlap} ({overlap/len(parsnp_set):.3f} of parsnp)")


if __name__ == "__main__":
    main()
