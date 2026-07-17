import random

OUT = "patterns_500.txt"

patterns = []
for i in range(500):
    seed = 1000 + i
    random.seed(seed)
    density = 0.1 + 0.8 * (i / 499)  # linearly spaced 10% -> 90% density across the 500 patterns
    length = 50
    chars = ['#' if random.random() < density else '_' for _ in range(length)]
    if '#' not in chars:
        chars[0] = '#'
    patterns.append(''.join(chars))

assert len(set(patterns)) == 500, "collision in generated patterns"

with open(OUT, "w") as f:
    for i, p in enumerate(patterns):
        f.write(f"{i}\t{p}\n")

print(f"wrote {OUT}: 500 patterns, density range 10%-90%+, seeds 1000-1499")
