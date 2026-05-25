# Promote REJECTED — `388062cdae015a34` on `filetypes/tar.gz`

Generated 2026-05-24T08:36:30Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-24T08-32-32_20260524T083032-promote-388062cdae015a34_azoth-validate.log; tail: wrote /home/t/collimator/out/models/azoth-candidate-filetypes-tar.gz-388062cdae015a34/global_policy_metrics.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-tar.gz-388062cdae015a34/global_policy_metrics.md
.venv/bin/python scripts/compute_routed_metrics.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filetypes-tar.gz-388062cdae015a34 --db postgres://hopper@localhost:5432/hopper --no-ci --no-stacked 
computing test-partition metrics (reporting)
loaded cached test-bucket mask: /home/t/collimator/out/cache/azoth-test-masks/test-947ff4cebbdd8fe06d90df9b8d8e0e32f498a93413f371a2883896fb3f53512a.npz
test bucket: 588814/4731967 rows (12.44%)
fitting per-route isotonic calibrators (5-fold CV) over 588814 rows (parallelism=16)
calibration complete; computing per-filetype metrics
filetypes/xlsb: 0 rows in score table; skipping
computing dev-partition metrics (strategy selection)
loaded cached dev-bucket mask: /home/t/collimator/out/cache/azoth-test-masks/dev-947ff4cebbdd8fe06d90df9b8d8e0e32f498a93413f371a2883896fb3f53512a.npz
dev bucket: 589608/4731967 rows (12.46%)
fitting per-route isotonic calibrators (5-fold CV) over 589608 rows (parallelism=16)
calibration complete; computing per-filetype metrics
filetypes/xlsb: 0 rows in score table; skipping
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-tar.gz-388062cdae015a34/per_filetype_metrics.json (filetypes: 78, filegroups: 0)
.venv/bin/python scripts/azoth_route_policy_eval.py \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-tar.gz-388062cdae015a34/score_table.npz \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filetypes-tar.gz-388062cdae015a34/general/threshold_scores.npz \
	--route-policies /home/t/collimator/out/models/azoth-candidate-filetypes-tar.gz-388062cdae015a34/route_policies.json \
	--partition test \
	--output-md /home/t/collimator/out/models/azoth-candidate-filetypes-tar.gz-388062cdae015a34/route_policy_eval_oof.md \
	--output-json /home/t/collimator/out/models/azoth-candidate-filetypes-tar.gz-388062cdae015a34/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-tar.gz-388062cdae015a34/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-tar.gz-388062cdae015a34/route_policy_eval_oof.md
.venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filetypes-tar.gz-388062cdae015a34
staged runtime azoth bundle: /tmp/tmp.hQW12Db3IW
azoth bundle ok: /tmp/tmp.hQW12Db3IW

12 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - c: L3 hostile ENSEMBLE recall dropped 0.91pp BELOW LOW-WATER-MARK (10.93% → 10.02%; LWM tolerance 0.90pp)
  - csharp: L3 hostile ENSEMBLE recall dropped 2.14pp BELOW LOW-WATER-MARK (27.35% → 25.21%; LWM tolerance 0.90pp)
  - docx: L3 hostile ENSEMBLE recall dropped 2.27pp BELOW LOW-WATER-MARK (73.86% → 71.59%; LWM tolerance 0.90pp)
  - gz: L3 hostile ENSEMBLE recall dropped 3.47pp BELOW LOW-WATER-MARK (31.79% → 28.32%; LWM tolerance 0.90pp)
  - javascript: L3 hostile ENSEMBLE recall dropped 5.71pp BELOW LOW-WATER-MARK (71.91% → 66.20%; LWM tolerance 0.90pp)
  - kotlin: L3 hostile ENSEMBLE recall dropped 4.39pp BELOW LOW-WATER-MARK (57.06% → 52.67%; LWM tolerance 0.90pp)
  - pe: L3 hostile ENSEMBLE recall dropped 3.26pp BELOW LOW-WATER-MARK (65.21% → 61.96%; LWM tolerance 0.90pp)
  - powershell: L3 hostile ENSEMBLE recall dropped 8.85pp BELOW LOW-WATER-MARK (38.46% → 29.62%; LWM tolerance 0.90pp)
  - pptx: L3 hostile ENSEMBLE recall dropped 13.64pp BELOW LOW-WATER-MARK (22.73% → 9.09%; LWM tolerance 0.90pp)
  - python: L3 hostile ENSEMBLE recall dropped 2.73pp BELOW LOW-WATER-MARK (67.00% → 64.28%; LWM tolerance 0.90pp)
  - tar: L3 hostile ENSEMBLE recall dropped 14.00pp BELOW LOW-WATER-MARK (76.00% → 62.00%; LWM tolerance 0.90pp)
  - zip: L3 hostile ENSEMBLE recall dropped 1.38pp BELOW LOW-WATER-MARK (41.99% → 40.61%; LWM tolerance 0.90pp)

compared 63 filetypes (mal≥1, ben≥1); 2 below threshold and skipped.

blocked by: low-water-mark gate (0.90pp vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[1]: *** [Makefile:1117: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9994)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `388062cdae015a34` | `d251dec3e738261e` | `c9178b59b963b00f` |
| PR AUC | 0.9994 | 0.9994 | 0.9994 |
| ROC AUC | 0.9987 | 0.9988 | 0.9988 |
| F1 | 0.9913 | 0.9921 | 0.9914 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-24T08-32-32_20260524T083032-promote-388062cdae015a34_azoth-validate.log; tail: wrote /home/t/collimator/out/models/azoth-candidate-filetypes-tar.gz-388062cdae015a34/global_policy_metrics.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-tar.gz-388062cdae015a34/global_policy_metrics.md
.venv/bin/python scripts/compute_routed_metrics.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filetypes-tar.gz-388062cdae015a34 --db postgres://hopper@localhost:5432/hopper --no-ci --no-stacked 
computing test-partition metrics (reporting)
loaded cached test-bucket mask: /home/t/collimator/out/cache/azoth-test-masks/test-947ff4cebbdd8fe06d90df9b8d8e0e32f498a93413f371a2883896fb3f53512a.npz
test bucket: 588814/4731967 rows (12.44%)
fitting per-route isotonic calibrators (5-fold CV) over 588814 rows (parallelism=16)
calibration complete; computing per-filetype metrics
filetypes/xlsb: 0 rows in score table; skipping
computing dev-partition metrics (strategy selection)
loaded cached dev-bucket mask: /home/t/collimator/out/cache/azoth-test-masks/dev-947ff4cebbdd8fe06d90df9b8d8e0e32f498a93413f371a2883896fb3f53512a.npz
dev bucket: 589608/4731967 rows (12.46%)
fitting per-route isotonic calibrators (5-fold CV) over 589608 rows (parallelism=16)
calibration complete; computing per-filetype metrics
filetypes/xlsb: 0 rows in score table; skipping
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-tar.gz-388062cdae015a34/per_filetype_metrics.json (filetypes: 78, filegroups: 0)
.venv/bin/python scripts/azoth_route_policy_eval.py \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-tar.gz-388062cdae015a34/score_table.npz \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filetypes-tar.gz-388062cdae015a34/general/threshold_scores.npz \
	--route-policies /home/t/collimator/out/models/azoth-candidate-filetypes-tar.gz-388062cdae015a34/route_policies.json \
	--partition test \
	--output-md /home/t/collimator/out/models/azoth-candidate-filetypes-tar.gz-388062cdae015a34/route_policy_eval_oof.md \
	--output-json /home/t/collimator/out/models/azoth-candidate-filetypes-tar.gz-388062cdae015a34/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-tar.gz-388062cdae015a34/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-tar.gz-388062cdae015a34/route_policy_eval_oof.md
.venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filetypes-tar.gz-388062cdae015a34
staged runtime azoth bundle: /tmp/tmp.hQW12Db3IW
azoth bundle ok: /tmp/tmp.hQW12Db3IW

12 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - c: L3 hostile ENSEMBLE recall dropped 0.91pp BELOW LOW-WATER-MARK (10.93% → 10.02%; LWM tolerance 0.90pp)
  - csharp: L3 hostile ENSEMBLE recall dropped 2.14pp BELOW LOW-WATER-MARK (27.35% → 25.21%; LWM tolerance 0.90pp)
  - docx: L3 hostile ENSEMBLE recall dropped 2.27pp BELOW LOW-WATER-MARK (73.86% → 71.59%; LWM tolerance 0.90pp)
  - gz: L3 hostile ENSEMBLE recall dropped 3.47pp BELOW LOW-WATER-MARK (31.79% → 28.32%; LWM tolerance 0.90pp)
  - javascript: L3 hostile ENSEMBLE recall dropped 5.71pp BELOW LOW-WATER-MARK (71.91% → 66.20%; LWM tolerance 0.90pp)
  - kotlin: L3 hostile ENSEMBLE recall dropped 4.39pp BELOW LOW-WATER-MARK (57.06% → 52.67%; LWM tolerance 0.90pp)
  - pe: L3 hostile ENSEMBLE recall dropped 3.26pp BELOW LOW-WATER-MARK (65.21% → 61.96%; LWM tolerance 0.90pp)
  - powershell: L3 hostile ENSEMBLE recall dropped 8.85pp BELOW LOW-WATER-MARK (38.46% → 29.62%; LWM tolerance 0.90pp)
  - pptx: L3 hostile ENSEMBLE recall dropped 13.64pp BELOW LOW-WATER-MARK (22.73% → 9.09%; LWM tolerance 0.90pp)
  - python: L3 hostile ENSEMBLE recall dropped 2.73pp BELOW LOW-WATER-MARK (67.00% → 64.28%; LWM tolerance 0.90pp)
  - tar: L3 hostile ENSEMBLE recall dropped 14.00pp BELOW LOW-WATER-MARK (76.00% → 62.00%; LWM tolerance 0.90pp)
  - zip: L3 hostile ENSEMBLE recall dropped 1.38pp BELOW LOW-WATER-MARK (41.99% → 40.61%; LWM tolerance 0.90pp)

compared 63 filetypes (mal≥1, ben≥1); 2 below threshold and skipped.

blocked by: low-water-mark gate (0.90pp vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[1]: *** [Makefile:1117: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')
