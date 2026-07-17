import random

OUT = "patterns_500.txt"

patterns = []

# 450 structured patterns: systematic grid of (run_length, gap_length) pairs.
# pattern = '#' * run + '_' * gap, repeated by the cyclic mask lookup in bronko.
# run in 1..15, gap in 1..30 -> 450 combinations, all small/bounded (max gap = 30,
# nothing like skip-by-1000), density ranges from 1/31 (~3%) to 15/16 (~94%).
for run in range(1, 16):
    for gap in range(1, 31):
        patterns.append(("#" * run) + ("_" * gap))

assert len(patterns) == 450

# 50 random-gap patterns: consecutive kept positions spaced a random 1-3 apart
# (same style as the earlier random_gap1to3 pattern), each with a distinct seed
for i in range(50):
    seed = 5000 + i
    random.seed(seed)
    chunk = []
    length = 0
    target_len = 50
    while length < target_len:
        chunk.append("#")
        gap = random.choice([1, 2, 3])
        chunk.append("_" * (gap - 1))
        length += gap
    patterns.append("".join(chunk))

assert len(patterns) == 500

# guarantee uniqueness - if a random one collides with a grid one (extremely
# unlikely given the different construction, but check anyway), bump the seed
seen = set()
final = []
next_seed = 6000
for p in patterns:
    while p in seen:
        random.seed(next_seed)
        next_seed += 1
        chunk = []
        length = 0
        while length < 50:
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
print(f"wrote {OUT}: 500 patterns (450 structured run/gap grid + 50 random-gap 1-3)")
print(f"density range: {min(densities):.2f} - {max(densities):.2f}")
print(f"max single gap across all patterns: {max(p.count('_') // max(1, p.count('#')) for p in final[:450])} (structured only, bounded by design)")
