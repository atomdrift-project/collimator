# Promote REJECTED — `07bc5b056e10b50d` on `filetypes/java_class`

Generated 2026-05-26T19:30:14Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-26T19-25-40_20260526T192528-promote-07bc5b056e10b50d_azoth-validate.log; tail: fitting per-route isotonic calibrators (5-fold CV) over 589608 rows (parallelism=16, cache=out/cache/azoth-calibrator)
calibration complete; computing per-filetype metrics
filetypes/xlsb: 0 rows in score table; skipping
filetypes/pyproject.toml: 0 rows in score table; skipping
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-java_class-07bc5b056e10b50d/per_filetype_metrics.json (filetypes: 79, filegroups: 0)
.venv/bin/python scripts/azoth_route_policy_eval.py \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-java_class-07bc5b056e10b50d/score_table.npz \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filetypes-java_class-07bc5b056e10b50d/general/threshold_scores.npz \
	--route-policies /home/t/collimator/out/models/azoth-candidate-filetypes-java_class-07bc5b056e10b50d/route_policies.json \
	--partition test \
	--output-md /home/t/collimator/out/models/azoth-candidate-filetypes-java_class-07bc5b056e10b50d/route_policy_eval_oof.md \
	--output-json /home/t/collimator/out/models/azoth-candidate-filetypes-java_class-07bc5b056e10b50d/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-java_class-07bc5b056e10b50d/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-java_class-07bc5b056e10b50d/route_policy_eval_oof.md
.venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filetypes-java_class-07bc5b056e10b50d
staged runtime azoth bundle: /tmp/tmp.EdhDSFZgiu
azoth bundle ok: /tmp/tmp.EdhDSFZgiu
--source-bundle out/models/azoth: 1 routes changed → 1 filetypes impacted, 65 unimpacted (drift treated as pre-existing)

ensemble improvements (≥0.10pp):
  xls: L3 hostile ensemble recall +0.31pp (95.22% → 95.53%)

per-route regressions (informational; does not block deploy):
  java_class :: filetypes/java_class recall@3FP/M dropped 2.91pp (84.30% → 81.40%)

14 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + c: L3 hostile ensemble recall +2.72pp above LWM (10.02% → 12.74%)
  + javascript: L3 hostile ensemble recall +8.35pp above LWM (66.20% → 74.55%)
  + lnk: L3 hostile ensemble recall +13.03pp above LWM (48.66% → 61.69%)
  + package.json: L3 hostile ensemble recall +3.79pp above LWM (86.78% → 90.57%)
  + pdf: L3 hostile ensemble recall +1.09pp above LWM (6.41% → 7.50%)
  + pe: L3 hostile ensemble recall +2.21pp above LWM (61.96% → 64.17%)
  + perl: L3 hostile ensemble recall +7.41pp above LWM (77.78% → 85.19%)
  + plist: L3 hostile ensemble recall +1.47pp above LWM (2.94% → 4.41%)
  + png: L3 hostile ensemble recall +3.20pp above LWM (1.07% → 4.26%)
  + powershell: L3 hostile ensemble recall +1.54pp above LWM (29.62% → 31.15%)
  + pptx: L3 hostile ensemble recall +9.09pp above LWM (9.09% → 18.18%)
  + python: L3 hostile ensemble recall +2.05pp above LWM (64.28% → 66.33%)
  + xls: L3 hostile ensemble recall +3.08pp above LWM (92.44% → 95.53%)
  + xml: L3 hostile ensemble recall +5.48pp above LWM (2.74% → 8.22%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - java_class: L3 hostile ENSEMBLE recall dropped 2.31pp BELOW LOW-WATER-MARK (73.41% → 71.10%; LWM tolerance 0.90pp)

compared 63 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: low-water-mark gate (0.90pp vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1136: azoth-validate] Error 1)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 1.0000)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `07bc5b056e10b50d` | `4fbd37f13e1fe5f4` | `f47adf9736a90ae2` |
| PR AUC | 1.0000 | 0.9958 | 0.9962 |
| ROC AUC | 1.0000 | 0.9990 | 0.9991 |
| F1 | 0.9922 | 0.9737 | 0.9772 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-26T19-25-40_20260526T192528-promote-07bc5b056e10b50d_azoth-validate.log; tail: fitting per-route isotonic calibrators (5-fold CV) over 589608 rows (parallelism=16, cache=out/cache/azoth-calibrator)
calibration complete; computing per-filetype metrics
filetypes/xlsb: 0 rows in score table; skipping
filetypes/pyproject.toml: 0 rows in score table; skipping
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-java_class-07bc5b056e10b50d/per_filetype_metrics.json (filetypes: 79, filegroups: 0)
.venv/bin/python scripts/azoth_route_policy_eval.py \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-java_class-07bc5b056e10b50d/score_table.npz \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filetypes-java_class-07bc5b056e10b50d/general/threshold_scores.npz \
	--route-policies /home/t/collimator/out/models/azoth-candidate-filetypes-java_class-07bc5b056e10b50d/route_policies.json \
	--partition test \
	--output-md /home/t/collimator/out/models/azoth-candidate-filetypes-java_class-07bc5b056e10b50d/route_policy_eval_oof.md \
	--output-json /home/t/collimator/out/models/azoth-candidate-filetypes-java_class-07bc5b056e10b50d/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-java_class-07bc5b056e10b50d/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-java_class-07bc5b056e10b50d/route_policy_eval_oof.md
.venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filetypes-java_class-07bc5b056e10b50d
staged runtime azoth bundle: /tmp/tmp.EdhDSFZgiu
azoth bundle ok: /tmp/tmp.EdhDSFZgiu
--source-bundle out/models/azoth: 1 routes changed → 1 filetypes impacted, 65 unimpacted (drift treated as pre-existing)

ensemble improvements (≥0.10pp):
  xls: L3 hostile ensemble recall +0.31pp (95.22% → 95.53%)

per-route regressions (informational; does not block deploy):
  java_class :: filetypes/java_class recall@3FP/M dropped 2.91pp (84.30% → 81.40%)

14 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + c: L3 hostile ensemble recall +2.72pp above LWM (10.02% → 12.74%)
  + javascript: L3 hostile ensemble recall +8.35pp above LWM (66.20% → 74.55%)
  + lnk: L3 hostile ensemble recall +13.03pp above LWM (48.66% → 61.69%)
  + package.json: L3 hostile ensemble recall +3.79pp above LWM (86.78% → 90.57%)
  + pdf: L3 hostile ensemble recall +1.09pp above LWM (6.41% → 7.50%)
  + pe: L3 hostile ensemble recall +2.21pp above LWM (61.96% → 64.17%)
  + perl: L3 hostile ensemble recall +7.41pp above LWM (77.78% → 85.19%)
  + plist: L3 hostile ensemble recall +1.47pp above LWM (2.94% → 4.41%)
  + png: L3 hostile ensemble recall +3.20pp above LWM (1.07% → 4.26%)
  + powershell: L3 hostile ensemble recall +1.54pp above LWM (29.62% → 31.15%)
  + pptx: L3 hostile ensemble recall +9.09pp above LWM (9.09% → 18.18%)
  + python: L3 hostile ensemble recall +2.05pp above LWM (64.28% → 66.33%)
  + xls: L3 hostile ensemble recall +3.08pp above LWM (92.44% → 95.53%)
  + xml: L3 hostile ensemble recall +5.48pp above LWM (2.74% → 8.22%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - java_class: L3 hostile ENSEMBLE recall dropped 2.31pp BELOW LOW-WATER-MARK (73.41% → 71.10%; LWM tolerance 0.90pp)

compared 63 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: low-water-mark gate (0.90pp vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1136: azoth-validate] Error 1)
