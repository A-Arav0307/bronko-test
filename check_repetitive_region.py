import sys

REF = "reference_single_chromosome_only.fasta"

# regions of interest (1-based positions from the VCF, converted to 0-based for slicing)
REGIONS = [
    ("cluster_1", 167500, 167800),
    ("cluster_2", 169300, 169500),
]

with open(REF) as f:
    lines = f.readlines()
seq = "".join(l.strip() for l in lines if not l.startswith(">")).upper()
print(f"reference length: {len(seq)}")

for name, start, end in REGIONS:
    region_seq = seq[start:end]
    print(f"\n=== {name}: {start}-{end} ({len(region_seq)}bp) ===")
    print(f"sequence: {region_seq[:60]}...")

    # search for this exact region sequence elsewhere in the genome
    occurrences = []
    idx = seq.find(region_seq)
    while idx != -1:
        occurrences.append(idx)
        idx = seq.find(region_seq, idx + 1)
    print(f"exact full-region match count (incl. itself): {len(occurrences)}  positions: {occurrences[:10]}")

    # also check a shorter, more sensitive 30bp seed from the middle of the region,
    # in case the full region isn't repeated but a sub-piece is
    mid = len(region_seq) // 2
    seed = region_seq[mid-15:mid+15]
    seed_occurrences = []
    idx = seq.find(seed)
    while idx != -1:
        seed_occurrences.append(idx)
        idx = seq.find(seed, idx + 1)
    print(f"30bp seed match count (incl. itself): {len(seed_occurrences)}  positions: {seed_occurrences[:10]}")
