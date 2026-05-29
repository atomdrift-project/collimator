# Promote REJECTED — `d79c1cbb52c60a9b` on `filetypes/pe`

Generated 2026-05-26T11:06:39Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-26T10-52-37_20260526T104409-promote-d79c1cbb52c60a9b_azoth-validate.log; tail: filetypes/xlsb: 0 rows in score table; skipping
filetypes/pyproject.toml: 0 rows in score table; skipping
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-pe-d79c1cbb52c60a9b/per_filetype_metrics.json (filetypes: 79, filegroups: 0)
.venv/bin/python scripts/azoth_route_policy_eval.py \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-pe-d79c1cbb52c60a9b/score_table.npz \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filetypes-pe-d79c1cbb52c60a9b/general/threshold_scores.npz \
	--route-policies /home/t/collimator/out/models/azoth-candidate-filetypes-pe-d79c1cbb52c60a9b/route_policies.json \
	--partition test \
	--output-md /home/t/collimator/out/models/azoth-candidate-filetypes-pe-d79c1cbb52c60a9b/route_policy_eval_oof.md \
	--output-json /home/t/collimator/out/models/azoth-candidate-filetypes-pe-d79c1cbb52c60a9b/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-pe-d79c1cbb52c60a9b/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-pe-d79c1cbb52c60a9b/route_policy_eval_oof.md
.venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filetypes-pe-d79c1cbb52c60a9b
staged runtime azoth bundle: /tmp/tmp.WBRBNL7FAi
azoth bundle ok: /tmp/tmp.WBRBNL7FAi
--source-bundle out/models/azoth: 1 routes changed → 1 filetypes impacted, 65 unimpacted (drift treated as pre-existing)

ensemble improvements (≥0.10pp):
  c: L3 hostile ensemble recall +1.42pp (11.33% → 12.74%)
  javascript: L3 hostile ensemble recall +2.43pp (72.12% → 74.55%)

per-route improvements (≥0.10pp, informational):
  c :: filetypes/c recall@3FP/M +0.11pp (13.82% → 13.93%)
  javascript :: filetypes/javascript recall@3FP/M +2.19pp (76.95% → 79.14%)
  pe :: filetypes/pe recall@3FP/M +10.34pp (61.35% → 71.69%)

13 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + c: L3 hostile ensemble recall +2.72pp above LWM (10.02% → 12.74%)
  + java_class: L3 hostile ensemble recall +2.89pp above LWM (73.41% → 76.30%)
  + javascript: L3 hostile ensemble recall +8.35pp above LWM (66.20% → 74.55%)
  + lnk: L3 hostile ensemble recall +13.03pp above LWM (48.66% → 61.69%)
  + package.json: L3 hostile ensemble recall +4.35pp above LWM (86.78% → 91.12%)
  + pdf: L3 hostile ensemble recall +1.09pp above LWM (6.41% → 7.50%)
  + perl: L3 hostile ensemble recall +7.41pp above LWM (77.78% → 85.19%)
  + png: L3 hostile ensemble recall +3.20pp above LWM (1.07% → 4.26%)
  + powershell: L3 hostile ensemble recall +1.54pp above LWM (29.62% → 31.15%)
  + pptx: L3 hostile ensemble recall +9.09pp above LWM (9.09% → 18.18%)
  + python: L3 hostile ensemble recall +2.05pp above LWM (64.28% → 66.33%)
  + xls: L3 hostile ensemble recall +2.78pp above LWM (92.44% → 95.22%)
  + xml: L3 hostile ensemble recall +8.22pp above LWM (2.74% → 10.96%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - pe: L3 hostile ENSEMBLE recall dropped 3.30pp BELOW LOW-WATER-MARK (61.96% → 58.65%; LWM tolerance 0.90pp)

compared 63 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: deployed-tolerance gate (1.70pp), low-water-mark gate (0.90pp vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1136: azoth-validate] Error 1)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9997)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `d79c1cbb52c60a9b` | `c2042031ec133528` | `2ec949e634cb078a` |
| PR AUC | 0.9997 | 1.0000 | 1.0000 |
| ROC AUC | 0.9997 | 0.9999 | 0.9999 |
| F1 | 0.9899 | 0.9987 | 0.9974 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-26T10-52-37_20260526T104409-promote-d79c1cbb52c60a9b_azoth-validate.log; tail: filetypes/xlsb: 0 rows in score table; skipping
filetypes/pyproject.toml: 0 rows in score table; skipping
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-pe-d79c1cbb52c60a9b/per_filetype_metrics.json (filetypes: 79, filegroups: 0)
.venv/bin/python scripts/azoth_route_policy_eval.py \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-pe-d79c1cbb52c60a9b/score_table.npz \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filetypes-pe-d79c1cbb52c60a9b/general/threshold_scores.npz \
	--route-policies /home/t/collimator/out/models/azoth-candidate-filetypes-pe-d79c1cbb52c60a9b/route_policies.json \
	--partition test \
	--output-md /home/t/collimator/out/models/azoth-candidate-filetypes-pe-d79c1cbb52c60a9b/route_policy_eval_oof.md \
	--output-json /home/t/collimator/out/models/azoth-candidate-filetypes-pe-d79c1cbb52c60a9b/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-pe-d79c1cbb52c60a9b/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-pe-d79c1cbb52c60a9b/route_policy_eval_oof.md
.venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filetypes-pe-d79c1cbb52c60a9b
staged runtime azoth bundle: /tmp/tmp.WBRBNL7FAi
azoth bundle ok: /tmp/tmp.WBRBNL7FAi
--source-bundle out/models/azoth: 1 routes changed → 1 filetypes impacted, 65 unimpacted (drift treated as pre-existing)

ensemble improvements (≥0.10pp):
  c: L3 hostile ensemble recall +1.42pp (11.33% → 12.74%)
  javascript: L3 hostile ensemble recall +2.43pp (72.12% → 74.55%)

per-route improvements (≥0.10pp, informational):
  c :: filetypes/c recall@3FP/M +0.11pp (13.82% → 13.93%)
  javascript :: filetypes/javascript recall@3FP/M +2.19pp (76.95% → 79.14%)
  pe :: filetypes/pe recall@3FP/M +10.34pp (61.35% → 71.69%)

13 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + c: L3 hostile ensemble recall +2.72pp above LWM (10.02% → 12.74%)
  + java_class: L3 hostile ensemble recall +2.89pp above LWM (73.41% → 76.30%)
  + javascript: L3 hostile ensemble recall +8.35pp above LWM (66.20% → 74.55%)
  + lnk: L3 hostile ensemble recall +13.03pp above LWM (48.66% → 61.69%)
  + package.json: L3 hostile ensemble recall +4.35pp above LWM (86.78% → 91.12%)
  + pdf: L3 hostile ensemble recall +1.09pp above LWM (6.41% → 7.50%)
  + perl: L3 hostile ensemble recall +7.41pp above LWM (77.78% → 85.19%)
  + png: L3 hostile ensemble recall +3.20pp above LWM (1.07% → 4.26%)
  + powershell: L3 hostile ensemble recall +1.54pp above LWM (29.62% → 31.15%)
  + pptx: L3 hostile ensemble recall +9.09pp above LWM (9.09% → 18.18%)
  + python: L3 hostile ensemble recall +2.05pp above LWM (64.28% → 66.33%)
  + xls: L3 hostile ensemble recall +2.78pp above LWM (92.44% → 95.22%)
  + xml: L3 hostile ensemble recall +8.22pp above LWM (2.74% → 10.96%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - pe: L3 hostile ENSEMBLE recall dropped 3.30pp BELOW LOW-WATER-MARK (61.96% → 58.65%; LWM tolerance 0.90pp)

compared 63 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: deployed-tolerance gate (1.70pp), low-water-mark gate (0.90pp vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1136: azoth-validate] Error 1)
