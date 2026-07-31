import csv
import glob

SKA_TSV = glob.glob("/tmp/pileup_ska/*.tsv")[0]
DEFAULT_TSV = glob.glob("/tmp/pileup_default/*.tsv")[0]
EXAMPLES_CSV = "real_genome_results/ska_only_examples.csv"
TARGET_GENOME = "GCF_001644745.1_ASM164474v1_genomic.fna"


def load_pileup(path):
    # index (1-based position) -> (A,C,G,T,a,c,g,t)
    pileup = {}
    with open(path) as f:
        for line in f:
            fields = line.rstrip("\n").split("\t")
            if len(fields) < 11 or fields[0] == "reference":
                continue
            pos = int(fields[1])
            counts = tuple(int(x) for x in fields[3:11])
            pileup[pos] = counts
    return pileup


def classify(ska_counts, default_counts):
    if ska_counts is None:
        return "ska_missing"
    ska_total = sum(ska_counts)
    ska_nonzero_bases = sum(1 for i in (2, 3, 6, 7) if ska_counts[i] > 0)  # G,T,g,t indices... adjust below

    # bases order: A,C,G,T,a,c,g,t -> combine upper+lower per base
    A = ska_counts[0] + ska_counts[4]
    C = ska_counts[1] + ska_counts[5]
    G = ska_counts[2] + ska_counts[6]
    T = ska_counts[3] + ska_counts[7]
    ska_base_counts = {"A": A, "C": C, "G": G, "T": T}
    ska_nonzero = [b for b, c in ska_base_counts.items() if c > 0]
    ska_unanimous = len(ska_nonzero) == 1

    if default_counts is None:
        return "ska_unanimous_default_absent" if ska_unanimous else "ska_mixed_default_absent"

    dA = default_counts[0] + default_counts[4]
    dC = default_counts[1] + default_counts[5]
    dG = default_counts[2] + default_counts[6]
    dT = default_counts[3] + default_counts[7]
    default_base_counts = {"A": dA, "C": dC, "G": dG, "T": dT}
    default_total = sum(default_base_counts.values())
    default_nonzero = [b for b, c in default_base_counts.items() if c > 0]
    default_unanimous = len(default_nonzero) == 1

    if default_total == 0:
        return "ska_unanimous_default_zero_depth" if ska_unanimous else "ska_mixed_default_zero_depth"

    if ska_unanimous and not default_unanimous:
        return "MATCHES_PATTERN: ska_unanimous_default_mixed"
    elif ska_unanimous and default_unanimous:
        return "ska_unanimous_default_also_unanimous"
    else:
        return "ska_itself_not_unanimous"


def main():
    ska_pileup = load_pileup(SKA_TSV)
    default_pileup = load_pileup(DEFAULT_TSV)
    print(f"loaded {len(ska_pileup)} ska positions, {len(default_pileup)} default positions")

    examples = []
    with open(EXAMPLES_CSV) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["genome_id"] == TARGET_GENOME:
                examples.append(int(row["pos"]))

    print(f"total ska-only examples for {TARGET_GENOME}: {len(examples)}")

    from collections import Counter
    results = Counter()
    for pos in examples:
        ska_c = ska_pileup.get(pos)
        default_c = default_pileup.get(pos)
        results[classify(ska_c, default_c)] += 1

    print("\nbreakdown:")
    for category, count in results.most_common():
        pct = count / len(examples) * 100
        print(f"  {category}: {count} ({pct:.1f}%)")


if __name__ == "__main__":
    main()
