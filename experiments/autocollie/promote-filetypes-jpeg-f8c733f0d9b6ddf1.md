# Promote REJECTED — `f8c733f0d9b6ddf1` on `filetypes/jpeg`

Generated 2026-05-20T07:34:54Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-20T07-30-33_20260520T073018-promote-f8c733f0d9b6ddf1_azoth-validate.log; tail: .venv/bin/python scripts/azoth_policy_global_metrics.py \
	--config /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-f8c733f0d9b6ddf1/config.json \
	--policy /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-f8c733f0d9b6ddf1/route_policies.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-f8c733f0d9b6ddf1/score_table.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-f8c733f0d9b6ddf1/global_policy_metrics.json \
	--markdown /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-f8c733f0d9b6ddf1/global_policy_metrics.md \
	--fail-on-budget
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-f8c733f0d9b6ddf1/global_policy_metrics.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-f8c733f0d9b6ddf1/global_policy_metrics.md
.venv/bin/python scripts/compute_routed_metrics.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-f8c733f0d9b6ddf1 --db postgres://hopper@localhost:5432/hopper --no-ci --no-stacked 
computing test-partition metrics (reporting)
loaded cached test-bucket mask: /home/t/collimator/out/cache/azoth-test-masks/test-5fbe877e32cf00452d21320909bf25270d1a40d7a34297eadbb67b0f69075d35.npz
test bucket: 587975/4725221 rows (12.44%)
fitting per-route isotonic calibrators (5-fold CV) over 587975 rows
calibration complete; computing per-filetype metrics
filetypes/xlsb: 0 rows in score table; skipping
computing dev-partition metrics (strategy selection)
loaded cached dev-bucket mask: /home/t/collimator/out/cache/azoth-test-masks/dev-5fbe877e32cf00452d21320909bf25270d1a40d7a34297eadbb67b0f69075d35.npz
dev bucket: 588763/4725221 rows (12.46%)
fitting per-route isotonic calibrators (5-fold CV) over 588763 rows
calibration complete; computing per-filetype metrics
filetypes/xlsb: 0 rows in score table; skipping
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-f8c733f0d9b6ddf1/per_filetype_metrics.json (filetypes: 78, filegroups: 0)
.venv/bin/python scripts/azoth_route_policy_eval.py \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-f8c733f0d9b6ddf1/score_table.npz \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-f8c733f0d9b6ddf1/general/threshold_scores.npz \
	--route-policies /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-f8c733f0d9b6ddf1/route_policies.json \
	--partition test \
	--output-md /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-f8c733f0d9b6ddf1/route_policy_eval_oof.md \
	--output-json /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-f8c733f0d9b6ddf1/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-f8c733f0d9b6ddf1/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-f8c733f0d9b6ddf1/route_policy_eval_oof.md
.venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-f8c733f0d9b6ddf1
staged runtime azoth bundle: /tmp/tmp.kBXxw3xNf0
azoth bundle ok: /tmp/tmp.kBXxw3xNf0

error: 7 regression(s) over tolerance:
  - elf: L3 hostile recall dropped 5.19pp (94.84% → 89.65%; tolerance 1.00pp)
  - package.json: L3 hostile recall dropped 1.71pp (92.65% → 90.94%; tolerance 1.00pp)
  - pe: L3 hostile recall dropped 2.08pp (69.97% → 67.89%; tolerance 1.00pp)
  - php: L3 hostile recall dropped 1.37pp (51.27% → 49.90%; tolerance 1.00pp)
  - python: L3 hostile recall dropped 7.74pp (56.40% → 48.66%; tolerance 1.00pp)
  - tar.gz: L3 hostile recall dropped 3.55pp (58.52% → 54.96%; tolerance 1.00pp)
  - zip: L3 hostile recall dropped 2.08pp (45.25% → 43.18%; tolerance 1.00pp)

compared 16 filetypes (mal≥500, ben≥500); 49 below threshold and skipped.

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run.
make[1]: *** [Makefile:1071: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9798)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `f8c733f0d9b6ddf1` | `960fc2f0e3c98bd9` | `3dfa8283c0448224` |
| PR AUC | 0.9798 | 0.9749 | 0.9789 |
| ROC AUC | 0.9839 | 0.9801 | 0.9839 |
| F1 | 0.8936 | 0.8519 | 0.9362 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-20T07-30-33_20260520T073018-promote-f8c733f0d9b6ddf1_azoth-validate.log; tail: .venv/bin/python scripts/azoth_policy_global_metrics.py \
	--config /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-f8c733f0d9b6ddf1/config.json \
	--policy /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-f8c733f0d9b6ddf1/route_policies.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-f8c733f0d9b6ddf1/score_table.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-f8c733f0d9b6ddf1/global_policy_metrics.json \
	--markdown /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-f8c733f0d9b6ddf1/global_policy_metrics.md \
	--fail-on-budget
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-f8c733f0d9b6ddf1/global_policy_metrics.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-f8c733f0d9b6ddf1/global_policy_metrics.md
.venv/bin/python scripts/compute_routed_metrics.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-f8c733f0d9b6ddf1 --db postgres://hopper@localhost:5432/hopper --no-ci --no-stacked 
computing test-partition metrics (reporting)
loaded cached test-bucket mask: /home/t/collimator/out/cache/azoth-test-masks/test-5fbe877e32cf00452d21320909bf25270d1a40d7a34297eadbb67b0f69075d35.npz
test bucket: 587975/4725221 rows (12.44%)
fitting per-route isotonic calibrators (5-fold CV) over 587975 rows
calibration complete; computing per-filetype metrics
filetypes/xlsb: 0 rows in score table; skipping
computing dev-partition metrics (strategy selection)
loaded cached dev-bucket mask: /home/t/collimator/out/cache/azoth-test-masks/dev-5fbe877e32cf00452d21320909bf25270d1a40d7a34297eadbb67b0f69075d35.npz
dev bucket: 588763/4725221 rows (12.46%)
fitting per-route isotonic calibrators (5-fold CV) over 588763 rows
calibration complete; computing per-filetype metrics
filetypes/xlsb: 0 rows in score table; skipping
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-f8c733f0d9b6ddf1/per_filetype_metrics.json (filetypes: 78, filegroups: 0)
.venv/bin/python scripts/azoth_route_policy_eval.py \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-f8c733f0d9b6ddf1/score_table.npz \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-f8c733f0d9b6ddf1/general/threshold_scores.npz \
	--route-policies /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-f8c733f0d9b6ddf1/route_policies.json \
	--partition test \
	--output-md /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-f8c733f0d9b6ddf1/route_policy_eval_oof.md \
	--output-json /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-f8c733f0d9b6ddf1/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-f8c733f0d9b6ddf1/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-f8c733f0d9b6ddf1/route_policy_eval_oof.md
.venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-f8c733f0d9b6ddf1
staged runtime azoth bundle: /tmp/tmp.kBXxw3xNf0
azoth bundle ok: /tmp/tmp.kBXxw3xNf0

error: 7 regression(s) over tolerance:
  - elf: L3 hostile recall dropped 5.19pp (94.84% → 89.65%; tolerance 1.00pp)
  - package.json: L3 hostile recall dropped 1.71pp (92.65% → 90.94%; tolerance 1.00pp)
  - pe: L3 hostile recall dropped 2.08pp (69.97% → 67.89%; tolerance 1.00pp)
  - php: L3 hostile recall dropped 1.37pp (51.27% → 49.90%; tolerance 1.00pp)
  - python: L3 hostile recall dropped 7.74pp (56.40% → 48.66%; tolerance 1.00pp)
  - tar.gz: L3 hostile recall dropped 3.55pp (58.52% → 54.96%; tolerance 1.00pp)
  - zip: L3 hostile recall dropped 2.08pp (45.25% → 43.18%; tolerance 1.00pp)

compared 16 filetypes (mal≥500, ben≥500); 49 below threshold and skipped.

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run.
make[1]: *** [Makefile:1071: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')
