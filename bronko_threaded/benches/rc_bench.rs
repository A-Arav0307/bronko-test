use criterion::{black_box, criterion_group, criterion_main, Criterion};

// old O(k) loop implementation
fn reverse_complement_old(kmer_val: u64, k: usize) -> u64 {
    let mut rc = 0u64;
    for i in 0..k {
        let two_bits = (kmer_val >> (2 * i)) & 0b11;
        let comp = 0b11 ^ two_bits;
        rc <<= 2;
        rc |= comp;
    }
    rc
}

// new constant-time bitwise implementation
fn reverse_complement_new(kmer_val: u64, k: usize) -> u64 {
    let rev = kmer_val.reverse_bits() >> (64 - 2 * k);
    let rev_fixed = ((rev >> 1) & 0x5555_5555_5555_5555u64)
        | ((rev & 0x5555_5555_5555_5555u64) << 1);
    rev_fixed ^ ((1u64 << (2 * k)).wrapping_sub(1))
}

fn bench_rc(c: &mut Criterion) {
    let k = 21usize;
    let kmer: u64 = 0b11_10_01_00_11_10_01_00_11_10_01_00_11_10_01_00_11_10_01_00_11;

    let mut group = c.benchmark_group("reverse_complement");

    group.bench_function("old_loop", |b| {
        b.iter(|| reverse_complement_old(black_box(kmer), black_box(k)))
    });

    group.bench_function("new_bitwise", |b| {
        b.iter(|| reverse_complement_new(black_box(kmer), black_box(k)))
    });

    group.finish();
}

criterion_group!(benches, bench_rc);
criterion_main!(benches);
