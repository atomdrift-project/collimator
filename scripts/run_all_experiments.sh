#!/bin/bash
set -u

DB="${DB:-postgres://hopper@localhost:5432/hopper}"
TRAIN_SAMPLES=75000
TEST_SAMPLES=30000
WORKERS=8
SEED=42

run() {
    NAME=$1
    shift
    echo "Running Experiment: $NAME"
    .venv/bin/python -u -m collimator experiment \
        --db "$DB" \
        --train-samples "$TRAIN_SAMPLES" \
        --max-test-samples "$TEST_SAMPLES" \
        --n-folds 2 \
        --seed "$SEED" \
        --workers "$WORKERS" \
        "$@" > "out/exp_${NAME}.log" 2>&1
}

# Exp Baseline
run "baseline" --n-estimators 600 --max-depth 10 --learning-rate 0.02 --early-stopping-rounds 100

# Exp 7 Deeper Slower
run "exp7" --n-estimators 1000 --max-depth 14 --learning-rate 0.01 --early-stopping-rounds 100

# Exp 10 Stochastic
run "exp10" --n-estimators 600 --max-depth 10 --learning-rate 0.02 --early-stopping-rounds 100 --colsample-bytree 0.5 --subsample 0.5

# Exp 11 Heavy Regularization
run "exp11" --n-estimators 600 --max-depth 10 --learning-rate 0.02 --early-stopping-rounds 100 --reg-lambda 10 --gamma 1.0

# Exp 12 High Depth and Reg
run "exp12" --n-estimators 800 --max-depth 12 --learning-rate 0.02 --early-stopping-rounds 100 --reg-lambda 5 --gamma 0.5

# Exp 8 Rare Path Signal (MIN_PATH_FREQ=10)
echo "Setting MIN_PATH_FREQ=10"
sed -i 's/MIN_PATH_FREQ = 30/MIN_PATH_FREQ = 10/' src/collimator/features.py
run "exp8" --n-estimators 600 --max-depth 10 --learning-rate 0.02 --early-stopping-rounds 100
sed -i 's/MIN_PATH_FREQ = 10/MIN_PATH_FREQ = 30/' src/collimator/features.py

# Exp 9 High-Conf Only (MIN_CONFIDENCE=0.85)
echo "Setting MIN_CONFIDENCE=0.85"
sed -i 's/MIN_CONFIDENCE = 0.65/MIN_CONFIDENCE = 0.85/' src/collimator/features.py
run "exp9" --n-estimators 600 --max-depth 10 --learning-rate 0.02 --early-stopping-rounds 100
sed -i 's/MIN_CONFIDENCE = 0.85/MIN_CONFIDENCE = 0.65/' src/collimator/features.py

# Exp 13 Deep Path Signal (min(len(parts), 5))
echo "Setting path depth to 5"
sed -i 's/min(len(parts), 3)/min(len(parts), 5)/' src/collimator/features.py
run "exp13" --n-estimators 600 --max-depth 10 --learning-rate 0.02 --early-stopping-rounds 100
sed -i 's/min(len(parts), 5)/min(len(parts), 3)/' src/collimator/features.py
