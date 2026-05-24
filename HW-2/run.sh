#!/bin/bash
TRACES_DIR="/mnt/storage/mipt/microarch/data/traces"
BINARY="/mnt/storage/mipt/microarch/third-party/ChampSim/bin/champsim"
PREDICTOR="bimodal"

BASE_DIR="/mnt/storage/mipt/microarch/HW-2"
RESULTS_DIR="${BASE_DIR}/results-${PREDICTOR}"
THREADS=12

mkdir -p $RESULTS_DIR

run_sim() {
    TRACE_PATH=$1
    BINARY=$2
    RESULTS_DIR=$3
    TRACE_NAME=$(basename $TRACE_PATH | cut -d'-' -f1)
    
    echo "Starting $TRACE_NAME..."
    $BINARY --warmup_instructions 10000000 --simulation_instructions 50000000 $TRACE_PATH > "$RESULTS_DIR/${TRACE_NAME}.log"
    echo "Finished $TRACE_NAME"
}

export -f run_sim

ls $TRACES_DIR/*.xz | xargs -n 1 -P $THREADS -I {} bash -c 'run_sim "{}" "'$BINARY'" "'$RESULTS_DIR'"'

echo "Done. All traces for $PREDICTOR finished. Results are in $RESULTS_DIR"