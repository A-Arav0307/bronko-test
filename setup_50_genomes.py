import sys
import os
from Bio import SeqIO

REF_PATH = "reference_single.fasta"
GENOMES_PATH = "ecoli_simulation_output.fasta"
OUT_DIR = "genomes_50"
MANIFEST = "genomes_50_manifest.txt"

os.makedirs(OUT_DIR, exist_ok=True)

ref_record = next(SeqIO.parse(REF_PATH, "fasta"))
ref_seq = str(ref_record.seq).upper()
ref_len = len(ref_seq)
print(f"reference: {ref_record.id}, {ref_len} bp")

records = list(SeqIO.parse(GENOMES_PATH, "fasta"))
print(f"loaded {len(records)} candidate genomes")

# compute diff count vs reference for each candidate
scored = []
for r in records:
    seq = str(r.seq).upper()
    if len(seq) != ref_len:
        print(f"WARNING: skipping {r.id}, length {len(seq)} != reference {ref_len}")
        continue
    diffs = sum(1 for a, b in zip(ref_seq, seq) if a != b)
    scored.append((diffs, r))

# Parsnp's auto-picked reference genome appears TWICE in the tree - once as the
# ".ref" backbone, once as a regular query (since it was also one of the 50 real
# input genomes). Both leaves evolve from ~zero branch length, so BOTH show up
# with near-zero diffs here (e.g. 7 and 9 out of 5.88M bp) - neither is a
# meaningfully-evolved genome, so keeping "the higher of the two" (an earlier,
# wrong version of this fix) just picks which near-empty duplicate to keep.
# Exclude both entirely. That leaves 49 genomes, not 50 - there genuinely is no
# meaningfully-evolved descendant of the reference genome in this simulation.
by_normalized_id = {}
for diffs, r in scored:
    norm_id = r.id[:-4] if r.id.endswith(".ref") else r.id
    by_normalized_id.setdefault(norm_id, []).append((diffs, r))

selected = []
for norm_id, group in by_normalized_id.items():
    if len(group) > 1:
        ids = [r.id for _, r in group]
        diffs_list = [d for d, _ in group]
        print(f"duplicate pair detected for {norm_id}: excluding both {ids} ({diffs_list} diffs - both near-zero, neither meaningfully evolved)")
    else:
        selected.append(group[0])

selected.sort(key=lambda x: x[0])
print(f"{len(selected)} meaningful genomes remain after excluding the duplicate pair")

manifest_lines = []
for diffs, r in selected:
    safe_id = r.id
    seq = str(r.seq).upper()

    genome_fasta = f"{OUT_DIR}/{safe_id}.fasta"
    with open(genome_fasta, "w") as f:
        f.write(f">{safe_id}\n{seq}\n")

    truth_csv = f"{OUT_DIR}/{safe_id}_ground_truth.csv"
    with open(truth_csv, "w") as f:
        f.write("pos_1based,ref_base,alt_base,genome_count,allele_freq\n")
        n = 0
        for i, (a, b) in enumerate(zip(ref_seq, seq)):
            if b != a and b in "ACGT":
                f.write(f"{i+1},{a},{b},1,1.0\n")
                n += 1

    manifest_lines.append(safe_id)
    print(f"  {safe_id}: {n} true variants -> {genome_fasta}, {truth_csv}")

with open(MANIFEST, "w") as f:
    f.write("\n".join(manifest_lines) + "\n")

print(f"wrote {MANIFEST} with {len(manifest_lines)} genome IDs")
