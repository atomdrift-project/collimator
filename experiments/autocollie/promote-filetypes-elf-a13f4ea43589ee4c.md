# Promote REJECTED — `a13f4ea43589ee4c` on `filetypes/elf`

Generated 2026-05-25T18:18:24Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-25T18-14-32_20260525T181430-promote-a13f4ea43589ee4c_azoth-validate.log; tail: computing dev-partition metrics (strategy selection)
loaded cached dev-bucket mask: /home/t/collimator/out/cache/azoth-test-masks/dev-947ff4cebbdd8fe06d90df9b8d8e0e32f498a93413f371a2883896fb3f53512a.npz
dev bucket: 589608/4731967 rows (12.46%)
fitting per-route isotonic calibrators (5-fold CV) over 589608 rows (parallelism=16, cache=out/cache/azoth-calibrator)
calibration complete; computing per-filetype metrics
filetypes/xlsb: 0 rows in score table; skipping
filetypes/pyproject.toml: 0 rows in score table; skipping
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-elf-a13f4ea43589ee4c/per_filetype_metrics.json (filetypes: 79, filegroups: 0)
.venv/bin/python scripts/azoth_route_policy_eval.py \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-elf-a13f4ea43589ee4c/score_table.npz \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filetypes-elf-a13f4ea43589ee4c/general/threshold_scores.npz \
	--route-policies /home/t/collimator/out/models/azoth-candidate-filetypes-elf-a13f4ea43589ee4c/route_policies.json \
	--partition test \
	--output-md /home/t/collimator/out/models/azoth-candidate-filetypes-elf-a13f4ea43589ee4c/route_policy_eval_oof.md \
	--output-json /home/t/collimator/out/models/azoth-candidate-filetypes-elf-a13f4ea43589ee4c/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-elf-a13f4ea43589ee4c/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-elf-a13f4ea43589ee4c/route_policy_eval_oof.md
.venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filetypes-elf-a13f4ea43589ee4c
staged runtime azoth bundle: /tmp/tmp.mdeRDW0bXK
azoth bundle ok: /tmp/tmp.mdeRDW0bXK
--source-bundle out/models/azoth: 1 routes changed → 1 filetypes impacted, 64 unimpacted (drift treated as pre-existing)

ensemble improvements (≥0.10pp):
  c: L3 hostile ensemble recall +2.49pp (10.02% → 12.51%)
  javascript: L3 hostile ensemble recall +9.33pp (66.20% → 75.53%)
  package.json: L3 hostile ensemble recall +2.68pp (86.78% → 89.46%)
  xml: L3 hostile ensemble recall +6.16pp (2.74% → 8.90%)

per-route improvements (≥0.10pp, informational):
  elf :: filetypes/elf recall@3FP/M +3.01pp (93.40% → 96.42%)
  go :: filetypes/go recall@3FP/M +0.59pp (4.84% → 5.44%)
  javascript :: filetypes/javascript recall@3FP/M +12.81pp (65.71% → 78.52%)
  package.json :: filegroups/config recall@3FP/M +0.83pp (98.71% → 99.54%)
  xml :: filegroups/config recall@3FP/M +12.33pp (3.42% → 15.75%)

4 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + c: L3 hostile ensemble recall +2.49pp above LWM (10.02% → 12.51%)
  + javascript: L3 hostile ensemble recall +9.33pp above LWM (66.20% → 75.53%)
  + package.json: L3 hostile ensemble recall +2.68pp above LWM (86.78% → 89.46%)
  + xml: L3 hostile ensemble recall +6.16pp above LWM (2.74% → 8.90%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - elf: L3 hostile ENSEMBLE recall dropped 1.29pp BELOW LOW-WATER-MARK (92.79% → 91.50%; LWM tolerance 0.90pp)

compared 63 filetypes (mal≥1, ben≥1); 2 below threshold and skipped.

blocked by: low-water-mark gate (0.90pp vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1136: azoth-validate] Error 1)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 1.0000)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `a13f4ea43589ee4c` | `8ef34c82f2c457d3` | `20ec992d1689b4a8` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 1.0000 | 1.0000 | 1.0000 |
| F1 | 0.9970 | 0.9988 | 0.9989 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-25T18-14-32_20260525T181430-promote-a13f4ea43589ee4c_azoth-validate.log; tail: computing dev-partition metrics (strategy selection)
loaded cached dev-bucket mask: /home/t/collimator/out/cache/azoth-test-masks/dev-947ff4cebbdd8fe06d90df9b8d8e0e32f498a93413f371a2883896fb3f53512a.npz
dev bucket: 589608/4731967 rows (12.46%)
fitting per-route isotonic calibrators (5-fold CV) over 589608 rows (parallelism=16, cache=out/cache/azoth-calibrator)
calibration complete; computing per-filetype metrics
filetypes/xlsb: 0 rows in score table; skipping
filetypes/pyproject.toml: 0 rows in score table; skipping
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-elf-a13f4ea43589ee4c/per_filetype_metrics.json (filetypes: 79, filegroups: 0)
.venv/bin/python scripts/azoth_route_policy_eval.py \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-elf-a13f4ea43589ee4c/score_table.npz \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filetypes-elf-a13f4ea43589ee4c/general/threshold_scores.npz \
	--route-policies /home/t/collimator/out/models/azoth-candidate-filetypes-elf-a13f4ea43589ee4c/route_policies.json \
	--partition test \
	--output-md /home/t/collimator/out/models/azoth-candidate-filetypes-elf-a13f4ea43589ee4c/route_policy_eval_oof.md \
	--output-json /home/t/collimator/out/models/azoth-candidate-filetypes-elf-a13f4ea43589ee4c/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-elf-a13f4ea43589ee4c/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-elf-a13f4ea43589ee4c/route_policy_eval_oof.md
.venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filetypes-elf-a13f4ea43589ee4c
staged runtime azoth bundle: /tmp/tmp.mdeRDW0bXK
azoth bundle ok: /tmp/tmp.mdeRDW0bXK
--source-bundle out/models/azoth: 1 routes changed → 1 filetypes impacted, 64 unimpacted (drift treated as pre-existing)

ensemble improvements (≥0.10pp):
  c: L3 hostile ensemble recall +2.49pp (10.02% → 12.51%)
  javascript: L3 hostile ensemble recall +9.33pp (66.20% → 75.53%)
  package.json: L3 hostile ensemble recall +2.68pp (86.78% → 89.46%)
  xml: L3 hostile ensemble recall +6.16pp (2.74% → 8.90%)

per-route improvements (≥0.10pp, informational):
  elf :: filetypes/elf recall@3FP/M +3.01pp (93.40% → 96.42%)
  go :: filetypes/go recall@3FP/M +0.59pp (4.84% → 5.44%)
  javascript :: filetypes/javascript recall@3FP/M +12.81pp (65.71% → 78.52%)
  package.json :: filegroups/config recall@3FP/M +0.83pp (98.71% → 99.54%)
  xml :: filegroups/config recall@3FP/M +12.33pp (3.42% → 15.75%)

4 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + c: L3 hostile ensemble recall +2.49pp above LWM (10.02% → 12.51%)
  + javascript: L3 hostile ensemble recall +9.33pp above LWM (66.20% → 75.53%)
  + package.json: L3 hostile ensemble recall +2.68pp above LWM (86.78% → 89.46%)
  + xml: L3 hostile ensemble recall +6.16pp above LWM (2.74% → 8.90%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - elf: L3 hostile ENSEMBLE recall dropped 1.29pp BELOW LOW-WATER-MARK (92.79% → 91.50%; LWM tolerance 0.90pp)

compared 63 filetypes (mal≥1, ben≥1); 2 below threshold and skipped.

blocked by: low-water-mark gate (0.90pp vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1136: azoth-validate] Error 1)
