#!/usr/bin/env bash
# Shared memory admission for the unattended train and sweep.
# Budgets include 48 GB of host reserve and 48 GB per resident training.
# The last successful two-chain run peaked at 76 GB; leave room for growth.
mem_avail_gb() {
    awk '/^MemAvailable:/ { printf "%.0f", $2/1024/1024; found=1 } END { if (!found) exit 1 }' /proc/meminfo
}

wait_for_azoth_memory() {
    local required=$1 available waited=0
    local max_wait=${AZOTH_MEMORY_WAIT_SECONDS:-21600}
    local interval=${AZOTH_MEMORY_POLL_SECONDS:-60}
    if ! [[ $required =~ ^[1-9][0-9]*$ && $max_wait =~ ^[0-9]+$ && $interval =~ ^[1-9][0-9]*$ ]]; then
        echo "ERROR: invalid Azoth memory admission settings" >&2
        return 1
    fi
    while true; do
        available=$(mem_avail_gb) || available=unknown
        if [[ $available =~ ^[0-9]+$ ]] && (( available >= required )); then
            echo "[memory] admitted: ${available} GB available, ${required} GB required"
            return 0
        fi
        if (( waited >= max_wait )); then
            echo "ERROR: memory admission timed out after ${waited}s (${available} GB available, ${required} GB required)" >&2
            return 1
        fi
        echo "[memory] waiting: ${available} GB available, ${required} GB required (${waited}/${max_wait}s)"
        local delay=$interval
        (( delay > max_wait - waited )) && delay=$(( max_wait - waited ))
        sleep "$delay"
        waited=$(( waited + delay ))
    done
}

azoth_parallel_memory_ok() {
    local available required=${AZOTH_PARALLEL_MIN_AVAILABLE_GB:-144}
    [[ $required =~ ^[1-9][0-9]*$ ]] || return 1
    available=$(mem_avail_gb) || return 1
    [[ $available =~ ^[0-9]+$ ]] && (( available >= required ))
}
