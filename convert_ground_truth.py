import sys
import csv

IUPAC = {
    "R": "AG", "Y": "CT", "S": "GC", "W": "AT", "K": "GT", "M": "AC",
    "B": "CGT", "D": "AGT", "H": "ACT", "V": "ACG", "N": "ACGT",
}

def resolve_alt(ref, code):
    code = code.upper()
    if code in "ACGT":
        return code, 1.0
    if code in IUPAC:
        options = [b for b in IUPAC[code] if b != ref]
        if len(options) == 1:
            return options[0], 0.5
        return None, None
    return None, None

def main():
    if len(sys.argv) != 3:
        print("usage: python3 convert_ground_truth.py <input.txt> <output.csv>")
        sys.exit(1)

    in_path, out_path = sys.argv[1], sys.argv[2]
    rows = []
    skipped = 0
    with open(in_path) as f:
        for line in f:
            fields = line.rstrip("\n").split("\t")
            if len(fields) < 4:
                continue
            _chrom, pos, ref, code = fields[0], fields[1], fields[2].upper(), fields[3]
            alt, af = resolve_alt(ref, code)
            if alt is None:
                skipped += 1
                continue
            rows.append((int(pos), ref, alt, 1, af))

    with open(out_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["pos_1based", "ref_base", "alt_base", "genome_count", "allele_freq"])
        for pos, ref, alt, gc, af in sorted(rows):
            writer.writerow([pos, ref, alt, gc, af])

    print(f"wrote {out_path}: {len(rows)} variants ({skipped} skipped as ambiguous/unresolvable)")


if __name__ == "__main__":
    main()
