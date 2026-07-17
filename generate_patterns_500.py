import random

OUT = "patterns_500.txt"

patterns = []

# 400 structured patterns: systematic grid of (run_length, gap_length) pairs.
# pattern = '#' * run + '_' * gap, repeated by the cyclic mask lookup in bronko.
# run in 1..20, gap in 1..20 -> 400 combinations. Both bounded well under k=21
# (the default k-mer size), so kept positions stay close together - no pattern
# skips further than 20 positions between hits. Density ranges 1/21 (~5%) to
# 20/21 (~95%).
for run in range(1, 21):
    for gap in range(1, 21):
        patterns.append(("#" * run) + ("_" * gap))

assert len(patterns) == 400

# 100 random-gap patterns: consecutive kept positions spaced a random amount
# apart, still small/close-together (max gap 3), varying the gap range across
# sub-groups for some diversity, each with a distinct seed
gap_ranges = [[1, 2], [1, 2, 3], [2, 3]]
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
    patterns.append("".join(chunk))

assert len(patterns) == 500

# guarantee uniqueness - bump the seed on any collision (extremely unlikely
# given the different construction, but check anyway)
seen = set()
final = []
next_seed = 6000
for p in patterns:
    while p in seen:
        random.seed(next_seed)
        next_seed += 1
        chunk = []
        length = 0
        while length < 40:
            chunk.append("#")
            gap = random.choice([1, 2, 3])
            chunk.append("_" * (gap - 1))
            length += gap
        p = "".join(chunk)
    seen.add(p)
    final.append(p)

assert len(set(final)) == 500

with open(OUT, "w") as f:
    for i, p in enumerate(final):
        f.write(f"{i}\t{p}\n")

densities = [p.count("#") / len(p) for p in final]
lengths = [len(p) for p in final]
print(f"wrote {OUT}: 500 patterns (400 structured run/gap grid, run<=20 gap<=20 + 100 random-gap<=3)")
print(f"density range: {min(densities):.2f} - {max(densities):.2f}")
print(f"pattern length range: {min(lengths)} - {max(lengths)} chars")
