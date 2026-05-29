# Promote REJECTED — `1f9ee448fdf4f9e3` on `filegroups/source`

Generated 2026-05-25T15:28:57Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-25T15-22-39_20260525T152235-promote-1f9ee448fdf4f9e3_azoth-validate.log; tail: fitting per-route isotonic calibrators (5-fold CV) over 588814 rows (parallelism=16, cache=out/cache/azoth-calibrator)
calibration complete; computing per-filetype metrics
filetypes/xlsb: 0 rows in score table; skipping
computing dev-partition metrics (strategy selection)
loaded cached dev-bucket mask: /home/t/collimator/out/cache/azoth-test-masks/dev-947ff4cebbdd8fe06d90df9b8d8e0e32f498a93413f371a2883896fb3f53512a.npz
dev bucket: 589608/4731967 rows (12.46%)
fitting per-route isotonic calibrators (5-fold CV) over 589608 rows (parallelism=16, cache=out/cache/azoth-calibrator)
calibration complete; computing per-filetype metrics
filetypes/pyproject.toml: 0 rows in score table; skipping
filetypes/xlsb: 0 rows in score table; skipping
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-source-1f9ee448fdf4f9e3/per_filetype_metrics.json (filetypes: 79, filegroups: 0)
.venv/bin/python scripts/azoth_route_policy_eval.py \
	--score-table /home/t/collimator/out/models/azoth-candidate-filegroups-source-1f9ee448fdf4f9e3/score_table.npz \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filegroups-source-1f9ee448fdf4f9e3/general/threshold_scores.npz \
	--route-policies /home/t/collimator/out/models/azoth-candidate-filegroups-source-1f9ee448fdf4f9e3/route_policies.json \
	--partition test \
	--output-md /home/t/collimator/out/models/azoth-candidate-filegroups-source-1f9ee448fdf4f9e3/route_policy_eval_oof.md \
	--output-json /home/t/collimator/out/models/azoth-candidate-filegroups-source-1f9ee448fdf4f9e3/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-source-1f9ee448fdf4f9e3/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-source-1f9ee448fdf4f9e3/route_policy_eval_oof.md
.venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filegroups-source-1f9ee448fdf4f9e3
staged runtime azoth bundle: /tmp/tmp.NtmfpLAxch
azoth bundle ok: /tmp/tmp.NtmfpLAxch
--source-bundle out/models/azoth: 1 routes changed → 7 filetypes impacted, 58 unimpacted (drift treated as pre-existing)

ensemble improvements (≥0.10pp):
  c: L3 hostile ensemble recall +2.49pp (10.02% → 12.51%)
  kotlin: L3 hostile ensemble recall +4.72pp (52.67% → 57.39%)

per-route improvements (≥0.10pp, informational):
  c :: filegroups/source recall@3FP/M +0.28pp (13.36% → 13.65%)
  rust :: filegroups/source recall@3FP/M +0.61pp (3.05% → 3.66%)

per-route regressions (informational; does not block deploy):
  csharp :: filegroups/source recall@3FP/M dropped 3.85pp (32.05% → 28.21%)
  kotlin :: filegroups/source recall@3FP/M dropped 8.34pp (72.06% → 63.73%)

2 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + c: L3 hostile ensemble recall +2.49pp above LWM (10.02% → 12.51%)
  + kotlin: L3 hostile ensemble recall +4.72pp above LWM (52.67% → 57.39%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - java: L3 hostile ENSEMBLE recall dropped 25.00pp BELOW LOW-WATER-MARK (50.00% → 25.00%; LWM tolerance 0.90pp)

compared 63 filetypes (mal≥1, ben≥1); 2 below threshold and skipped.

blocked by: low-water-mark gate (0.90pp vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1136: azoth-validate] Error 1)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9988)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `1f9ee448fdf4f9e3` | `4238aae72b541df4` | `0aa0d39c285f03a4` |
| PR AUC | 0.9988 | 0.9992 | 0.9992 |
| ROC AUC | 0.9982 | 0.9984 | 0.9985 |
| F1 | 0.9818 | 0.9810 | 0.9789 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-25T15-22-39_20260525T152235-promote-1f9ee448fdf4f9e3_azoth-validate.log; tail: fitting per-route isotonic calibrators (5-fold CV) over 588814 rows (parallelism=16, cache=out/cache/azoth-calibrator)
calibration complete; computing per-filetype metrics
filetypes/xlsb: 0 rows in score table; skipping
computing dev-partition metrics (strategy selection)
loaded cached dev-bucket mask: /home/t/collimator/out/cache/azoth-test-masks/dev-947ff4cebbdd8fe06d90df9b8d8e0e32f498a93413f371a2883896fb3f53512a.npz
dev bucket: 589608/4731967 rows (12.46%)
fitting per-route isotonic calibrators (5-fold CV) over 589608 rows (parallelism=16, cache=out/cache/azoth-calibrator)
calibration complete; computing per-filetype metrics
filetypes/pyproject.toml: 0 rows in score table; skipping
filetypes/xlsb: 0 rows in score table; skipping
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-source-1f9ee448fdf4f9e3/per_filetype_metrics.json (filetypes: 79, filegroups: 0)
.venv/bin/python scripts/azoth_route_policy_eval.py \
	--score-table /home/t/collimator/out/models/azoth-candidate-filegroups-source-1f9ee448fdf4f9e3/score_table.npz \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filegroups-source-1f9ee448fdf4f9e3/general/threshold_scores.npz \
	--route-policies /home/t/collimator/out/models/azoth-candidate-filegroups-source-1f9ee448fdf4f9e3/route_policies.json \
	--partition test \
	--output-md /home/t/collimator/out/models/azoth-candidate-filegroups-source-1f9ee448fdf4f9e3/route_policy_eval_oof.md \
	--output-json /home/t/collimator/out/models/azoth-candidate-filegroups-source-1f9ee448fdf4f9e3/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-source-1f9ee448fdf4f9e3/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-source-1f9ee448fdf4f9e3/route_policy_eval_oof.md
.venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filegroups-source-1f9ee448fdf4f9e3
staged runtime azoth bundle: /tmp/tmp.NtmfpLAxch
azoth bundle ok: /tmp/tmp.NtmfpLAxch
--source-bundle out/models/azoth: 1 routes changed → 7 filetypes impacted, 58 unimpacted (drift treated as pre-existing)

ensemble improvements (≥0.10pp):
  c: L3 hostile ensemble recall +2.49pp (10.02% → 12.51%)
  kotlin: L3 hostile ensemble recall +4.72pp (52.67% → 57.39%)

per-route improvements (≥0.10pp, informational):
  c :: filegroups/source recall@3FP/M +0.28pp (13.36% → 13.65%)
  rust :: filegroups/source recall@3FP/M +0.61pp (3.05% → 3.66%)

per-route regressions (informational; does not block deploy):
  csharp :: filegroups/source recall@3FP/M dropped 3.85pp (32.05% → 28.21%)
  kotlin :: filegroups/source recall@3FP/M dropped 8.34pp (72.06% → 63.73%)

2 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + c: L3 hostile ensemble recall +2.49pp above LWM (10.02% → 12.51%)
  + kotlin: L3 hostile ensemble recall +4.72pp above LWM (52.67% → 57.39%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - java: L3 hostile ENSEMBLE recall dropped 25.00pp BELOW LOW-WATER-MARK (50.00% → 25.00%; LWM tolerance 0.90pp)

compared 63 filetypes (mal≥1, ben≥1); 2 below threshold and skipped.

blocked by: low-water-mark gate (0.90pp vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1136: azoth-validate] Error 1)
