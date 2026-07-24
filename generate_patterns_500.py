import itertools

OUT = "patterns_500.txt"
K = 21
HALF_BUDGET = 10  # each side of the pattern (half + mirrored half) fits within this, plus 1+ middle chars = K

ska_pattern = "__________#__________"
TARGET_TOTAL = 500

patterns = []
seen = set()

for run in range(1, HALF_BUDGET):
    for gap in range(1, HALF_BUDGET - run + 1):
        base = ("#" * run) + ("_" * gap)
        L = len(base)
        reps = HALF_BUDGET // L
        half = base * reps
        middle_len = K - 2 * len(half)
        right = half[::-1]

        tier = []
        for bits in itertools.product("#_", repeat=middle_len):
            middle = "".join(bits)
            pattern = half + middle + right
            if pattern not in seen:
                seen.add(pattern)
                tier.append(pattern)

        remaining = (TARGET_TOTAL - 1) - len(patterns)  # -1 reserves the last slot for ska_pattern
        if remaining <= 0:
            break
        patterns.extend(tier[:remaining])
        print(f"base={base!r} (run={run},gap={gap},L={L}): half={half!r} ({len(half)} chars), "
              f"middle_len={middle_len} ({2**middle_len} possible), took {min(len(tier), remaining)}")
    if len(patterns) >= TARGET_TOTAL - 1:
        break

patterns.append(ska_pattern)

assert len(patterns) == TARGET_TOTAL, f"expected {TARGET_TOTAL}, got {len(patterns)}"
assert len(set(patterns)) == TARGET_TOTAL, "collision found"
assert all(len(p) == K for p in patterns), "not every pattern is exactly k=21 chars"

with open(OUT, "w") as f:
    for i, p in enumerate(patterns):
        f.write(f"{i}\t{p}\n")

print(f"\nwrote {OUT}: {TARGET_TOTAL} patterns, all exactly k={K} chars, all symmetric "
      f"(half + free middle + mirrored half), ska_pattern kept as idx {TARGET_TOTAL - 1}")
