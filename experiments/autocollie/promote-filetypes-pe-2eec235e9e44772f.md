# Promote REJECTED — `2eec235e9e44772f` on `filetypes/pe`

Generated 2026-05-25T16:37:20Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-25T16-25-33_20260525T162530-promote-2eec235e9e44772f_azoth-validate.log; tail: computing test-partition metrics (reporting)
loaded cached test-bucket mask: /home/t/collimator/out/cache/azoth-test-masks/test-947ff4cebbdd8fe06d90df9b8d8e0e32f498a93413f371a2883896fb3f53512a.npz
test bucket: 588814/4731967 rows (12.44%)
fitting per-route isotonic calibrators (5-fold CV) over 588814 rows (parallelism=16, cache=out/cache/azoth-calibrator)
calibration complete; computing per-filetype metrics
filetypes/xlsb: 0 rows in score table; skipping
computing dev-partition metrics (strategy selection)
loaded cached dev-bucket mask: /home/t/collimator/out/cache/azoth-test-masks/dev-947ff4cebbdd8fe06d90df9b8d8e0e32f498a93413f371a2883896fb3f53512a.npz
dev bucket: 589608/4731967 rows (12.46%)
fitting per-route isotonic calibrators (5-fold CV) over 589608 rows (parallelism=16, cache=out/cache/azoth-calibrator)
calibration complete; computing per-filetype metrics
filetypes/pyproject.toml: 0 rows in score table; skipping
filetypes/xlsb: 0 rows in score table; skipping
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-pe-2eec235e9e44772f/per_filetype_metrics.json (filetypes: 79, filegroups: 0)
.venv/bin/python scripts/azoth_route_policy_eval.py \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-pe-2eec235e9e44772f/score_table.npz \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filetypes-pe-2eec235e9e44772f/general/threshold_scores.npz \
	--route-policies /home/t/collimator/out/models/azoth-candidate-filetypes-pe-2eec235e9e44772f/route_policies.json \
	--partition test \
	--output-md /home/t/collimator/out/models/azoth-candidate-filetypes-pe-2eec235e9e44772f/route_policy_eval_oof.md \
	--output-json /home/t/collimator/out/models/azoth-candidate-filetypes-pe-2eec235e9e44772f/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-pe-2eec235e9e44772f/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-pe-2eec235e9e44772f/route_policy_eval_oof.md
.venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filetypes-pe-2eec235e9e44772f
staged runtime azoth bundle: /tmp/tmp.FGGnyynEfA
azoth bundle ok: /tmp/tmp.FGGnyynEfA
--source-bundle out/models/azoth: 1 routes changed → 1 filetypes impacted, 64 unimpacted (drift treated as pre-existing)

ensemble improvements (≥0.10pp):
  c: L3 hostile ensemble recall +2.49pp (10.02% → 12.51%)
  javascript: L3 hostile ensemble recall +9.33pp (66.20% → 75.53%)

per-route improvements (≥0.10pp, informational):
  go :: filetypes/go recall@3FP/M +0.59pp (4.84% → 5.44%)
  javascript :: filetypes/javascript recall@3FP/M +12.81pp (65.71% → 78.52%)
  pe :: filetypes/pe recall@3FP/M +13.87pp (61.35% → 75.22%)

2 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + c: L3 hostile ensemble recall +2.49pp above LWM (10.02% → 12.51%)
  + javascript: L3 hostile ensemble recall +9.33pp above LWM (66.20% → 75.53%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - pe: L3 hostile ENSEMBLE recall dropped 3.21pp BELOW LOW-WATER-MARK (61.96% → 58.74%; LWM tolerance 0.90pp)

compared 63 filetypes (mal≥1, ben≥1); 2 below threshold and skipped.

blocked by: deployed-tolerance gate (1.70pp), low-water-mark gate (0.90pp vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1136: azoth-validate] Error 1)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9997)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `2eec235e9e44772f` | `5cf06fd239187a04` | `7b8a38aeb675012b` |
| PR AUC | 0.9997 | 1.0000 | 1.0000 |
| ROC AUC | 0.9997 | 0.9999 | 0.9999 |
| F1 | 0.9905 | 0.9990 | 0.9978 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-25T16-25-33_20260525T162530-promote-2eec235e9e44772f_azoth-validate.log; tail: computing test-partition metrics (reporting)
loaded cached test-bucket mask: /home/t/collimator/out/cache/azoth-test-masks/test-947ff4cebbdd8fe06d90df9b8d8e0e32f498a93413f371a2883896fb3f53512a.npz
test bucket: 588814/4731967 rows (12.44%)
fitting per-route isotonic calibrators (5-fold CV) over 588814 rows (parallelism=16, cache=out/cache/azoth-calibrator)
calibration complete; computing per-filetype metrics
filetypes/xlsb: 0 rows in score table; skipping
computing dev-partition metrics (strategy selection)
loaded cached dev-bucket mask: /home/t/collimator/out/cache/azoth-test-masks/dev-947ff4cebbdd8fe06d90df9b8d8e0e32f498a93413f371a2883896fb3f53512a.npz
dev bucket: 589608/4731967 rows (12.46%)
fitting per-route isotonic calibrators (5-fold CV) over 589608 rows (parallelism=16, cache=out/cache/azoth-calibrator)
calibration complete; computing per-filetype metrics
filetypes/pyproject.toml: 0 rows in score table; skipping
filetypes/xlsb: 0 rows in score table; skipping
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-pe-2eec235e9e44772f/per_filetype_metrics.json (filetypes: 79, filegroups: 0)
.venv/bin/python scripts/azoth_route_policy_eval.py \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-pe-2eec235e9e44772f/score_table.npz \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filetypes-pe-2eec235e9e44772f/general/threshold_scores.npz \
	--route-policies /home/t/collimator/out/models/azoth-candidate-filetypes-pe-2eec235e9e44772f/route_policies.json \
	--partition test \
	--output-md /home/t/collimator/out/models/azoth-candidate-filetypes-pe-2eec235e9e44772f/route_policy_eval_oof.md \
	--output-json /home/t/collimator/out/models/azoth-candidate-filetypes-pe-2eec235e9e44772f/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-pe-2eec235e9e44772f/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-pe-2eec235e9e44772f/route_policy_eval_oof.md
.venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filetypes-pe-2eec235e9e44772f
staged runtime azoth bundle: /tmp/tmp.FGGnyynEfA
azoth bundle ok: /tmp/tmp.FGGnyynEfA
--source-bundle out/models/azoth: 1 routes changed → 1 filetypes impacted, 64 unimpacted (drift treated as pre-existing)

ensemble improvements (≥0.10pp):
  c: L3 hostile ensemble recall +2.49pp (10.02% → 12.51%)
  javascript: L3 hostile ensemble recall +9.33pp (66.20% → 75.53%)

per-route improvements (≥0.10pp, informational):
  go :: filetypes/go recall@3FP/M +0.59pp (4.84% → 5.44%)
  javascript :: filetypes/javascript recall@3FP/M +12.81pp (65.71% → 78.52%)
  pe :: filetypes/pe recall@3FP/M +13.87pp (61.35% → 75.22%)

2 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + c: L3 hostile ensemble recall +2.49pp above LWM (10.02% → 12.51%)
  + javascript: L3 hostile ensemble recall +9.33pp above LWM (66.20% → 75.53%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - pe: L3 hostile ENSEMBLE recall dropped 3.21pp BELOW LOW-WATER-MARK (61.96% → 58.74%; LWM tolerance 0.90pp)

compared 63 filetypes (mal≥1, ben≥1); 2 below threshold and skipped.

blocked by: deployed-tolerance gate (1.70pp), low-water-mark gate (0.90pp vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1136: azoth-validate] Error 1)
