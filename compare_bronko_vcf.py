import sys
import re
import csv


def parse_vcf(path):
    variants = {}
    with open(path) as f:
        for line in f:
            if line.startswith("#"):
                continue
            fields = line.rstrip("\n").split("\t")
            if len(fields) < 8:
                continue
            _chrom, pos, _id, ref, alt, _qual, _filt, info = fields[:8]
            af_match = re.search(r"AF=([\d.eE+-]+)", info)
            dp_match = re.search(r"DP=(\d+)", info)
            af = float(af_match.group(1)) if af_match else None
            dp = int(dp_match.group(1)) if dp_match else None
            variants[(int(pos), alt.upper())] = {"ref": ref.upper(), "af": af, "dp": dp}
    return variants


def parse_ground_truth(path):
    truth = {}
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            pos = int(row["pos_1based"])
            alt = row["alt_base"].upper()
            truth[(pos, alt)] = {
                "ref": row["ref_base"].upper(),
                "af": float(row["allele_freq"]),
                "genome_count": int(row["genome_count"]),
            }
    return truth


def main():
    if len(sys.argv) not in (3, 4):
        print("usage: python3 compare_bronko_vcf.py <bronko_output.vcf> <phastsim_ground_truth.csv> [min_af_filter]")
        sys.exit(1)

    vcf_path, truth_path = sys.argv[1], sys.argv[2]
    min_af_filter = float(sys.argv[3]) if len(sys.argv) == 4 else None

    called = parse_vcf(vcf_path)
    truth = parse_ground_truth(truth_path)

    if min_af_filter is not None:
        called = {k: v for k, v in called.items() if v["af"] is not None and v["af"] > min_af_filter}
        truth = {k: v for k, v in truth.items() if v["af"] > min_af_filter}
        print(f"applied AF > {min_af_filter} filter: {len(called)} called, {len(truth)} true variants remain")

    called_keys = set(called)
    truth_keys = set(truth)

    tp = called_keys & truth_keys
    fp = called_keys - truth_keys
    fn = truth_keys - called_keys

    precision = len(tp) / len(called_keys) if called_keys else 0.0
    recall = len(tp) / len(truth_keys) if truth_keys else 0.0

    ref_mismatches = [k for k in tp if called[k]["ref"] != truth[k]["ref"]]

    af_errors = []
    for key in tp:
        called_af = called[key]["af"]
        true_af = truth[key]["af"]
        if called_af is not None:
            af_errors.append(abs(called_af - true_af))

    print(f"true variants:    {len(truth_keys)}")
    print(f"called variants:  {len(called_keys)}")
    print(f"true positives:   {len(tp)}")
    print(f"false positives:  {len(fp)}  (called but not a real variant)")
    print(f"false negatives:  {len(fn)}  (real variant bronko missed)")
    print(f"precision:        {precision:.4f}")
    print(f"recall:           {recall:.4f}")
    if ref_mismatches:
        print(f"WARNING: {len(ref_mismatches)} positions have mismatched REF base between VCF and ground truth (check coordinate/contig alignment)")

    if af_errors:
        af_errors.sort()
        n = len(af_errors)
        mean_err = sum(af_errors) / n
        median_err = af_errors[n // 2]
        print(f"AF error on true positives: mean={mean_err:.4f}, median={median_err:.4f}, max={max(af_errors):.4f}")

    if fn:
        low_af_missed = sum(1 for k in fn if truth[k]["af"] < 0.05)
        print(f"false negatives with true AF < 0.05: {low_af_missed}/{len(fn)} (low-frequency variants are the expected place to lose recall)")

    with open("vcf_comparison_detail.csv", "w") as f:
        f.write("pos,alt,category,true_af,called_af\n")
        for key in sorted(tp):
            f.write(f"{key[0]},{key[1]},TP,{truth[key]['af']:.4f},{called[key]['af']}\n")
        for key in sorted(fp):
            f.write(f"{key[0]},{key[1]},FP,,{called[key]['af']}\n")
        for key in sorted(fn):
            f.write(f"{key[0]},{key[1]},FN,{truth[key]['af']:.4f},\n")

    print("wrote vcf_comparison_detail.csv")


if __name__ == "__main__":
    main()
