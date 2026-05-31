# Promote REJECTED — `440ce55c5791cb34` on `general`

Generated 2026-05-30T16:10:13Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-30T16-04-33_20260530T160431-promote-440ce55c5791cb34_azoth-validate.log; tail: 	--csv /home/t/collimator/out/models/azoth-candidate-general-440ce55c5791cb34/route_policies.csv \
	--markdown /home/t/collimator/out/models/azoth-candidate-general-440ce55c5791cb34/route_policies.md \
	 \
	--previous-bundle out/models/azoth \
	--workers 64
policy_search carry-forward: 1/59 routes changed; 0/89 filetypes can be carried forward from previous bundle
policy_search: processing 89 filetypes across 32 worker processes (0 carried forward)
# learned_blend: 1 route(s) without isotonic calibrators; passing raw probs through: ['filetypes/chrome-manifest']
wrote /home/t/collimator/out/models/azoth-candidate-general-440ce55c5791cb34/route_policies.json
wrote /home/t/collimator/out/models/azoth-candidate-general-440ce55c5791cb34/route_policies.csv
wrote /home/t/collimator/out/models/azoth-candidate-general-440ce55c5791cb34/route_policies.md
.venv/bin/python scripts/azoth_policy_global_metrics.py \
	--config /home/t/collimator/out/models/azoth-candidate-general-440ce55c5791cb34/config.json \
	--policy /home/t/collimator/out/models/azoth-candidate-general-440ce55c5791cb34/route_policies.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-general-440ce55c5791cb34/score_table.npz \
	--output /home/t/collimator/out/models/azoth-candidate-general-440ce55c5791cb34/global_policy_metrics.json \
	--markdown /home/t/collimator/out/models/azoth-candidate-general-440ce55c5791cb34/global_policy_metrics.md \
	--fail-on-budget --max-budget-multiplier 30
wrote /home/t/collimator/out/models/azoth-candidate-general-440ce55c5791cb34/global_policy_metrics.json
wrote /home/t/collimator/out/models/azoth-candidate-general-440ce55c5791cb34/global_policy_metrics.md
.venv/bin/python scripts/compute_routed_metrics.py --azoth-root /home/t/collimator/out/models/azoth-candidate-general-440ce55c5791cb34 --db postgres://hopper@localhost:5432/hopper --no-ci --no-stacked 
computing test-partition metrics (reporting)
loaded cached test-bucket mask: /home/t/collimator/out/cache/azoth-test-masks/test-9cd1b636f1f7928ed92de886ec9cefbbad172d1d9fe05122d98736ffb401159e.npz
test bucket: 695967/5591524 rows (12.45%)
fitting per-route isotonic calibrators (5-fold CV) over 695967 rows (parallelism=16, cache=out/cache/azoth-calibrator)
calibration complete; computing per-filetype metrics
filetypes/ppam: 0 rows in score table; skipping
filetypes/xlsb: 0 rows in score table; skipping
filetypes/xpi: 0 rows in score table; skipping
computing dev-partition metrics (strategy selection)
loaded cached dev-bucket mask: /home/t/collimator/out/cache/azoth-test-masks/dev-9cd1b636f1f7928ed92de886ec9cefbbad172d1d9fe05122d98736ffb401159e.npz
dev bucket: 697116/5591524 rows (12.47%)
fitting per-route isotonic calibrators (5-fold CV) over 697116 rows (parallelism=16, cache=out/cache/azoth-calibrator)
calibration complete; computing per-filetype metrics
filetypes/ppam: 0 rows in score table; skipping
filetypes/xlsb: 0 rows in score table; skipping
filetypes/xpi: 0 rows in score table; skipping
wrote /home/t/collimator/out/models/azoth-candidate-general-440ce55c5791cb34/per_filetype_metrics.json (filetypes: 86, filegroups: 0)
.venv/bin/python scripts/azoth_route_policy_eval.py \
	--score-table /home/t/collimator/out/models/azoth-candidate-general-440ce55c5791cb34/score_table.npz \
	--general-scores /home/t/collimator/out/models/azoth-candidate-general-440ce55c5791cb34/general/threshold_scores.npz \
	--route-policies /home/t/collimator/out/models/azoth-candidate-general-440ce55c5791cb34/route_policies.json \
	--partition test \
	--output-md /home/t/collimator/out/models/azoth-candidate-general-440ce55c5791cb34/route_policy_eval_oof.md \
	--output-json /home/t/collimator/out/models/azoth-candidate-general-440ce55c5791cb34/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-general-440ce55c5791cb34/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-general-440ce55c5791cb34/route_policy_eval_oof.md
.venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-general-440ce55c5791cb34
/home/t/collimator/out/models/azoth-candidate-general-440ce55c5791cb34/general: ONNX-only deploy but route ships non-ONNX model(s) ['seed_42.txt', 'seed_43.txt', 'seed_44.txt']; regenerate so every seed has an .onnx sibling (litmus dropped the LightGBM/XGBoost loaders).
make[2]: *** [Makefile:1151: azoth-validate] Error 1)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9997)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `440ce55c5791cb34` | `db70f6911d71f337` | `106d52e0efed3889` |
| PR AUC | 0.9997 | 0.9999 | 0.9996 |
| ROC AUC | 0.9997 | 0.9996 | 0.9996 |
| F1 | 0.9917 | 0.9936 | 0.9885 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-30T16-04-33_20260530T160431-promote-440ce55c5791cb34_azoth-validate.log; tail: 	--csv /home/t/collimator/out/models/azoth-candidate-general-440ce55c5791cb34/route_policies.csv \
	--markdown /home/t/collimator/out/models/azoth-candidate-general-440ce55c5791cb34/route_policies.md \
	 \
	--previous-bundle out/models/azoth \
	--workers 64
policy_search carry-forward: 1/59 routes changed; 0/89 filetypes can be carried forward from previous bundle
policy_search: processing 89 filetypes across 32 worker processes (0 carried forward)
# learned_blend: 1 route(s) without isotonic calibrators; passing raw probs through: ['filetypes/chrome-manifest']
wrote /home/t/collimator/out/models/azoth-candidate-general-440ce55c5791cb34/route_policies.json
wrote /home/t/collimator/out/models/azoth-candidate-general-440ce55c5791cb34/route_policies.csv
wrote /home/t/collimator/out/models/azoth-candidate-general-440ce55c5791cb34/route_policies.md
.venv/bin/python scripts/azoth_policy_global_metrics.py \
	--config /home/t/collimator/out/models/azoth-candidate-general-440ce55c5791cb34/config.json \
	--policy /home/t/collimator/out/models/azoth-candidate-general-440ce55c5791cb34/route_policies.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-general-440ce55c5791cb34/score_table.npz \
	--output /home/t/collimator/out/models/azoth-candidate-general-440ce55c5791cb34/global_policy_metrics.json \
	--markdown /home/t/collimator/out/models/azoth-candidate-general-440ce55c5791cb34/global_policy_metrics.md \
	--fail-on-budget --max-budget-multiplier 30
wrote /home/t/collimator/out/models/azoth-candidate-general-440ce55c5791cb34/global_policy_metrics.json
wrote /home/t/collimator/out/models/azoth-candidate-general-440ce55c5791cb34/global_policy_metrics.md
.venv/bin/python scripts/compute_routed_metrics.py --azoth-root /home/t/collimator/out/models/azoth-candidate-general-440ce55c5791cb34 --db postgres://hopper@localhost:5432/hopper --no-ci --no-stacked 
computing test-partition metrics (reporting)
loaded cached test-bucket mask: /home/t/collimator/out/cache/azoth-test-masks/test-9cd1b636f1f7928ed92de886ec9cefbbad172d1d9fe05122d98736ffb401159e.npz
test bucket: 695967/5591524 rows (12.45%)
fitting per-route isotonic calibrators (5-fold CV) over 695967 rows (parallelism=16, cache=out/cache/azoth-calibrator)
calibration complete; computing per-filetype metrics
filetypes/ppam: 0 rows in score table; skipping
filetypes/xlsb: 0 rows in score table; skipping
filetypes/xpi: 0 rows in score table; skipping
computing dev-partition metrics (strategy selection)
loaded cached dev-bucket mask: /home/t/collimator/out/cache/azoth-test-masks/dev-9cd1b636f1f7928ed92de886ec9cefbbad172d1d9fe05122d98736ffb401159e.npz
dev bucket: 697116/5591524 rows (12.47%)
fitting per-route isotonic calibrators (5-fold CV) over 697116 rows (parallelism=16, cache=out/cache/azoth-calibrator)
calibration complete; computing per-filetype metrics
filetypes/ppam: 0 rows in score table; skipping
filetypes/xlsb: 0 rows in score table; skipping
filetypes/xpi: 0 rows in score table; skipping
wrote /home/t/collimator/out/models/azoth-candidate-general-440ce55c5791cb34/per_filetype_metrics.json (filetypes: 86, filegroups: 0)
.venv/bin/python scripts/azoth_route_policy_eval.py \
	--score-table /home/t/collimator/out/models/azoth-candidate-general-440ce55c5791cb34/score_table.npz \
	--general-scores /home/t/collimator/out/models/azoth-candidate-general-440ce55c5791cb34/general/threshold_scores.npz \
	--route-policies /home/t/collimator/out/models/azoth-candidate-general-440ce55c5791cb34/route_policies.json \
	--partition test \
	--output-md /home/t/collimator/out/models/azoth-candidate-general-440ce55c5791cb34/route_policy_eval_oof.md \
	--output-json /home/t/collimator/out/models/azoth-candidate-general-440ce55c5791cb34/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-general-440ce55c5791cb34/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-general-440ce55c5791cb34/route_policy_eval_oof.md
.venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-general-440ce55c5791cb34
/home/t/collimator/out/models/azoth-candidate-general-440ce55c5791cb34/general: ONNX-only deploy but route ships non-ONNX model(s) ['seed_42.txt', 'seed_43.txt', 'seed_44.txt']; regenerate so every seed has an .onnx sibling (litmus dropped the LightGBM/XGBoost loaders).
make[2]: *** [Makefile:1151: azoth-validate] Error 1)
