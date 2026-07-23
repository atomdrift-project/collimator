# Contributing to collimator

Thanks for the interest. This file is the operator manual for proposing
changes — what's expected, what gates a PR, where to look first.

## Environment setup

```fish
# Python venv (uses pyproject.toml)
make venv

# Confirm tests pass on a fresh clone
.venv/bin/python -m pytest

# Lint + type check (CI runs both)
make lint
```

You'll also need a `hopper` database. For development, point at a SQLite
demo DB:

```fish
make demo-db
make azoth-fast-train DB=sqlite:///$(pwd)/out/demo.db WORKERS=4
```

For real workloads, point at a PostgreSQL `hopper` DSN.

## What we measure

Every change should preserve or improve at least one of:

- **Hostile recall at L50** under the global FP/100M ≤ 50 budget (= 0.5
  FP/M, the default deployed operating point). Reported in
  `global_policy_metrics.md` after `make azoth-deploy`.
- **Per-route ensemble F1/AUC** for the route(s) you touched. Reported in
  `ENSEMBLE_MODEL.md` and the per-route `README.md` under the deployed bundle.
- **Wall-clock training cost** for the part of the pipeline you touched.
  Don't trade hours of training for fractions of a percent.

If a change improves nothing measurable, it should be a cleanup or
correctness fix that's clearly explained in the PR.

## Proposing a feature experiment

The fastest path is to add a knob that's already in scope:

```fish
make experiment EXP_ROUTE=filetypes/python \
                EXP_IDEA=my-idea \
                EXP_FORMAT_HINTS=1 \
                EXP_NUM_LEAVES=128 \
                DB=postgres://...
```

This produces `out/experiments/azoth/runs/<key>.json` with the run summary.
Compare to recent best-of-route runs; if it's a meaningful improvement
(per the metrics above), open a PR that:

1. Updates `experiments/<your-tranche>.md` with the idea, method, and result.
2. Adds the knob to `autocollie/knobs.json` if it's a new feature toggle.
3. Adds tests if the change involves new code paths in `src/collimator/`.

For changes that need a new feature family (new C-side cleave trait, new
n-gram source, etc.), the work spans cleave → hopper → collimator. Open
issues against each repo with linked context.

## What gates a PR

- `pytest` passes (CI runs the full suite plus litmus integration).
- `make lint` passes (ruff + mypy).
- For changes to `src/collimator/bundle.py`, `experiment.py`,
  `train.py`, or anything in the deploy chain: at minimum a unit test
  pinning the new behavior; bonus for a smoke test that exercises the
  full `make azoth-fast-train` flow against the demo DB.
- For changes to the litmus runtime contract (bundle layout, calibrator
  schema, route policy schema): an accompanying PR to litmus that updates
  its loader, **and** confirmation that `make azoth-deploy` runs to
  completion (including the litmus-parity step) on a real bundle.
- Document the WHY (PR description), not the WHAT (the diff is the what).
  We especially want to see: what alternative did you consider, and why
  did you pick this one?

## Where to look first

| Question | Look here |
|---|---|
| "How does the routing decision get made?" | `out/models/azoth/ENSEMBLE_MODEL.md`, then `litmus/src/model.rs::predict_for`. |
| "Where does the calibrator come from?" | `scripts/azoth_calibrate_ensemble.py::_fit_and_persist_isotonic_calibrator`. Loaded by `litmus/src/model.rs::IsotonicCalibrator`. |
| "How does autocollie know what to try next?" | `../autocollie/skill.md` (the LLM's instruction manual) and the run JSONs under `out/experiments/azoth/runs/`. |
| "Why three different specialist training paths?" | There aren't, anymore — it's `make azoth-{full,fast}-train`. Anything else is internal to that target's chain. |
| "How do I add a new feature family?" | `src/collimator/features.py` for the extractor, `autocollie/knobs.json` for the toggle. Existing families are good templates. |

## Coding style

- Follow `pyproject.toml` (ruff). Keep lines reasonable; no rigid limit but
  if a function gets past ~80 lines, look for a natural split.
- Prefer adding a test over adding a comment that explains a tricky case.
- Comments answer **why**, not what. Identifiers do "what."
- One source of truth per concern. The `bundle.py` module is the canonical
  example: every "where's the model file?" question goes through it.
- `from __future__ import annotations` at the top of every Python file.
- Type-hint public functions; private ones if they take more than two args.

## Reporting issues

Open issues at https://github.com/atomdrift-project/collimator/issues. Useful
information:

- The exact command you ran and its full output (or a tail with the error).
- The deployed bundle's `MODEL.md` if the issue affects scoring.
- For training-time problems: the `out/experiments/azoth/runs/<key>.json`
  for the run that misbehaved.

## License

By submitting a PR, you agree your contribution is licensed under Apache 2.0
(see [LICENSE](LICENSE)).
