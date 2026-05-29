# Promote REJECTED — `3fd1b804c6667ff3` on `filegroups/scripts`

Generated 2026-05-26T04:55:24Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-26T04-48-53_20260526T044520-promote-3fd1b804c6667ff3_azoth-validate.log; tail: 	--output-json /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-3fd1b804c6667ff3/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-3fd1b804c6667ff3/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-3fd1b804c6667ff3/route_policy_eval_oof.md
.venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-3fd1b804c6667ff3
staged runtime azoth bundle: /tmp/tmp.4mzhAopBbu
azoth bundle ok: /tmp/tmp.4mzhAopBbu
--source-bundle out/models/azoth: 1 routes changed → 9 filetypes impacted, 57 unimpacted (drift treated as pre-existing)

ensemble improvements (≥0.10pp):
  c: L3 hostile ensemble recall +1.42pp (11.33% → 12.74%)
  javascript: L3 hostile ensemble recall +2.06pp (72.12% → 74.18%)
  powershell: L3 hostile ensemble recall +5.38pp (31.15% → 36.54%)
  shell: L3 hostile ensemble recall +0.24pp (82.78% → 83.03%)

per-route improvements (≥0.10pp, informational):
  c :: filetypes/c recall@3FP/M +0.11pp (13.82% → 13.93%)
  perl :: filegroups/scripts recall@3FP/M +7.41pp (85.19% → 92.59%)
  powershell :: filegroups/scripts recall@3FP/M +5.00pp (51.15% → 56.15%)
  python :: filegroups/scripts recall@3FP/M +4.26pp (63.42% → 67.68%)

per-route regressions (informational; does not block deploy):
  batch :: filegroups/scripts recall@3FP/M dropped 98.31pp (99.01% → 0.71%)
  javascript :: filegroups/scripts recall@3FP/M dropped 1.75pp (75.73% → 73.98%)
  lua :: filegroups/scripts recall@3FP/M dropped 16.67pp (66.67% → 50.00%)
  shell :: filegroups/scripts recall@3FP/M dropped 2.32pp (81.32% → 79.00%)

13 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + c: L3 hostile ensemble recall +2.72pp above LWM (10.02% → 12.74%)
  + java_class: L3 hostile ensemble recall +2.89pp above LWM (73.41% → 76.30%)
  + javascript: L3 hostile ensemble recall +7.98pp above LWM (66.20% → 74.18%)
  + lnk: L3 hostile ensemble recall +13.03pp above LWM (48.66% → 61.69%)
  + package.json: L3 hostile ensemble recall +4.35pp above LWM (86.78% → 91.12%)
  + pdf: L3 hostile ensemble recall +1.09pp above LWM (6.41% → 7.50%)
  + perl: L3 hostile ensemble recall +7.41pp above LWM (77.78% → 85.19%)
  + png: L3 hostile ensemble recall +3.20pp above LWM (1.07% → 4.26%)
  + powershell: L3 hostile ensemble recall +6.92pp above LWM (29.62% → 36.54%)
  + pptx: L3 hostile ensemble recall +9.09pp above LWM (9.09% → 18.18%)
  + python: L3 hostile ensemble recall +2.10pp above LWM (64.28% → 66.37%)
  + xls: L3 hostile ensemble recall +2.78pp above LWM (92.44% → 95.22%)
  + xml: L3 hostile ensemble recall +8.22pp above LWM (2.74% → 10.96%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - batch: L3 hostile ENSEMBLE recall dropped 4.87pp BELOW LOW-WATER-MARK (98.83% → 93.97%; LWM tolerance 0.90pp)

compared 63 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: deployed-tolerance gate (1.70pp), low-water-mark gate (0.90pp vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1136: azoth-validate] Error 1)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9977)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `3fd1b804c6667ff3` | `f682ac9c385c7e80` | `93a2117c9cc66c00` |
| PR AUC | 0.9977 | 0.9993 | 0.9994 |
| ROC AUC | 0.9975 | 0.9992 | 0.9993 |
| F1 | 0.9723 | 0.9841 | 0.9843 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-26T04-48-53_20260526T044520-promote-3fd1b804c6667ff3_azoth-validate.log; tail: 	--output-json /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-3fd1b804c6667ff3/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-3fd1b804c6667ff3/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-3fd1b804c6667ff3/route_policy_eval_oof.md
.venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-3fd1b804c6667ff3
staged runtime azoth bundle: /tmp/tmp.4mzhAopBbu
azoth bundle ok: /tmp/tmp.4mzhAopBbu
--source-bundle out/models/azoth: 1 routes changed → 9 filetypes impacted, 57 unimpacted (drift treated as pre-existing)

ensemble improvements (≥0.10pp):
  c: L3 hostile ensemble recall +1.42pp (11.33% → 12.74%)
  javascript: L3 hostile ensemble recall +2.06pp (72.12% → 74.18%)
  powershell: L3 hostile ensemble recall +5.38pp (31.15% → 36.54%)
  shell: L3 hostile ensemble recall +0.24pp (82.78% → 83.03%)

per-route improvements (≥0.10pp, informational):
  c :: filetypes/c recall@3FP/M +0.11pp (13.82% → 13.93%)
  perl :: filegroups/scripts recall@3FP/M +7.41pp (85.19% → 92.59%)
  powershell :: filegroups/scripts recall@3FP/M +5.00pp (51.15% → 56.15%)
  python :: filegroups/scripts recall@3FP/M +4.26pp (63.42% → 67.68%)

per-route regressions (informational; does not block deploy):
  batch :: filegroups/scripts recall@3FP/M dropped 98.31pp (99.01% → 0.71%)
  javascript :: filegroups/scripts recall@3FP/M dropped 1.75pp (75.73% → 73.98%)
  lua :: filegroups/scripts recall@3FP/M dropped 16.67pp (66.67% → 50.00%)
  shell :: filegroups/scripts recall@3FP/M dropped 2.32pp (81.32% → 79.00%)

13 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + c: L3 hostile ensemble recall +2.72pp above LWM (10.02% → 12.74%)
  + java_class: L3 hostile ensemble recall +2.89pp above LWM (73.41% → 76.30%)
  + javascript: L3 hostile ensemble recall +7.98pp above LWM (66.20% → 74.18%)
  + lnk: L3 hostile ensemble recall +13.03pp above LWM (48.66% → 61.69%)
  + package.json: L3 hostile ensemble recall +4.35pp above LWM (86.78% → 91.12%)
  + pdf: L3 hostile ensemble recall +1.09pp above LWM (6.41% → 7.50%)
  + perl: L3 hostile ensemble recall +7.41pp above LWM (77.78% → 85.19%)
  + png: L3 hostile ensemble recall +3.20pp above LWM (1.07% → 4.26%)
  + powershell: L3 hostile ensemble recall +6.92pp above LWM (29.62% → 36.54%)
  + pptx: L3 hostile ensemble recall +9.09pp above LWM (9.09% → 18.18%)
  + python: L3 hostile ensemble recall +2.10pp above LWM (64.28% → 66.37%)
  + xls: L3 hostile ensemble recall +2.78pp above LWM (92.44% → 95.22%)
  + xml: L3 hostile ensemble recall +8.22pp above LWM (2.74% → 10.96%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - batch: L3 hostile ENSEMBLE recall dropped 4.87pp BELOW LOW-WATER-MARK (98.83% → 93.97%; LWM tolerance 0.90pp)

compared 63 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: deployed-tolerance gate (1.70pp), low-water-mark gate (0.90pp vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1136: azoth-validate] Error 1)
