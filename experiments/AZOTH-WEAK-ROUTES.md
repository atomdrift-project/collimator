# Azoth Weak Route Experiments

Created: 2026-05-06

Script:

```sh
scripts/run_azoth_weak_route_tranche.sh
```

Purpose: probe weak/high-volume routes with the standard fast experiment profile
before promoting anything into deployable specialists.

Routes:

- `filetypes/pe`
- `filetypes/javascript`
- `filetypes/python`
- `filegroups/scripts`
- `filetypes/macho`

Profile:

- `EXP_WORKERS=64`
- `EXP_TRAIN_SAMPLES=150000`
- `EXP_MAX_TEST_SAMPLES=40000`
- `EXP_ESTIMATORS=180`
- `EXP_FOLDS=0`

Outcome log:

- 2026-05-06: tranche defined after adding deploy-time runtime route validation.
- 2026-05-06: `filetypes/pe` / `pe_route_static_tax_no_score`
  (`b0403873e7c267fd`): external F1 0.9965, precision 0.9949,
  recall 0.9981, AUC 0.9998, AP 0.9998, Brier 0.0030; holdout F1
  0.9946. Useful PE candidate, but confirm under routed full-corpus
  calibration before promotion.
- 2026-05-06: `filetypes/pe` / `pe_route_tail_static`
  (`7a0d1f4b702144da`): external F1 0.9969, precision 0.9962,
  recall 0.9976, AUC 0.9998, AP 0.9998, Brier 0.0027; holdout F1
  0.9954. Slightly better PE F1/Brier than `pe_route_static_tax_no_score`,
  but the 150k PE probe took 2496s because the PE matrix is dense
  (~274M nonzeros). Do not use 150k as the default PE iteration size.
- 2026-05-06: `filetypes/javascript` / `javascript_route_hsn8_allcrit`
  (`fe54233e689afa92`): external F1 0.9931, precision 0.9900,
  recall 0.9963, AUC 0.9997, AP 0.9994, Brier 0.0025; holdout F1
  0.9960. This is a credible JavaScript specialist candidate. It should be
  compared against the current deployed JavaScript route under routed
  full-corpus calibration before promotion.
- 2026-05-06: routed full-corpus confirmation for
  `javascript_route_hsn8_allcrit` rejected promotion. Replacing only
  `filetypes/javascript` in `out/models/azoth-confirm-js-fe542` and
  refreshing that route gave lower global recall at the same budgets:
  L3 hostile 62.98% vs baseline 63.59%, L5 hostile 69.42% vs 70.04%,
  L9 hostile 70.64% vs 71.20%. Isolated sampled-test gains did not survive
  ensemble budget allocation.
- 2026-05-06: routed full-corpus confirmation for `pe_route_tail_static`
  rejected promotion. Replacing only `filetypes/pe` in
  `out/models/azoth-confirm-pe-7a0d` and refreshing that route gave much
  lower global recall at the same budgets: L3 hostile 51.45% vs baseline
  63.59%, L5 hostile 57.89% vs 70.04%, L9 hostile 59.05% vs 71.20%.
  The route scorer also showed why PE confirmation is expensive: 423,309 PE
  rows, 564M nonzeros, 644s to refresh scores. Isolated PE sampled-test
  metrics are not reliable promotion evidence under the routed FP budget.
- 2026-05-06: `filetypes/javascript` / `javascript_route_no_score_objectives`
  (`630a5d5da1c4ba04`): external F1 0.9946, precision 0.9942,
  recall 0.9949, AUC 0.9997, AP 0.9995, Brier 0.0023; holdout F1
  0.9968. This is better than `javascript_route_hsn8_allcrit` on isolated
  sampled F1, with a smaller matrix (22,585 features, 68M nonzeros) and
  497s runtime. Needs routed full-corpus confirmation before promotion.
- 2026-05-06: routed full-corpus confirmation for
  `javascript_route_no_score_objectives` rejected promotion. Replacing only
  `filetypes/javascript` in `out/models/azoth-confirm-js-630a` reduced global
  recall at the same budgets: L3 hostile 62.98% vs baseline 63.59%, L5
  hostile 69.42% vs 70.04%, L9 hostile 70.66% vs 71.20%. Better isolated
  JavaScript F1 still did not improve routed ensemble recall.
- 2026-05-06: `filetypes/python` / `python_route_tax_density_depth8`
  (`0325c98f8957861e`): external F1 0.9882, precision 0.9826,
  recall 0.9939, AUC 0.9997, AP 0.9987, Brier 0.0020; holdout F1
  0.9928. Slightly ahead of the no-score H/S/N Python probe on sampled F1
  and recall.
- 2026-05-06: routed full-corpus confirmation for
  `python_route_tax_density_depth8` passed as a small promotion candidate.
  Replacing only `filetypes/python` in `out/models/azoth-confirm-python-0325`
  preserved L3 hostile recall at 63.59% while improving L3 suspicious
  76.97% -> 77.02%; improved L5 hostile 70.04% -> 70.09%; improved L9
  hostile 71.20% -> 71.25%. Same FP budgets. Small, but directionally
  positive and cheap to score (107,449 Python rows refreshed in 6.7s).
- 2026-05-06: promoted `python_route_tax_density_depth8` into
  `out/models/azoth/filetypes/python` and deployed via `make deploy`. Final
  deployed full-corpus metrics: L3 hostile recall 63.59% at 5 FP (2.75/1M),
  L3 suspicious 77.02% at 58 FP (31.84/1M), L5 hostile 70.09% at 9 FP
  (4.94/1M), L9 hostile 71.25% at 16 FP (8.78/1M). Litmus staged runtime
  validation passed with `az`, `az/native`, and `az/elf` scores present.
- 2026-05-06: `filetypes/python` / `python_route_no_score_hsn`
  (`f23e385ae643181f`): external F1 0.9879, precision 0.9849,
  recall 0.9909, AUC 0.9994, AP 0.9982, Brier 0.0024; holdout F1
  0.9891. Not preferred over `python_route_tax_density_depth8`.
- 2026-05-06: `filegroups/scripts` / `scripts_route_hsn8_tail`
  (`cfcf43815bd89495`): external F1 0.9919, precision 0.9926,
  recall 0.9913, AUC 0.9995, AP 0.9993, Brier 0.0040; holdout F1
  0.9953. Runtime was 1434s on 140,273 train rows and 176M nonzeros, so this
  is also confirmation-scale rather than cheap iteration-scale. Needs routed
  full-corpus confirmation before promotion.

Runtime note:

- The standard 150k/40k probe is acceptable for many specialist routes, but
  PE is too dense for the 9-10 minute target. Use a smaller PE probe
  (for example 80k train / 25k external / 120 trees) for idea triage, then
  confirm winners with the larger profile or `make train`.
- `scripts/run_azoth_weak_route_tranche.sh` now applies that smaller PE
  profile by default unless the caller explicitly sets the probe size.
