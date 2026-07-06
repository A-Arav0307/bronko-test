pub mod cli;
use cli::*;

use crate::consts::BRONKO_VERSION;

pub mod consts;
pub mod call;
pub mod lcb;
pub mod build;
pub mod util;

fn main() {
    println!("bronko v{}", BRONKO_VERSION);
    println!("Developed by Ryan Doughty (Rice University)");
    println!("Correspondence: rdd4@rice.edu, treangen@rice.edu\n");

    let args = cli::parse_args();
    match args.mode {
        Mode::Call(call_args) => call::call(call_args),
        Mode::Build(build_args) => build::build(build_args),
    }
}
