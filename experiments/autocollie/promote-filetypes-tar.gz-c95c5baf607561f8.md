# Promote REJECTED — `c95c5baf607561f8` on `filetypes/tar.gz`

Generated 2026-05-24T13:08:09Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-24T13-03-21_20260524T130019-promote-c95c5baf607561f8_azoth-validate.log; tail: filetypes/xlsb: 0 rows in score table; skipping
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-tar.gz-c95c5baf607561f8/per_filetype_metrics.json (filetypes: 78, filegroups: 0)
.venv/bin/python scripts/azoth_route_policy_eval.py \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-tar.gz-c95c5baf607561f8/score_table.npz \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filetypes-tar.gz-c95c5baf607561f8/general/threshold_scores.npz \
	--route-policies /home/t/collimator/out/models/azoth-candidate-filetypes-tar.gz-c95c5baf607561f8/route_policies.json \
	--partition test \
	--output-md /home/t/collimator/out/models/azoth-candidate-filetypes-tar.gz-c95c5baf607561f8/route_policy_eval_oof.md \
	--output-json /home/t/collimator/out/models/azoth-candidate-filetypes-tar.gz-c95c5baf607561f8/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-tar.gz-c95c5baf607561f8/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-tar.gz-c95c5baf607561f8/route_policy_eval_oof.md
.venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filetypes-tar.gz-c95c5baf607561f8
staged runtime azoth bundle: /tmp/tmp.DnIAOmrkFK
azoth bundle ok: /tmp/tmp.DnIAOmrkFK

12 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + cab: L3 hostile ensemble recall +3.45pp above LWM (0.00% → 3.45%)
  + doc: L3 hostile ensemble recall +18.80pp above LWM (72.18% → 90.99%)
  + html: L3 hostile ensemble recall +16.67pp above LWM (0.00% → 16.67%)
  + java: L3 hostile ensemble recall +25.00pp above LWM (25.00% → 50.00%)
  + macho: L3 hostile ensemble recall +2.67pp above LWM (83.97% → 86.64%)
  + msi: L3 hostile ensemble recall +18.72pp above LWM (57.45% → 76.17%)
  + package.json: L3 hostile ensemble recall +5.59pp above LWM (81.18% → 86.78%)
  + perl: L3 hostile ensemble recall +51.85pp above LWM (25.93% → 77.78%)
  + php: L3 hostile ensemble recall +9.57pp above LWM (52.54% → 62.11%)
  + png: L3 hostile ensemble recall +1.07pp above LWM (0.00% → 1.07%)
  + shell: L3 hostile ensemble recall +0.98pp above LWM (81.81% → 82.78%)
  + tar.gz: L3 hostile ensemble recall +1.07pp above LWM (55.63% → 56.69%)

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
| key | `c95c5baf607561f8` | `679a6e6720691894` | `083776fd861ddbcb` |
| PR AUC | 0.9994 | 0.9994 | 0.9994 |
| ROC AUC | 0.9987 | 0.9988 | 0.9988 |
| F1 | 0.9890 | 0.9916 | 0.9925 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-24T13-03-21_20260524T130019-promote-c95c5baf607561f8_azoth-validate.log; tail: filetypes/xlsb: 0 rows in score table; skipping
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-tar.gz-c95c5baf607561f8/per_filetype_metrics.json (filetypes: 78, filegroups: 0)
.venv/bin/python scripts/azoth_route_policy_eval.py \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-tar.gz-c95c5baf607561f8/score_table.npz \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filetypes-tar.gz-c95c5baf607561f8/general/threshold_scores.npz \
	--route-policies /home/t/collimator/out/models/azoth-candidate-filetypes-tar.gz-c95c5baf607561f8/route_policies.json \
	--partition test \
	--output-md /home/t/collimator/out/models/azoth-candidate-filetypes-tar.gz-c95c5baf607561f8/route_policy_eval_oof.md \
	--output-json /home/t/collimator/out/models/azoth-candidate-filetypes-tar.gz-c95c5baf607561f8/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-tar.gz-c95c5baf607561f8/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-tar.gz-c95c5baf607561f8/route_policy_eval_oof.md
.venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filetypes-tar.gz-c95c5baf607561f8
staged runtime azoth bundle: /tmp/tmp.DnIAOmrkFK
azoth bundle ok: /tmp/tmp.DnIAOmrkFK

12 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + cab: L3 hostile ensemble recall +3.45pp above LWM (0.00% → 3.45%)
  + doc: L3 hostile ensemble recall +18.80pp above LWM (72.18% → 90.99%)
  + html: L3 hostile ensemble recall +16.67pp above LWM (0.00% → 16.67%)
  + java: L3 hostile ensemble recall +25.00pp above LWM (25.00% → 50.00%)
  + macho: L3 hostile ensemble recall +2.67pp above LWM (83.97% → 86.64%)
  + msi: L3 hostile ensemble recall +18.72pp above LWM (57.45% → 76.17%)
  + package.json: L3 hostile ensemble recall +5.59pp above LWM (81.18% → 86.78%)
  + perl: L3 hostile ensemble recall +51.85pp above LWM (25.93% → 77.78%)
  + php: L3 hostile ensemble recall +9.57pp above LWM (52.54% → 62.11%)
  + png: L3 hostile ensemble recall +1.07pp above LWM (0.00% → 1.07%)
  + shell: L3 hostile ensemble recall +0.98pp above LWM (81.81% → 82.78%)
  + tar.gz: L3 hostile ensemble recall +1.07pp above LWM (55.63% → 56.69%)

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
