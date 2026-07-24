K = 21  # for the printed k=21 expansion preview only - does not affect what's stored
OLD_PATTERNS_FILE = "patterns_500.txt"
OUT = "patterns_450_symmetric.txt"

# symmetric construction: for each (run, gap) in the grid, half = "#"*run + "_"*gap,
# and the final pattern is half + "#" (middle, always kept) + reverse(half).
# run 1..15, gap 1..30 -> 15*30 = 450 combinations, matching the exact grid laid out by hand.


def expand_to_k(pattern, k=K):
    return "".join(pattern[i % len(pattern)] for i in range(k))


def main():
    patterns = []
    for run in range(1, 16):
        for gap in range(1, 31):
            half = ("#" * run) + ("_" * gap)
            patterns.append(half + "#" + half[::-1])

    assert len(patterns) == 450
    assert len(set(patterns)) == 450, "collision found - should be impossible by construction"

    with open(OLD_PATTERNS_FILE) as f:
        old_lines = [line.rstrip("\n").split("\t", 1)[1] for line in f if line.strip()]
    last_50 = old_lines[450:500]
    assert len(last_50) == 50, f"expected 50 preserved randomized patterns, got {len(last_50)} - check {OLD_PATTERNS_FILE}"

    ska_pattern = "__________#__________"

    combined = patterns + last_50 + [ska_pattern]
    assert len(combined) == 501
    assert len(set(combined)) == 501, "collision somewhere in the combined set"

    with open(OUT, "w") as f:
        for i, p in enumerate(combined):
            f.write(f"{i}\t{p}\n")
    print(f"wrote {OUT}: 450 symmetric run/gap patterns (idx 0-449) + 50 preserved randomized (idx 450-499) + ska_pattern (idx 500)")

    print(f"\n=== sample: first 5 (run=1) ===")
    for i in range(5):
        p = patterns[i]
        print(f"  idx={i:>3} len={len(p):>2}  raw={p!r:<15}  k{K}={expand_to_k(p)}")

    print(f"\n=== sample: run=1,gap=2 and run=1,gap=3 (your worked examples) ===")
    for i in (1, 2):
        p = patterns[i]
        print(f"  idx={i:>3} raw={p!r}")

    print(f"\n=== sample: last 5 (run=15) ===")
    for i in range(445, 450):
        p = patterns[i]
        print(f"  idx={i:>3} len={len(p):>2}  raw={p!r:<35}  k{K}={expand_to_k(p)}")


if __name__ == "__main__":
    main()
