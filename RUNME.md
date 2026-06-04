# RUNME — how to run bronko (personal cheat-sheet)

Quick reference for building, testing, and running bronko on this machine.

Environment already set up on this laptop:
- **conda** (Miniforge) at `~/miniforge3`, with an env named `bronko` containing **KMC3** (`kmc`, `kmc_tools`)
- **Rust** at `~/.cargo` (used to compile bronko)
- project root: `~/Documents/bronko/bronko`

---

## Step 1 — Set up the terminal (every new terminal window)

```bash
source ~/miniforge3/bin/activate bronko
. "$HOME/.cargo/env"
cd ~/Documents/bronko/bronko
```

Puts `kmc` and `cargo` on your PATH and moves you into the project folder.

Check it worked (optional):
```bash
kmc --help | head -1     # K-Mer Counter (KMC) ver. 3.2.4 ...
cargo --version          # cargo 1.96.x
pwd                      # /Users/aaravgupta/Documents/bronko/bronko
```

---

## Step 2 — Build the program (once; redo only if the code changes)

```bash
cargo build --release
```

Creates `./target/release/bronko`. **Warnings are fine** — only look for the final
`Finished \`release\` profile ...` line. (Warnings = heads-up; errors = must fix.)

---

## Step 3 — (optional) Run the code's automated tests

```bash
cargo test
```

Look for `test result: ok. 3 passed`. These tests only exercise `build`, so they
don't need KMC.

---

## Step 4 — Run the variant caller on data

Keep the whole command on ONE line (if it wraps and splits, delete and re-paste it):

```bash
./target/release/bronko call -d test_data/hpv.bkdb -1 test_data/rep1_R1.fastq.gz -2 test_data/rep1_R2.fastq.gz -o hpv_out --pileup --consensus
```

Ends with `bronko complete!`. Results go in the `hpv_out/` folder.

What each part means:
- `call` — the variant-calling subcommand
- `-d test_data/hpv.bkdb` — the prebuilt reference index
- `-1 ... -2 ...` — paired-end read files (R1 and R2)
- `-o hpv_out` — output folder name
- `--pileup --consensus` — also write the per-position count table and a consensus sequence
- threads default to 4, so no `-t` needed

Input variations:
- **Single-end reads:** use `-r reads.fastq.gz` instead of `-1/-2`.
- **No prebuilt index:** use `-g some_genome.fa` instead of `-d` (builds an index on the fly, doesn't save it).

---

## Step 5 — Read the results

```bash
cat  hpv_out/bronko_overview.tsv    # summary: chosen genome, #variants, coverage
cat  hpv_out/rep1_R1.vcf            # the variant calls (VCF)
head -20 hpv_out/rep1_R1.tsv        # the pileup: per-position A/C/G/T counts (fwd UPPER / rev lower)
head -6  hpv_out/rep1_R1.fa         # the consensus sequence
```

Output files are named after the R1 file stem (e.g. `rep1_R1`).

Reading a VCF data line:
```
HPV16REF  4784  .  T  A  .  PASS  DP=24072;AF=0.014;DP4=18245,5438,115,218;SOR=1.296
```
- `T -> A` at position 4784; `AF=0.014` = 1.4% minor variant (iSNV); `DP=24072` total depth
- `DP4` = ref-fwd, ref-rev, alt-fwd, alt-rev (alt seen on BOTH strands here)
- `SOR` = strand-bias score; low = balanced = trustworthy

---

## Optional — build your own index

```bash
./target/release/bronko build -g test_data/4_sarscov2/*.fasta -k 21 -o my_sars_db
```
Creates `my_sars_db.bkdb`, then use it with `-d my_sars_db.bkdb` in a `call`.
(`-k` must match between `build` and `call`; odd, 15–31; default 21. `build` does NOT need KMC.)

## Optional — see all options

```bash
./target/release/bronko --help
./target/release/bronko call --help
./target/release/bronko build --help
```

## Optional — looser settings (shows more, lower-confidence variants)

```bash
./target/release/bronko call -d test_data/hpv.bkdb -1 test_data/rep1_R1.fastq.gz -2 test_data/rep1_R2.fastq.gz -o hpv_loose --min-af 0.005 --noise-multiplier 1.2
cat hpv_loose/rep1_R1.vcf
```

---

## Key parameters (defaults in `src/consts.rs`)

| Flag | Default | Meaning |
|---|---|---|
| `-k, --kmer-size` | 21 | k-mer length; **must match the index's k** |
| `--min-kmers` | 3 | a k-mer must appear >= this many times in the reads to be used |
| `--min-af` | 0.01 | minimum minor-allele frequency reported (1%) |
| `--noise-multiplier` | 1.5 | how far above the local estimated noise a variant must sit |
| `--n-per-strand` | 2 | distinct k-mers required on each strand |
| `--strand_odds` | 6.0 | max strand-bias (SOR) allowed |
| `--n-fixed` | 2 | k-mer end positions ignored when placing a variant |
| `--no-end-filter` / `--no-strand-filter` | off | disable the end-trim / strand-bias filters |
| `--pileup` / `--consensus` / `--alignment` | off | extra output files |
| `-t, --threads` | 4 | threads |

---

## The absolute minimum (fresh terminal -> results)

```bash
source ~/miniforge3/bin/activate bronko
. "$HOME/.cargo/env"
cd ~/Documents/bronko/bronko
cargo build --release
./target/release/bronko call -d test_data/hpv.bkdb -1 test_data/rep1_R1.fastq.gz -2 test_data/rep1_R2.fastq.gz -o hpv_out --pileup --consensus
cat hpv_out/bronko_overview.tsv
cat hpv_out/rep1_R1.vcf
```
