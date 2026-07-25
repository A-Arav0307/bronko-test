import itertools

OUT = "patterns_500.txt"
K = 21
HALF_BUDGET = 10  # each side of the pattern (half + mirrored half) fits within this, plus 1+ middle chars = K
MAX_BASE_LEN = 10  # base pattern ('#'*run + '_'*gap) capped at this length before tiling
MAX_HASHES = 11  # discard any generated pattern with more '#'s than this - keeps patterns sparse/distinct;
                  # 11 is the sparsest threshold that still reaches 500 with this base family

ska_pattern = "__________#__________"
TARGET_TOTAL = 500

def palindromic_middles(m):
    """all binary strings of length m that are themselves palindromes -
    determined entirely by their first ceil(m/2) characters"""
    half_len = (m + 1) // 2
    mirror_len = m // 2
    for combo in itertools.product("#_", repeat=half_len):
        free_part = "".join(combo)
        yield free_part + free_part[:mirror_len][::-1]


def bases_of_length(L):
    """every binary string of length L starting with '#' - not just single-run-then-gap,
    so shapes like '#_#' and '##_#' are included too, giving far more sparse options"""
    for combo in itertools.product("#_", repeat=L - 1):
        yield "#" + "".join(combo)


patterns = []
seen = set()

for L in range(1, MAX_BASE_LEN + 1):
    for base in bases_of_length(L):
        reps = HALF_BUDGET // L
        half = base * reps
        middle_len = K - 2 * len(half)
        right = half[::-1]

        tier = []
        for middle in palindromic_middles(middle_len):
            pattern = half + middle + right
            if pattern.count("#") > MAX_HASHES:
                continue
            if pattern not in seen:
                seen.add(pattern)
                tier.append(pattern)

        remaining = (TARGET_TOTAL - 1) - len(patterns)  # -1 reserves the last slot for ska_pattern
        if remaining <= 0:
            break
        patterns.extend(tier[:remaining])
    if len(patterns) >= TARGET_TOTAL - 1:
        break

if len(patterns) < TARGET_TOTAL - 1:
    print(f"\nWARNING: exhausted every base pattern up to length {MAX_BASE_LEN} - "
          f"only {len(patterns)} distinct symmetric patterns possible (target was {TARGET_TOTAL - 1})")
patterns.append(ska_pattern)

assert len(set(patterns)) == len(patterns), "collision found"
assert all(len(p) == K for p in patterns), "not every pattern is exactly k=21 chars"

with open(OUT, "w") as f:
    for i, p in enumerate(patterns):
        f.write(f"{i}\t{p}\n")

print(f"\nwrote {OUT}: {len(patterns)} patterns, all exactly k={K} chars, all symmetric "
      f"(half + free middle + mirrored half), ska_pattern kept as idx {len(patterns) - 1}")
