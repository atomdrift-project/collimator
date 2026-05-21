# Promote REJECTED — `07d42cbbdf21fd84` on `filetypes/javascript`

Generated 2026-05-21T05:35:55Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-21T05-31-17_20260521T052903-promote-07d42cbbdf21fd84_azoth-validate.log; tail: loaded cached dev-bucket mask: /home/t/collimator/out/cache/azoth-test-masks/dev-ea2b446eb50ab99bf2fc544959ed8f35b2bd308fe62db14b81dca4056052e3ac.npz
dev bucket: 589021/4727335 rows (12.46%)
fitting per-route isotonic calibrators (5-fold CV) over 589021 rows
calibration complete; computing per-filetype metrics
filetypes/xlsb: 0 rows in score table; skipping
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-07d42cbbdf21fd84/per_filetype_metrics.json (filetypes: 78, filegroups: 0)
.venv/bin/python scripts/azoth_route_policy_eval.py \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-07d42cbbdf21fd84/score_table.npz \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-07d42cbbdf21fd84/general/threshold_scores.npz \
	--route-policies /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-07d42cbbdf21fd84/route_policies.json \
	--partition test \
	--output-md /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-07d42cbbdf21fd84/route_policy_eval_oof.md \
	--output-json /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-07d42cbbdf21fd84/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-07d42cbbdf21fd84/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-07d42cbbdf21fd84/route_policy_eval_oof.md
.venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-07d42cbbdf21fd84
staged runtime azoth bundle: /tmp/tmp.znAx6riDWe
azoth bundle ok: /tmp/tmp.znAx6riDWe

ensemble improvements (≥0.10pp):
  c: L3 hostile ensemble recall +0.91pp (3.74% → 4.64%)
  csharp: L3 hostile ensemble recall +1.28pp (17.52% → 18.80%)
  java_class: L3 hostile ensemble recall +18.50pp (45.66% → 64.16%)
  rust: L3 hostile ensemble recall +0.61pp (1.22% → 1.83%)
  xml: L3 hostile ensemble recall +0.34pp (2.74% → 3.08%)

per-route improvements (≥0.10pp, informational):
  c :: filegroups/source recall@3FP/M +10.42pp (3.00% → 13.42%)
  csharp :: filegroups/source recall@3FP/M +3.85pp (24.79% → 28.63%)
  go :: filegroups/source recall@3FP/M +2.12pp (0.68% → 2.80%)
  java :: filegroups/source recall@3FP/M +25.00pp (50.00% → 75.00%)
  java_class :: filegroups/portable recall@3FP/M +1.73pp (83.24% → 84.97%)
  java_class :: filetypes/java_class recall@3FP/M +8.09pp (75.72% → 83.82%)
  python :: filetypes/python recall@3FP/M +3.61pp (65.77% → 69.38%)
  rust :: filegroups/source recall@3FP/M +3.66pp (1.22% → 4.88%)
  xml :: filetypes/xml recall@3FP/M +1.03pp (1.71% → 2.74%)

per-route regressions (informational; does not block deploy):
  javascript :: filetypes/javascript recall@3FP/M dropped 11.73pp (89.71% → 77.98%)
  kotlin :: filegroups/source recall@3FP/M dropped 19.22pp (82.76% → 63.54%)
  perl :: filetypes/perl recall@3FP/M dropped 11.11pp (96.30% → 85.19%)

error: 1 ensemble regression(s) over tolerance:
  - javascript: L3 hostile ENSEMBLE recall dropped 4.11pp (88.33% → 84.23%; tolerance 1.00pp; deployed 95% CI lower = 87.71%)

compared 63 filetypes (mal≥1, ben≥1); 2 below threshold and skipped.

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run.
make[1]: *** [Makefile:1085: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9994)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `07d42cbbdf21fd84` | `e9e3cd72f928634f` | `e0a90ed9ab682d61` |
| PR AUC | 0.9994 | 0.9997 | 0.9997 |
| ROC AUC | 0.9989 | 0.9995 | 0.9995 |
| F1 | 0.9851 | 0.9894 | 0.9898 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-21T05-31-17_20260521T052903-promote-07d42cbbdf21fd84_azoth-validate.log; tail: loaded cached dev-bucket mask: /home/t/collimator/out/cache/azoth-test-masks/dev-ea2b446eb50ab99bf2fc544959ed8f35b2bd308fe62db14b81dca4056052e3ac.npz
dev bucket: 589021/4727335 rows (12.46%)
fitting per-route isotonic calibrators (5-fold CV) over 589021 rows
calibration complete; computing per-filetype metrics
filetypes/xlsb: 0 rows in score table; skipping
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-07d42cbbdf21fd84/per_filetype_metrics.json (filetypes: 78, filegroups: 0)
.venv/bin/python scripts/azoth_route_policy_eval.py \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-07d42cbbdf21fd84/score_table.npz \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-07d42cbbdf21fd84/general/threshold_scores.npz \
	--route-policies /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-07d42cbbdf21fd84/route_policies.json \
	--partition test \
	--output-md /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-07d42cbbdf21fd84/route_policy_eval_oof.md \
	--output-json /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-07d42cbbdf21fd84/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-07d42cbbdf21fd84/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-07d42cbbdf21fd84/route_policy_eval_oof.md
.venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-07d42cbbdf21fd84
staged runtime azoth bundle: /tmp/tmp.znAx6riDWe
azoth bundle ok: /tmp/tmp.znAx6riDWe

ensemble improvements (≥0.10pp):
  c: L3 hostile ensemble recall +0.91pp (3.74% → 4.64%)
  csharp: L3 hostile ensemble recall +1.28pp (17.52% → 18.80%)
  java_class: L3 hostile ensemble recall +18.50pp (45.66% → 64.16%)
  rust: L3 hostile ensemble recall +0.61pp (1.22% → 1.83%)
  xml: L3 hostile ensemble recall +0.34pp (2.74% → 3.08%)

per-route improvements (≥0.10pp, informational):
  c :: filegroups/source recall@3FP/M +10.42pp (3.00% → 13.42%)
  csharp :: filegroups/source recall@3FP/M +3.85pp (24.79% → 28.63%)
  go :: filegroups/source recall@3FP/M +2.12pp (0.68% → 2.80%)
  java :: filegroups/source recall@3FP/M +25.00pp (50.00% → 75.00%)
  java_class :: filegroups/portable recall@3FP/M +1.73pp (83.24% → 84.97%)
  java_class :: filetypes/java_class recall@3FP/M +8.09pp (75.72% → 83.82%)
  python :: filetypes/python recall@3FP/M +3.61pp (65.77% → 69.38%)
  rust :: filegroups/source recall@3FP/M +3.66pp (1.22% → 4.88%)
  xml :: filetypes/xml recall@3FP/M +1.03pp (1.71% → 2.74%)

per-route regressions (informational; does not block deploy):
  javascript :: filetypes/javascript recall@3FP/M dropped 11.73pp (89.71% → 77.98%)
  kotlin :: filegroups/source recall@3FP/M dropped 19.22pp (82.76% → 63.54%)
  perl :: filetypes/perl recall@3FP/M dropped 11.11pp (96.30% → 85.19%)

error: 1 ensemble regression(s) over tolerance:
  - javascript: L3 hostile ENSEMBLE recall dropped 4.11pp (88.33% → 84.23%; tolerance 1.00pp; deployed 95% CI lower = 87.71%)

compared 63 filetypes (mal≥1, ben≥1); 2 below threshold and skipped.

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run.
make[1]: *** [Makefile:1085: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')
