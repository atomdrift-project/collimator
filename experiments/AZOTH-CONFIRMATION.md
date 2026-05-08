# Azoth Confirmation Plan

Created: 2026-05-07

Goal: separate screening wins from deployable wins. A sampled F1/AUC win is only
an invitation to confirm. Promotion requires routed full-corpus policy metrics at
the active FP budget and litmus feature parity.

## Candidate Order

1. `shell_kv_metric_vocab_wide` (`409805a4e6219218`)
   - Why: shell sampled F1 0.9859 vs deployed shell F1 0.9465.
   - Risk: uses experimental `kv` and `textenc`; litmus parity required.
2. `package_json_kv_lifecycle_textenc` (`0f85c7e43d7ff625`)
   - Why: small lift over already-strong deployed package.json.
   - Risk: likely a precision/detail win; must show routed improvement.
3. `documents_textenc_kv_static` (`c8ece36bb498112a`)
   - Why: documents group sampled F1 0.9920 with compact feature count.
   - Risk: broad group may hide weak filetypes.
4. `media_textenc_kv_carrier` (`2a27e207e4f656b0`)
   - Why: media sampled F1 0.9867; metadata-only variant nearly tied.
   - Risk: route value depends on corpus volume and FP budget.
5. `elf_symbol_vocab_kv_static` (`24bf8f38f56cfc88`)
   - Why: sampled ELF lift from 0.9958 to 0.9974.
   - Risk: ELF is already strong; route policy may not move much.
6. `general_scoreless_symbol_kv_textenc` (`62b7038fc9d5a8a4`)
   - Why: global sampled F1 0.9960.
   - Risk: previous global sampled wins failed full-corpus FP calibration.
7. `source_formula_density_tax` (`b5af19645438cce3`)
   - Why: older source candidate was much stronger than current source route.
   - Risk: degenerate calibration in screening; needs route confirmation.

## Confirmation Recipe

For each candidate:

1. Re-run the exact candidate recipe at confirmation scale:
   - Same route and feature knobs.
   - `EXP_RERUN=1`, fresh seed only if the first confirmation is noisy.
   - Larger profile: at least `EXP_TRAIN_SAMPLES=200000`,
     `EXP_MAX_TEST_SAMPLES=60000`, `EXP_ESTIMATORS=220` for high-volume routes.
2. If sampled confirmation still wins, train a candidate specialist bundle under
   a separate root, for example `out/models/azoth-confirm-shell-kv`.
3. Rebuild route scores for only the affected route first:
   - `make azoth-calibrate AZOTH_ROOT=<candidate-root> AZOTH_REFRESH_ROUTE=<route>`
4. Run route policy search and global policy metrics:
   - `make azoth-policies AZOTH_ROOT=<candidate-root> AZOTH_POLICY_OVERRIDE_ROUTE=<route>`
   - `make azoth-diagnostics AZOTH_ROOT=<candidate-root>`
5. Promote only if the candidate improves the route and does not regress global
   policy at L3 hostile. Suspicious is secondary.
6. If the candidate uses `symbols`, `kv`, or `textenc`, implement and test litmus
   extraction parity before deployment.

## Stop Rules

- Reject a candidate that improves sampled F1 but loses routed L3 hostile recall.
- Reject a candidate that increases full-corpus FP/M over budget.
- Reject a feature family that cannot be implemented cheaply in litmus.
- Keep exact experiment keys in the log; do not promote from timestamped logs.
