#!/bin/bash

GENOME=/home/Users/rdd4/bronko-test/bronko_test/build_benchmark/data/random_genomes/1000000.fasta
READS=/home/Users/rdd4/bronko-test/bronko_test/build_benchmark/data/random_genome_seq_data/1000x/1000000.fastq
OLD=~/bronko_benchmark/bronko-test/old_bronko/target/release/bronko
NEW=~/bronko_benchmark/bronko-test/target/release/bronko
THREADS=30

echo "==============================="
echo "running OLD bronko..."
echo "==============================="
start_old=$(date +%s%N)
$OLD call -g $GENOME -r $READS -o /tmp/out_old -t $THREADS -k 21
end_old=$(date +%s%N)
old_time=$(( (end_old - start_old) / 1000000 ))
echo "OLD bronko time: ${old_time}ms"

echo ""
echo "==============================="
echo "running NEW bronko..."
echo "==============================="
start_new=$(date +%s%N)
$NEW call -g $GENOME -r $READS -o /tmp/out_new -t $THREADS -k 21
end_new=$(date +%s%N)
new_time=$(( (end_new - start_new) / 1000000 ))
echo "NEW bronko time: ${new_time}ms"

echo ""
echo "==============================="
echo "RESULTS"
echo "==============================="
echo "OLD: ${old_time}ms"
echo "NEW: ${new_time}ms"
speedup=$(echo "scale=2; $old_time / $new_time" | bc)
echo "Speedup: ${speedup}x"

echo ""
echo "==============================="
echo "comparing outputs..."
echo "==============================="
diff /tmp/out_old /tmp/out_new && echo "outputs are IDENTICAL" || echo "outputs DIFFER"
