# Promote REJECTED — `28f6675677cb01b9` on `filegroups/source`

Generated 2026-05-25T15:37:51Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-25T15-31-25_20260525T153008-promote-28f6675677cb01b9_azoth-validate.log; tail: loaded cached test-bucket mask: /home/t/collimator/out/cache/azoth-test-masks/test-947ff4cebbdd8fe06d90df9b8d8e0e32f498a93413f371a2883896fb3f53512a.npz
test bucket: 588814/4731967 rows (12.44%)
fitting per-route isotonic calibrators (5-fold CV) over 588814 rows (parallelism=16, cache=out/cache/azoth-calibrator)
calibration complete; computing per-filetype metrics
filetypes/xlsb: 0 rows in score table; skipping
computing dev-partition metrics (strategy selection)
loaded cached dev-bucket mask: /home/t/collimator/out/cache/azoth-test-masks/dev-947ff4cebbdd8fe06d90df9b8d8e0e32f498a93413f371a2883896fb3f53512a.npz
dev bucket: 589608/4731967 rows (12.46%)
fitting per-route isotonic calibrators (5-fold CV) over 589608 rows (parallelism=16, cache=out/cache/azoth-calibrator)
calibration complete; computing per-filetype metrics
filetypes/xlsb: 0 rows in score table; skipping
filetypes/pyproject.toml: 0 rows in score table; skipping
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-source-28f6675677cb01b9/per_filetype_metrics.json (filetypes: 79, filegroups: 0)
.venv/bin/python scripts/azoth_route_policy_eval.py \
	--score-table /home/t/collimator/out/models/azoth-candidate-filegroups-source-28f6675677cb01b9/score_table.npz \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filegroups-source-28f6675677cb01b9/general/threshold_scores.npz \
	--route-policies /home/t/collimator/out/models/azoth-candidate-filegroups-source-28f6675677cb01b9/route_policies.json \
	--partition test \
	--output-md /home/t/collimator/out/models/azoth-candidate-filegroups-source-28f6675677cb01b9/route_policy_eval_oof.md \
	--output-json /home/t/collimator/out/models/azoth-candidate-filegroups-source-28f6675677cb01b9/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-source-28f6675677cb01b9/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-source-28f6675677cb01b9/route_policy_eval_oof.md
.venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filegroups-source-28f6675677cb01b9
staged runtime azoth bundle: /tmp/tmp.8JAYLzU5JZ
azoth bundle ok: /tmp/tmp.8JAYLzU5JZ
--source-bundle out/models/azoth: 1 routes changed → 7 filetypes impacted, 58 unimpacted (drift treated as pre-existing)

ensemble improvements (≥0.10pp):
  c: L3 hostile ensemble recall +2.60pp (10.02% → 12.63%)
  csharp: L3 hostile ensemble recall +0.43pp (25.21% → 25.64%)
  kotlin: L3 hostile ensemble recall +4.75pp (52.67% → 57.42%)
  rust: L3 hostile ensemble recall +0.61pp (1.22% → 1.83%)

per-route regressions (informational; does not block deploy):
  csharp :: filegroups/source recall@3FP/M dropped 2.99pp (32.05% → 29.06%)
  kotlin :: filegroups/source recall@3FP/M dropped 8.65pp (72.06% → 63.42%)

2 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + c: L3 hostile ensemble recall +2.60pp above LWM (10.02% → 12.63%)
  + kotlin: L3 hostile ensemble recall +4.75pp above LWM (52.67% → 57.42%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - java: L3 hostile ENSEMBLE recall dropped 25.00pp BELOW LOW-WATER-MARK (50.00% → 25.00%; LWM tolerance 0.90pp)

compared 63 filetypes (mal≥1, ben≥1); 2 below threshold and skipped.

blocked by: low-water-mark gate (0.90pp vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1136: azoth-validate] Error 1)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9989)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `28f6675677cb01b9` | `cd5b1f975b5d4960` | `48b42e78ab180e21` |
| PR AUC | 0.9989 | 0.9991 | 0.9992 |
| ROC AUC | 0.9982 | 0.9984 | 0.9985 |
| F1 | 0.9816 | 0.9830 | 0.9823 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-25T15-31-25_20260525T153008-promote-28f6675677cb01b9_azoth-validate.log; tail: loaded cached test-bucket mask: /home/t/collimator/out/cache/azoth-test-masks/test-947ff4cebbdd8fe06d90df9b8d8e0e32f498a93413f371a2883896fb3f53512a.npz
test bucket: 588814/4731967 rows (12.44%)
fitting per-route isotonic calibrators (5-fold CV) over 588814 rows (parallelism=16, cache=out/cache/azoth-calibrator)
calibration complete; computing per-filetype metrics
filetypes/xlsb: 0 rows in score table; skipping
computing dev-partition metrics (strategy selection)
loaded cached dev-bucket mask: /home/t/collimator/out/cache/azoth-test-masks/dev-947ff4cebbdd8fe06d90df9b8d8e0e32f498a93413f371a2883896fb3f53512a.npz
dev bucket: 589608/4731967 rows (12.46%)
fitting per-route isotonic calibrators (5-fold CV) over 589608 rows (parallelism=16, cache=out/cache/azoth-calibrator)
calibration complete; computing per-filetype metrics
filetypes/xlsb: 0 rows in score table; skipping
filetypes/pyproject.toml: 0 rows in score table; skipping
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-source-28f6675677cb01b9/per_filetype_metrics.json (filetypes: 79, filegroups: 0)
.venv/bin/python scripts/azoth_route_policy_eval.py \
	--score-table /home/t/collimator/out/models/azoth-candidate-filegroups-source-28f6675677cb01b9/score_table.npz \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filegroups-source-28f6675677cb01b9/general/threshold_scores.npz \
	--route-policies /home/t/collimator/out/models/azoth-candidate-filegroups-source-28f6675677cb01b9/route_policies.json \
	--partition test \
	--output-md /home/t/collimator/out/models/azoth-candidate-filegroups-source-28f6675677cb01b9/route_policy_eval_oof.md \
	--output-json /home/t/collimator/out/models/azoth-candidate-filegroups-source-28f6675677cb01b9/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-source-28f6675677cb01b9/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-source-28f6675677cb01b9/route_policy_eval_oof.md
.venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filegroups-source-28f6675677cb01b9
staged runtime azoth bundle: /tmp/tmp.8JAYLzU5JZ
azoth bundle ok: /tmp/tmp.8JAYLzU5JZ
--source-bundle out/models/azoth: 1 routes changed → 7 filetypes impacted, 58 unimpacted (drift treated as pre-existing)

ensemble improvements (≥0.10pp):
  c: L3 hostile ensemble recall +2.60pp (10.02% → 12.63%)
  csharp: L3 hostile ensemble recall +0.43pp (25.21% → 25.64%)
  kotlin: L3 hostile ensemble recall +4.75pp (52.67% → 57.42%)
  rust: L3 hostile ensemble recall +0.61pp (1.22% → 1.83%)

per-route regressions (informational; does not block deploy):
  csharp :: filegroups/source recall@3FP/M dropped 2.99pp (32.05% → 29.06%)
  kotlin :: filegroups/source recall@3FP/M dropped 8.65pp (72.06% → 63.42%)

2 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + c: L3 hostile ensemble recall +2.60pp above LWM (10.02% → 12.63%)
  + kotlin: L3 hostile ensemble recall +4.75pp above LWM (52.67% → 57.42%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - java: L3 hostile ENSEMBLE recall dropped 25.00pp BELOW LOW-WATER-MARK (50.00% → 25.00%; LWM tolerance 0.90pp)

compared 63 filetypes (mal≥1, ben≥1); 2 below threshold and skipped.

blocked by: low-water-mark gate (0.90pp vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1136: azoth-validate] Error 1)
