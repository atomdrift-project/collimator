# Promote REJECTED — `f674e3cbd4d8f7fe` on `filegroups/native`

Generated 2026-05-25T18:04:11Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-25T17-52-55_20260525T173914-promote-f674e3cbd4d8f7fe_azoth-validate.log; tail: calibration complete; computing per-filetype metrics
filetypes/xlsb: 0 rows in score table; skipping
computing dev-partition metrics (strategy selection)
loaded cached dev-bucket mask: /home/t/collimator/out/cache/azoth-test-masks/dev-947ff4cebbdd8fe06d90df9b8d8e0e32f498a93413f371a2883896fb3f53512a.npz
dev bucket: 589608/4731967 rows (12.46%)
fitting per-route isotonic calibrators (5-fold CV) over 589608 rows (parallelism=16, cache=out/cache/azoth-calibrator)
calibration complete; computing per-filetype metrics
filetypes/pyproject.toml: 0 rows in score table; skipping
filetypes/xlsb: 0 rows in score table; skipping
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-native-f674e3cbd4d8f7fe/per_filetype_metrics.json (filetypes: 79, filegroups: 0)
.venv/bin/python scripts/azoth_route_policy_eval.py \
	--score-table /home/t/collimator/out/models/azoth-candidate-filegroups-native-f674e3cbd4d8f7fe/score_table.npz \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filegroups-native-f674e3cbd4d8f7fe/general/threshold_scores.npz \
	--route-policies /home/t/collimator/out/models/azoth-candidate-filegroups-native-f674e3cbd4d8f7fe/route_policies.json \
	--partition test \
	--output-md /home/t/collimator/out/models/azoth-candidate-filegroups-native-f674e3cbd4d8f7fe/route_policy_eval_oof.md \
	--output-json /home/t/collimator/out/models/azoth-candidate-filegroups-native-f674e3cbd4d8f7fe/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-native-f674e3cbd4d8f7fe/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-native-f674e3cbd4d8f7fe/route_policy_eval_oof.md
.venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filegroups-native-f674e3cbd4d8f7fe
staged runtime azoth bundle: /tmp/tmp.CrrqLUfT1v
azoth bundle ok: /tmp/tmp.CrrqLUfT1v
--source-bundle out/models/azoth: 1 routes changed → 3 filetypes impacted, 62 unimpacted (drift treated as pre-existing)

ensemble improvements (≥0.10pp):
  c: L3 hostile ensemble recall +2.49pp (10.02% → 12.51%)
  elf: L3 hostile ensemble recall +1.58pp (92.79% → 94.37%)
  javascript: L3 hostile ensemble recall +9.33pp (66.20% → 75.53%)

per-route improvements (≥0.10pp, informational):
  elf :: filegroups/native recall@3FP/M +11.04pp (86.66% → 97.70%)
  go :: filetypes/go recall@3FP/M +0.59pp (4.84% → 5.44%)
  javascript :: filetypes/javascript recall@3FP/M +12.81pp (65.71% → 78.52%)
  macho :: filegroups/native recall@3FP/M +20.23pp (69.08% → 89.31%)
  pe :: filegroups/native recall@3FP/M +5.74pp (59.94% → 65.68%)

3 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + c: L3 hostile ensemble recall +2.49pp above LWM (10.02% → 12.51%)
  + elf: L3 hostile ensemble recall +1.58pp above LWM (92.79% → 94.37%)
  + javascript: L3 hostile ensemble recall +9.33pp above LWM (66.20% → 75.53%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - pe: L3 hostile ENSEMBLE recall dropped 3.67pp BELOW LOW-WATER-MARK (61.96% → 58.29%; LWM tolerance 0.90pp)

compared 63 filetypes (mal≥1, ben≥1); 2 below threshold and skipped.

blocked by: deployed-tolerance gate (1.70pp), low-water-mark gate (0.90pp vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1136: azoth-validate] Error 1)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9995)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `f674e3cbd4d8f7fe` | `716c3364b8fc39b9` | `fea7eba2225b4bf3` |
| PR AUC | 0.9995 | 1.0000 | 1.0000 |
| ROC AUC | 0.9995 | 1.0000 | 1.0000 |
| F1 | 0.0000 | 0.9525 | 0.9478 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-25T17-52-55_20260525T173914-promote-f674e3cbd4d8f7fe_azoth-validate.log; tail: calibration complete; computing per-filetype metrics
filetypes/xlsb: 0 rows in score table; skipping
computing dev-partition metrics (strategy selection)
loaded cached dev-bucket mask: /home/t/collimator/out/cache/azoth-test-masks/dev-947ff4cebbdd8fe06d90df9b8d8e0e32f498a93413f371a2883896fb3f53512a.npz
dev bucket: 589608/4731967 rows (12.46%)
fitting per-route isotonic calibrators (5-fold CV) over 589608 rows (parallelism=16, cache=out/cache/azoth-calibrator)
calibration complete; computing per-filetype metrics
filetypes/pyproject.toml: 0 rows in score table; skipping
filetypes/xlsb: 0 rows in score table; skipping
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-native-f674e3cbd4d8f7fe/per_filetype_metrics.json (filetypes: 79, filegroups: 0)
.venv/bin/python scripts/azoth_route_policy_eval.py \
	--score-table /home/t/collimator/out/models/azoth-candidate-filegroups-native-f674e3cbd4d8f7fe/score_table.npz \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filegroups-native-f674e3cbd4d8f7fe/general/threshold_scores.npz \
	--route-policies /home/t/collimator/out/models/azoth-candidate-filegroups-native-f674e3cbd4d8f7fe/route_policies.json \
	--partition test \
	--output-md /home/t/collimator/out/models/azoth-candidate-filegroups-native-f674e3cbd4d8f7fe/route_policy_eval_oof.md \
	--output-json /home/t/collimator/out/models/azoth-candidate-filegroups-native-f674e3cbd4d8f7fe/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-native-f674e3cbd4d8f7fe/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-native-f674e3cbd4d8f7fe/route_policy_eval_oof.md
.venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filegroups-native-f674e3cbd4d8f7fe
staged runtime azoth bundle: /tmp/tmp.CrrqLUfT1v
azoth bundle ok: /tmp/tmp.CrrqLUfT1v
--source-bundle out/models/azoth: 1 routes changed → 3 filetypes impacted, 62 unimpacted (drift treated as pre-existing)

ensemble improvements (≥0.10pp):
  c: L3 hostile ensemble recall +2.49pp (10.02% → 12.51%)
  elf: L3 hostile ensemble recall +1.58pp (92.79% → 94.37%)
  javascript: L3 hostile ensemble recall +9.33pp (66.20% → 75.53%)

per-route improvements (≥0.10pp, informational):
  elf :: filegroups/native recall@3FP/M +11.04pp (86.66% → 97.70%)
  go :: filetypes/go recall@3FP/M +0.59pp (4.84% → 5.44%)
  javascript :: filetypes/javascript recall@3FP/M +12.81pp (65.71% → 78.52%)
  macho :: filegroups/native recall@3FP/M +20.23pp (69.08% → 89.31%)
  pe :: filegroups/native recall@3FP/M +5.74pp (59.94% → 65.68%)

3 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + c: L3 hostile ensemble recall +2.49pp above LWM (10.02% → 12.51%)
  + elf: L3 hostile ensemble recall +1.58pp above LWM (92.79% → 94.37%)
  + javascript: L3 hostile ensemble recall +9.33pp above LWM (66.20% → 75.53%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - pe: L3 hostile ENSEMBLE recall dropped 3.67pp BELOW LOW-WATER-MARK (61.96% → 58.29%; LWM tolerance 0.90pp)

compared 63 filetypes (mal≥1, ben≥1); 2 below threshold and skipped.

blocked by: deployed-tolerance gate (1.70pp), low-water-mark gate (0.90pp vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1136: azoth-validate] Error 1)
