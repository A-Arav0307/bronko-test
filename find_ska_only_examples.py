import csv
from collections import Counter


def load_set(path):
    variants = set()
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            variants.add((row["genome_id"], row["pos"], row["alt"]))
    return variants


def main():
    ska = load_set("variants_ska_pattern.csv")
    default = load_set("variants_default.csv")

    ska_only = ska - default
    print(f"ska_pattern found, default did NOT: {len(ska_only)} variants")

    # find which genome has the most examples, for an efficient single-genome investigation
    genome_counts = Counter(g for g, pos, alt in ska_only)
    top_genome, count = genome_counts.most_common(1)[0]
    print(f"genome with most examples: {top_genome} ({count} cases)")

    examples = sorted([v for v in ska_only if v[0] == top_genome], key=lambda v: int(v[1]))[:10]
    print(f"\nfirst 10 example positions on {top_genome}:")
    for genome_id, pos, alt in examples:
        print(f"  pos={pos} alt={alt}")

    with open("ska_only_examples.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["genome_id", "pos", "alt"])
        w.writerows(sorted(ska_only))
    print(f"\nwrote ska_only_examples.csv ({len(ska_only)} total rows)")


if __name__ == "__main__":
    main()
