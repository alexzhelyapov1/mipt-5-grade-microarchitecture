#!/bin/bash

TRACES_DIR="/mnt/storage/mipt/microarch/data/traces"
CHAMPSIM_DIR="/mnt/storage/mipt/microarch/third-party/ChampSim"
HW3_DIR="/mnt/storage/mipt/microarch/HW-3"
CONFIG_FILE="champsim_config.json"
THREADS=12

POLICIES=("lru" "plru" "srrip" "lru_lip" "lru_bip")

mkdir -p "$HW3_DIR"

if ! command -v jq &> /dev/null; then
    echo "Ошибка: утилита 'jq' не установлена. Пожалуйста, установите её: sudo apt install jq"
    exit 1
fi

run_sim() {
    TRACE_PATH=$1
    BINARY=$2
    RESULTS_DIR=$3
    TRACE_NAME=$(basename $TRACE_PATH | cut -d'-' -f1)
    
    echo "Starting $TRACE_NAME with $(basename $BINARY)..."
    $BINARY --warmup_instructions 5000000 --simulation_instructions 25000000 $TRACE_PATH > "$RESULTS_DIR/${TRACE_NAME}.log"
}
export -f run_sim

cd "$CHAMPSIM_DIR" || exit 1

for POLICY in "${POLICIES[@]}"; do
    echo "========================================================"
    echo "  Building and running ChampSim for L2 Policy: $POLICY"
    echo "========================================================"

    jq ".L2C.replacement = \"$POLICY\"" $CONFIG_FILE > tmp.json && mv tmp.json $CONFIG_FILE

    ./config.sh $CONFIG_FILE
    make -j$THREADS

    if [ ! -f bin/champsim ]; then
        echo "Ошибка компиляции для политики $POLICY! Остановка скрипта."
        exit 1
    fi

    BINARY="$HW3_DIR/champsim_${POLICY}"
    mv bin/champsim "$BINARY"

    RESULTS_DIR="$HW3_DIR/results_${POLICY}"
    mkdir -p "$RESULTS_DIR"

    echo "Running traces for $POLICY..."
    ls $TRACES_DIR/*.xz | xargs -n 1 -P $THREADS -I {} bash -c 'run_sim "{}" "'$BINARY'" "'$RESULTS_DIR'"'

    echo "Finished all traces for $POLICY."
    echo ""
done

echo "========================================================"
echo "  All policies tested successfully! Simulations done."
echo "========================================================"