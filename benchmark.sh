#!/bin/bash

GENOME=/home/Users/rdd4/bronko-test/bronko_test/build_benchmark/data/random_genomes/1000000.fasta
READS=/home/Users/rdd4/bronko-test/bronko_test/build_benchmark/data/random_genome_seq_data/1000x/1000000.fastq
OLD=~/bronko_benchmark/bronko-test/old_bronko/target/release/bronko
NEW=~/bronko_benchmark/bronko-test/target/release/bronko
THREADS=30
RESULTS_CSV=~/bronko_benchmark/results.csv
GENOME_SIZE=1000000

# create csv with header if it doesn't exist
if [ ! -f $RESULTS_CSV ]; then
    echo "genome_size,version,time_ms,peak_memory_kb" > $RESULTS_CSV
fi

echo "==============================="
echo "running OLD bronko..."
echo "==============================="
/usr/bin/time -v $OLD call -g $GENOME -r $READS -o /tmp/out_old -t $THREADS -k 21 2>/tmp/old_time.txt
old_time=$(grep "wall clock" /tmp/old_time.txt | awk '{print $NF}' | awk -F: '{print ($1*60+$2)*1000}')
old_mem=$(grep "Maximum resident" /tmp/old_time.txt | awk '{print $NF}')
echo "OLD bronko time: ${old_time}ms, peak memory: ${old_mem}kb"
echo "$GENOME_SIZE,old,$old_time,$old_mem" >> $RESULTS_CSV

echo ""
echo "==============================="
echo "running NEW bronko..."
echo "==============================="
/usr/bin/time -v $NEW call -g $GENOME -r $READS -o /tmp/out_new -t $THREADS -k 21 2>/tmp/new_time.txt
new_time=$(grep "wall clock" /tmp/new_time.txt | awk '{print $NF}' | awk -F: '{print ($1*60+$2)*1000}')
new_mem=$(grep "Maximum resident" /tmp/new_time.txt | awk '{print $NF}')
echo "NEW bronko time: ${new_time}ms, peak memory: ${new_mem}kb"
echo "$GENOME_SIZE,new,$new_time,$new_mem" >> $RESULTS_CSV

echo ""
echo "==============================="
echo "RESULTS"
echo "==============================="
echo "OLD: ${old_time}ms, ${old_mem}kb"
echo "NEW: ${new_time}ms, ${new_mem}kb"
speedup=$(echo "scale=2; $old_time / $new_time" | bc)
echo "Speedup: ${speedup}x"

echo ""
echo "==============================="
echo "comparing outputs..."
echo "==============================="
diff /tmp/out_old /tmp/out_new && echo "outputs are IDENTICAL" || echo "outputs DIFFER"

echo ""
echo "results saved to $RESULTS_CSV"
