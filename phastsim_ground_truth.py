import sys
from collections import defaultdict
from Bio import SeqIO

if len(sys.argv) != 4:
    print("usage: python3 phastsim_ground_truth.py <reference_single.fasta> <sars-cov-2_simulation_output.fasta> <out_prefix>")
    sys.exit(1)

ref_path, genomes_path, out_prefix = sys.argv[1], sys.argv[2], sys.argv[3]

ref_record = next(SeqIO.parse(ref_path, "fasta"))
ref_seq = str(ref_record.seq).upper()
ref_len = len(ref_seq)
print(f"reference: {ref_record.id}, {ref_len} bp")

# position (0-based) -> {alt_base: count of genomes carrying it}
variants = defaultdict(lambda: defaultdict(int))
n_genomes = 0
skipped = []

for record in SeqIO.parse(genomes_path, "fasta"):
    seq = str(record.seq).upper()
    if len(seq) != ref_len:
        skipped.append((record.id, len(seq)))
        continue
    n_genomes += 1
    for i, (r, q) in enumerate(zip(ref_seq, seq)):
        if q != r and q in "ACGT":
            variants[i][q] += 1

if skipped:
    print(f"WARNING: {len(skipped)} genomes skipped (length != reference, likely indels): {skipped[:5]}{'...' if len(skipped) > 5 else ''}")

print(f"compared {n_genomes} genomes against reference")
print(f"total variant positions: {len(variants)}")

with open(f"{out_prefix}_ground_truth.csv", "w") as f:
    f.write("pos_1based,ref_base,alt_base,genome_count,allele_freq\n")
    for pos in sorted(variants):
        for alt, count in variants[pos].items():
            af = count / n_genomes
            f.write(f"{pos + 1},{ref_seq[pos]},{alt},{count},{af:.4f}\n")

# flat one-line-per-variant file, for benchmark.sh's naive line-count "recall"
with open(f"{out_prefix}_ground_truth.txt", "w") as f:
    for pos in sorted(variants):
        for alt in variants[pos]:
            f.write(f"{ref_record.id}\t{pos + 1}\t{ref_seq[pos]}\t{alt}\t+\n")

print(f"wrote {out_prefix}_ground_truth.csv (with allele frequencies) and {out_prefix}_ground_truth.txt (flat, for benchmark.sh)")
