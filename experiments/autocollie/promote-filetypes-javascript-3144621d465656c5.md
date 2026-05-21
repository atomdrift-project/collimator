# Promote REJECTED — `3144621d465656c5` on `filetypes/javascript`

Generated 2026-05-21T18:46:13Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-21T18-41-00_20260521T183843-promote-3144621d465656c5_azoth-validate.log; tail: wrote /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-3144621d465656c5/route_policies.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-3144621d465656c5/route_policies.csv
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-3144621d465656c5/route_policies.md
.venv/bin/python scripts/azoth_policy_global_metrics.py \
	--config /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-3144621d465656c5/config.json \
	--policy /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-3144621d465656c5/route_policies.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-3144621d465656c5/score_table.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-3144621d465656c5/global_policy_metrics.json \
	--markdown /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-3144621d465656c5/global_policy_metrics.md \
	--fail-on-budget --max-budget-multiplier 30
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-3144621d465656c5/global_policy_metrics.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-3144621d465656c5/global_policy_metrics.md
.venv/bin/python scripts/compute_routed_metrics.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-3144621d465656c5 --db postgres://hopper@localhost:5432/hopper --no-ci --no-stacked 
computing test-partition metrics (reporting)
loaded cached test-bucket mask: /home/t/collimator/out/cache/azoth-test-masks/test-7ff4250a49d545e150cf60182c13800a77c6cc7170e52d1e62748cecd907399b.npz
test bucket: 588274/4727598 rows (12.44%)
fitting per-route isotonic calibrators (5-fold CV) over 588274 rows
calibration complete; computing per-filetype metrics
filetypes/xlsb: 0 rows in score table; skipping
computing dev-partition metrics (strategy selection)
loaded cached dev-bucket mask: /home/t/collimator/out/cache/azoth-test-masks/dev-7ff4250a49d545e150cf60182c13800a77c6cc7170e52d1e62748cecd907399b.npz
dev bucket: 589053/4727598 rows (12.46%)
fitting per-route isotonic calibrators (5-fold CV) over 589053 rows
calibration complete; computing per-filetype metrics
filetypes/xlsb: 0 rows in score table; skipping
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-3144621d465656c5/per_filetype_metrics.json (filetypes: 78, filegroups: 0)
.venv/bin/python scripts/azoth_route_policy_eval.py \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-3144621d465656c5/score_table.npz \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-3144621d465656c5/general/threshold_scores.npz \
	--route-policies /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-3144621d465656c5/route_policies.json \
	--partition test \
	--output-md /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-3144621d465656c5/route_policy_eval_oof.md \
	--output-json /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-3144621d465656c5/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-3144621d465656c5/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-3144621d465656c5/route_policy_eval_oof.md
.venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-3144621d465656c5
staged runtime azoth bundle: /tmp/tmp.n8F2Pp7TTf
azoth bundle ok: /tmp/tmp.n8F2Pp7TTf

per-route regressions (informational; does not block deploy):
  javascript :: filetypes/javascript recall@3FP/M dropped 11.46pp (89.53% → 78.07%)

error: 1 ensemble regression(s) over tolerance:
  - javascript: L3 hostile ENSEMBLE recall dropped 4.02pp (89.16% → 85.14%; tolerance 1.00pp; deployed 95% CI lower = 88.56%)

compared 63 filetypes (mal≥1, ben≥1); 2 below threshold and skipped.

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run.
make[1]: *** [Makefile:1082: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9993)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `3144621d465656c5` | `f35682ec94bfacb7` | `dcb59b8247676d13` |
| PR AUC | 0.9993 | 0.9997 | 0.9997 |
| ROC AUC | 0.9989 | 0.9995 | 0.9995 |
| F1 | 0.9871 | 0.9887 | 0.9891 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-21T18-41-00_20260521T183843-promote-3144621d465656c5_azoth-validate.log; tail: wrote /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-3144621d465656c5/route_policies.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-3144621d465656c5/route_policies.csv
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-3144621d465656c5/route_policies.md
.venv/bin/python scripts/azoth_policy_global_metrics.py \
	--config /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-3144621d465656c5/config.json \
	--policy /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-3144621d465656c5/route_policies.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-3144621d465656c5/score_table.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-3144621d465656c5/global_policy_metrics.json \
	--markdown /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-3144621d465656c5/global_policy_metrics.md \
	--fail-on-budget --max-budget-multiplier 30
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-3144621d465656c5/global_policy_metrics.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-3144621d465656c5/global_policy_metrics.md
.venv/bin/python scripts/compute_routed_metrics.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-3144621d465656c5 --db postgres://hopper@localhost:5432/hopper --no-ci --no-stacked 
computing test-partition metrics (reporting)
loaded cached test-bucket mask: /home/t/collimator/out/cache/azoth-test-masks/test-7ff4250a49d545e150cf60182c13800a77c6cc7170e52d1e62748cecd907399b.npz
test bucket: 588274/4727598 rows (12.44%)
fitting per-route isotonic calibrators (5-fold CV) over 588274 rows
calibration complete; computing per-filetype metrics
filetypes/xlsb: 0 rows in score table; skipping
computing dev-partition metrics (strategy selection)
loaded cached dev-bucket mask: /home/t/collimator/out/cache/azoth-test-masks/dev-7ff4250a49d545e150cf60182c13800a77c6cc7170e52d1e62748cecd907399b.npz
dev bucket: 589053/4727598 rows (12.46%)
fitting per-route isotonic calibrators (5-fold CV) over 589053 rows
calibration complete; computing per-filetype metrics
filetypes/xlsb: 0 rows in score table; skipping
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-3144621d465656c5/per_filetype_metrics.json (filetypes: 78, filegroups: 0)
.venv/bin/python scripts/azoth_route_policy_eval.py \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-3144621d465656c5/score_table.npz \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-3144621d465656c5/general/threshold_scores.npz \
	--route-policies /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-3144621d465656c5/route_policies.json \
	--partition test \
	--output-md /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-3144621d465656c5/route_policy_eval_oof.md \
	--output-json /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-3144621d465656c5/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-3144621d465656c5/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-3144621d465656c5/route_policy_eval_oof.md
.venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-3144621d465656c5
staged runtime azoth bundle: /tmp/tmp.n8F2Pp7TTf
azoth bundle ok: /tmp/tmp.n8F2Pp7TTf

per-route regressions (informational; does not block deploy):
  javascript :: filetypes/javascript recall@3FP/M dropped 11.46pp (89.53% → 78.07%)

error: 1 ensemble regression(s) over tolerance:
  - javascript: L3 hostile ENSEMBLE recall dropped 4.02pp (89.16% → 85.14%; tolerance 1.00pp; deployed 95% CI lower = 88.56%)

compared 63 filetypes (mal≥1, ben≥1); 2 below threshold and skipped.

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run.
make[1]: *** [Makefile:1082: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')
