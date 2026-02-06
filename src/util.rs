use memory_stats::memory_stats;
use std::path::Path;
use std::fs;
use log::*;



pub fn check_fastq(file: &str) -> bool {
    if file.ends_with(".fq")
        || file.ends_with(".fastq")
        || file.ends_with(".fq.gz")
        || file.ends_with("fastq.gz")
        || file.ends_with("fnq")
        || file.ends_with("fnq.gz")
    {
        return true;
    }
    return false;
}

pub fn check_fasta(file: &str) -> bool {
    if file.ends_with(".fa")
        || file.ends_with(".fasta")
        || file.ends_with(".fa.gz")
        || file.ends_with("fasta.gz")
        || file.ends_with("fna")
        || file.ends_with("fna.gz")
    {
        return true;
    }
    return false;
}

pub fn check_txt(file: &str) -> bool {
    if file.ends_with(".txt"){
        return true;
    }
    return false;
}

pub fn clean_sample_id<P: AsRef<Path>>(path: P) -> String {
    let filename = path.as_ref().file_name()
        .and_then(|s| s.to_str())
        .unwrap_or("unknown");

    // Known FASTQ/A suffixes (ordered by longest first to avoid mismatches)
    let suffixes = [".fastq.gz", ".fasta.gz", "fna.gz", "fnq.gz", ".fq.gz", ".fastq", ".fasta", ".fnq", ".fna", ".fa", ".fq"];

    for suffix in suffixes.iter() {
        if filename.ends_with(suffix) {
            return filename.trim_end_matches(suffix).to_string();
        }
    }

    // fallback: remove only the final extension
    Path::new(filename)
        .file_stem()
        .and_then(|s| s.to_str())
        .unwrap_or("unknown")
        .to_string()
}

pub fn canonicalize_file_paths(paths: &[String]) -> Vec<String> {
    paths
        .iter()
        .map(|p| {
            fs::canonicalize(p)
                .map(|path_buf| path_buf.to_string_lossy().into_owned())
                .unwrap_or_else(|e| {
                    error!("{} | {} path does not exist or is inaccessible", e, p);
                    std::process::exit(1);
                })
        })
        .collect()
}

pub fn log_memory_usage(info: bool, message: &str) {
    if let Some(usage) = memory_stats() {
        if info{
            log::info!(
                "{} --- Memory usage: {:.2} GB",
                message,
                usage.physical_mem as f64 / 1_000_000_000.
            );
        }
        else{
            log::debug!(
                "{} --- Memory usage: {:.2} GB",
                message,
                usage.physical_mem as f64 / 1_000_000_000.
            );
        }
    }
    else{
        log::info!("Memory usage: unknown (WARNING)");
    }
}
