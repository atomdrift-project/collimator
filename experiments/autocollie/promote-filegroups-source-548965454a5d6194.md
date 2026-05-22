# Promote REJECTED — `548965454a5d6194` on `filegroups/source`

Generated 2026-05-21T19:17:09Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-21T19-12-28_20260521T191146-promote-548965454a5d6194_azoth-validate.log; tail: .venv/bin/python scripts/compute_routed_metrics.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filegroups-source-548965454a5d6194 --db postgres://hopper@localhost:5432/hopper --no-ci --no-stacked 
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
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-source-548965454a5d6194/per_filetype_metrics.json (filetypes: 78, filegroups: 0)
.venv/bin/python scripts/azoth_route_policy_eval.py \
	--score-table /home/t/collimator/out/models/azoth-candidate-filegroups-source-548965454a5d6194/score_table.npz \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filegroups-source-548965454a5d6194/general/threshold_scores.npz \
	--route-policies /home/t/collimator/out/models/azoth-candidate-filegroups-source-548965454a5d6194/route_policies.json \
	--partition test \
	--output-md /home/t/collimator/out/models/azoth-candidate-filegroups-source-548965454a5d6194/route_policy_eval_oof.md \
	--output-json /home/t/collimator/out/models/azoth-candidate-filegroups-source-548965454a5d6194/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-source-548965454a5d6194/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-source-548965454a5d6194/route_policy_eval_oof.md
.venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filegroups-source-548965454a5d6194
staged runtime azoth bundle: /tmp/tmp.NpnzMhaTyY
azoth bundle ok: /tmp/tmp.NpnzMhaTyY

ensemble improvements (≥0.10pp):
  c: L3 hostile ensemble recall +0.91pp (4.02% → 4.93%)
  csharp: L3 hostile ensemble recall +0.43pp (39.32% → 39.74%)
  kotlin: L3 hostile ensemble recall +1.28pp (95.02% → 96.30%)

per-route improvements (≥0.10pp, informational):
  c :: filegroups/source recall@3FP/M +13.48pp (0.11% → 13.59%)
  csharp :: filegroups/source recall@3FP/M +27.35pp (0.85% → 28.21%)
  go :: filegroups/source recall@3FP/M +1.95pp (0.25% → 2.21%)
  java :: filegroups/source recall@3FP/M +25.00pp (50.00% → 75.00%)
  rust :: filegroups/source recall@3FP/M +1.83pp (1.22% → 3.05%)

per-route regressions (informational; does not block deploy):
  kotlin :: filegroups/source recall@3FP/M dropped 6.23pp (70.00% → 63.77%)

error: 1 ensemble regression(s) over tolerance:
  - go: L3 hostile ENSEMBLE recall dropped 4.50pp (16.82% → 12.32%; tolerance 1.00pp; deployed 95% CI lower = 14.73%)

compared 63 filetypes (mal≥1, ben≥1); 2 below threshold and skipped.

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run.
make[1]: *** [Makefile:1082: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9988)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `548965454a5d6194` | `d7a214a6430e0c44` | `e836d5b467698d33` |
| PR AUC | 0.9988 | 0.9988 | 0.9989 |
| ROC AUC | 0.9981 | 0.9981 | 0.9982 |
| F1 | 0.9765 | 0.9781 | 0.9798 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-21T19-12-28_20260521T191146-promote-548965454a5d6194_azoth-validate.log; tail: .venv/bin/python scripts/compute_routed_metrics.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filegroups-source-548965454a5d6194 --db postgres://hopper@localhost:5432/hopper --no-ci --no-stacked 
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
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-source-548965454a5d6194/per_filetype_metrics.json (filetypes: 78, filegroups: 0)
.venv/bin/python scripts/azoth_route_policy_eval.py \
	--score-table /home/t/collimator/out/models/azoth-candidate-filegroups-source-548965454a5d6194/score_table.npz \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filegroups-source-548965454a5d6194/general/threshold_scores.npz \
	--route-policies /home/t/collimator/out/models/azoth-candidate-filegroups-source-548965454a5d6194/route_policies.json \
	--partition test \
	--output-md /home/t/collimator/out/models/azoth-candidate-filegroups-source-548965454a5d6194/route_policy_eval_oof.md \
	--output-json /home/t/collimator/out/models/azoth-candidate-filegroups-source-548965454a5d6194/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-source-548965454a5d6194/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-source-548965454a5d6194/route_policy_eval_oof.md
.venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filegroups-source-548965454a5d6194
staged runtime azoth bundle: /tmp/tmp.NpnzMhaTyY
azoth bundle ok: /tmp/tmp.NpnzMhaTyY

ensemble improvements (≥0.10pp):
  c: L3 hostile ensemble recall +0.91pp (4.02% → 4.93%)
  csharp: L3 hostile ensemble recall +0.43pp (39.32% → 39.74%)
  kotlin: L3 hostile ensemble recall +1.28pp (95.02% → 96.30%)

per-route improvements (≥0.10pp, informational):
  c :: filegroups/source recall@3FP/M +13.48pp (0.11% → 13.59%)
  csharp :: filegroups/source recall@3FP/M +27.35pp (0.85% → 28.21%)
  go :: filegroups/source recall@3FP/M +1.95pp (0.25% → 2.21%)
  java :: filegroups/source recall@3FP/M +25.00pp (50.00% → 75.00%)
  rust :: filegroups/source recall@3FP/M +1.83pp (1.22% → 3.05%)

per-route regressions (informational; does not block deploy):
  kotlin :: filegroups/source recall@3FP/M dropped 6.23pp (70.00% → 63.77%)

error: 1 ensemble regression(s) over tolerance:
  - go: L3 hostile ENSEMBLE recall dropped 4.50pp (16.82% → 12.32%; tolerance 1.00pp; deployed 95% CI lower = 14.73%)

compared 63 filetypes (mal≥1, ben≥1); 2 below threshold and skipped.

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run.
make[1]: *** [Makefile:1082: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')
