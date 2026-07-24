import random

OUT = "patterns_500.txt"
K = 21  # bronko's default kmer size - patterns are capped to this length since anything
        # beyond position k-1 is never consulted (keep_mask[j % len] only ever sees j in 0..k)

patterns = []

# symmetric run/gap grid: half = "#"*run + "_"*gap, pattern = half + "#" + reverse(half).
# run 1..15, gap 1..30 -> 450 combinations, capped to k=21 chars. Capping collapses many
# of the longer run/gap combos into duplicates (since anything past position 20 never
# mattered anyway), so dedupe and report however many distinct patterns remain.
seen = set()
symmetric = []
for run in range(1, 16):
    for gap in range(1, 31):
        half = ("#" * run) + ("_" * gap)
        full = half + "#" + half[::-1]
        capped = full[:K]
        if capped not in seen:
            seen.add(capped)
            symmetric.append(capped)

print(f"symmetric run/gap grid: 450 combinations generated, {len(symmetric)} distinct after capping to k={K}")
patterns.extend(symmetric)

# 100 random-gap patterns: consecutive kept positions spaced a random amount
# apart, still small/close-together (max gap 3), varying the gap range across
# sub-groups for some diversity, each with a distinct seed. Kept unchanged from
# the original generator so this block is reproducible run to run.
gap_ranges = [[1, 2], [1, 2, 3], [2, 3]]
random_patterns = []
for i in range(100):
    seed = 5000 + i
    random.seed(seed)
    gap_choices = gap_ranges[i % len(gap_ranges)]
    chunk = []
    length = 0
    target_len = 40
    while length < target_len:
        chunk.append("#")
        gap = random.choice(gap_choices)
        chunk.append("_" * (gap - 1))
        length += gap
    random_patterns.append("".join(chunk))

# only the last 50 of the original 100 randomized patterns are kept (first 50 replaced
# by the symmetric grid above, per instruction to preserve "the last 50 as is")
preserved_randomized = random_patterns[50:100]
patterns.extend(preserved_randomized)

# manually added: single '#' centered in a k=21 window (named after the split-kmer
# concept in the SKA tool), added after the original 500-pattern sweep already ran
ska_pattern = "__________#__________"
patterns.append(ska_pattern)

# guarantee uniqueness across the whole combined set
assert len(patterns) == len(set(patterns)), "collision found in combined pattern set"

with open(OUT, "w") as f:
    for i, p in enumerate(patterns):
        f.write(f"{i}\t{p}\n")

print(f"wrote {OUT}: {len(symmetric)} symmetric (idx 0-{len(symmetric)-1}) + "
      f"{len(preserved_randomized)} preserved randomized + 1 ska_pattern = {len(patterns)} total patterns")
