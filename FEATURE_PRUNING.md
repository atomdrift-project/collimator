# Feature pruning (the allowlist) — workflow & automation

The azoth feature matrix is ~76k columns but **~90% are never split on** by any
deployed model, and the LightGBM fit's memory/time scales with *feature count*,
not data. Pruning the vocabulary to the features that matter is therefore a
"less memory, same-or-better quality" lever — the opposite of row/benign
subsampling (which removes signal by default).

Measured: a deployed general model uses ~5.2k of 76k features; the union across
all deployed route models is ~9.6%. An importance-union allowlist of ~12–15k
features matched/improved quality (PE A-B: AUC/AP identical, tail R@10FP/R@1e-4
*up*) while cutting the fit. Reproduce with `scripts/azoth_allowlist_experiment.py`
(the `--prepare` + `--level` / `--committed` A-B harness).

## How it plugs in

Training reads `COLLIMATOR_ALLOWED_FEATURES_FILE` (a JSON
`{"significant_features": [...]}` or bare list); `features.allowed_features()`
restricts the vocab to it. Two non-obvious wiring facts (both bit us once):

- The `experiment` target plumbs it through **`EXP_ALLOWED_FEATURES_FILE`**, not
  the global var (its recipe re-asserts `COLLIMATOR_ALLOWED_FEATURES_FILE`).
- The `general` route **replays a frozen "best idea"** whose captured env pins
  the allowlist empty, so the Makefile pin is overridden. `azoth-general` now
  injects `--set EXP_ALLOWED_FEATURES_FILE=$(abspath …)` (caller-wins layer) so
  the global allowlist actually reaches general. Use `EXP_RERUN=1` to force the
  replay to re-run.

The matrix cache key hashes the allowlist **content** (not just its path), so
overwriting a fixed pin path with new content correctly invalidates the cache.

## Commands

| command | what it does | mutates? |
|---|---|---|
| `make azoth-build-allowlist` | regenerate `importance(deployed bundle) ∪ frequency-floor(live DB)` at `AZOTH_ALLOWLIST_SIZE` | writes a candidate file |
| `make azoth-allowlist-tune` | sweep `AZOTH_TUNE_LEVELS` on proxy routes, write the SMALLEST passing `AZOTH_TUNE_TOLERANCE` | writes a candidate file |
| `make azoth-allowlist-monitor` | score the CURRENT pin on proxy routes → `OK`/`RE-TUNE` | read-only |
| `make azoth-full-train AZOTH_ALLOWED_FEATURES_FILE=<candidate> EXP_RERUN=1` | train + **gate** (`check_azoth_regression`) before deploy | gated adoption |

`scripts/azoth_allowlist_experiment.py` is the kernel behind tune/monitor:
`--prepare` caches the proxy-route matrices once (~minutes), then each `--level`
refit is ~30s, so a full sweep fits the ≤10-min experiment budget.

## The allowlist as a self-calibrating set

- **Frequency floor** re-learns every run for free (the vocab is recounted from
  the corpus each train). It admits *new* frequent features, so the set can
  discover features no model has used yet — the antidote to ossification.
- **Importance set** needs a trained model, so it self-updates with a one-cycle
  lag (this run derives from the last deployed bundle). `importance ∪ floor` is
  self-healing rather than self-confirming.

So the *set* tracks the data automatically; only the *level* (aggressiveness)
needs choosing, and that's a memory-vs-tail tradeoff only the FP/100M gate can
settle — i.e. autocollie's job, not a pinned constant.

## Automation loop (for autocollie)

Treat the global allowlist as a **virtual route** — one shared artifact, one
optimization target, distinct from the per-filetype routes:

1. **Trigger** — `azoth-allowlist-monitor` after each deploy cycle (piggyback
   the train's extraction to make it ~free). If `worst_dR@1e-3` at the pin
   crosses tolerance, raise "re-tune".
2. **Sweep** — `azoth-allowlist-tune` picks the smallest passing level → a
   candidate pin. (Proxy screens coarse quality only — it cannot resolve L50.)
3. **Gate** — `azoth-full-train` with the candidate runs `check_azoth_regression`
   (OOF + Clopper-Pearson L50 hostile recall). **This is the only thing that may
   move the pin.**
4. **Promote** — on gate-pass, write the candidate to the active pin path. The
   pin moving re-arms the monitor next cycle.

Two invariants: **adoption is always gated** (quality can't regress), and a
**dead-band / hysteresis** on the level (the quality curve is a broad flat
plateau, so only move the pin when meaningfully better) prevents churn.

Keep collimator's committed default as the reproducible *bootstrap*; let
autocollie evolve the *active* pin through the gate. Never auto-adopt from the
proxy — the metric it can't measure (the L50 tail) is the one that matters most.
