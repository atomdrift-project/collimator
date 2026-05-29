# Promote REJECTED — `f9bf3522cd7221f6` on `filegroups/scripts`

Generated 2026-05-26T05:21:36Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-26T05-15-36_20260526T051531-promote-f9bf3522cd7221f6_azoth-validate.log; tail: wrote /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-f9bf3522cd7221f6/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-f9bf3522cd7221f6/route_policy_eval_oof.md
.venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-f9bf3522cd7221f6
staged runtime azoth bundle: /tmp/tmp.xo1R2TUMOQ
azoth bundle ok: /tmp/tmp.xo1R2TUMOQ
--source-bundle out/models/azoth: 1 routes changed → 9 filetypes impacted, 57 unimpacted (drift treated as pre-existing)

ensemble improvements (≥0.10pp):
  c: L3 hostile ensemble recall +1.42pp (11.33% → 12.74%)
  javascript: L3 hostile ensemble recall +1.24pp (72.12% → 73.36%)
  php: L3 hostile ensemble recall +0.20pp (62.11% → 62.30%)
  powershell: L3 hostile ensemble recall +1.15pp (31.15% → 32.31%)

per-route improvements (≥0.10pp, informational):
  c :: filetypes/c recall@3FP/M +0.11pp (13.82% → 13.93%)
  javascript :: filegroups/scripts recall@3FP/M +0.34pp (75.73% → 76.07%)
  perl :: filegroups/scripts recall@3FP/M +7.41pp (85.19% → 92.59%)
  powershell :: filegroups/scripts recall@3FP/M +8.08pp (51.15% → 59.23%)
  python :: filegroups/scripts recall@3FP/M +1.48pp (63.42% → 64.91%)
  shell :: filegroups/scripts recall@3FP/M +0.24pp (81.32% → 81.56%)

per-route regressions (informational; does not block deploy):
  batch :: filegroups/scripts recall@3FP/M dropped 98.30pp (99.01% → 0.71%)
  lua :: filegroups/scripts recall@3FP/M dropped 16.67pp (66.67% → 50.00%)
  php :: filegroups/scripts recall@3FP/M dropped 3.32pp (66.60% → 63.28%)

13 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + c: L3 hostile ensemble recall +2.72pp above LWM (10.02% → 12.74%)
  + java_class: L3 hostile ensemble recall +2.89pp above LWM (73.41% → 76.30%)
  + javascript: L3 hostile ensemble recall +7.16pp above LWM (66.20% → 73.36%)
  + lnk: L3 hostile ensemble recall +13.03pp above LWM (48.66% → 61.69%)
  + package.json: L3 hostile ensemble recall +4.35pp above LWM (86.78% → 91.12%)
  + pdf: L3 hostile ensemble recall +1.09pp above LWM (6.41% → 7.50%)
  + perl: L3 hostile ensemble recall +7.41pp above LWM (77.78% → 85.19%)
  + png: L3 hostile ensemble recall +3.20pp above LWM (1.07% → 4.26%)
  + powershell: L3 hostile ensemble recall +2.69pp above LWM (29.62% → 32.31%)
  + pptx: L3 hostile ensemble recall +9.09pp above LWM (9.09% → 18.18%)
  + python: L3 hostile ensemble recall +2.14pp above LWM (64.28% → 66.42%)
  + xls: L3 hostile ensemble recall +2.78pp above LWM (92.44% → 95.22%)
  + xml: L3 hostile ensemble recall +8.22pp above LWM (2.74% → 10.96%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - batch: L3 hostile ENSEMBLE recall dropped 4.91pp BELOW LOW-WATER-MARK (98.83% → 93.92%; LWM tolerance 0.90pp)

compared 63 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: deployed-tolerance gate (1.70pp), low-water-mark gate (0.90pp vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1136: azoth-validate] Error 1)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9978)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `f9bf3522cd7221f6` | `fa6be051c8b0809c` | `3e6afabf181aab16` |
| PR AUC | 0.9978 | 0.9993 | 0.9993 |
| ROC AUC | 0.9976 | 0.9991 | 0.9992 |
| F1 | 0.9768 | 0.9840 | 0.9828 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-26T05-15-36_20260526T051531-promote-f9bf3522cd7221f6_azoth-validate.log; tail: wrote /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-f9bf3522cd7221f6/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-f9bf3522cd7221f6/route_policy_eval_oof.md
.venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-f9bf3522cd7221f6
staged runtime azoth bundle: /tmp/tmp.xo1R2TUMOQ
azoth bundle ok: /tmp/tmp.xo1R2TUMOQ
--source-bundle out/models/azoth: 1 routes changed → 9 filetypes impacted, 57 unimpacted (drift treated as pre-existing)

ensemble improvements (≥0.10pp):
  c: L3 hostile ensemble recall +1.42pp (11.33% → 12.74%)
  javascript: L3 hostile ensemble recall +1.24pp (72.12% → 73.36%)
  php: L3 hostile ensemble recall +0.20pp (62.11% → 62.30%)
  powershell: L3 hostile ensemble recall +1.15pp (31.15% → 32.31%)

per-route improvements (≥0.10pp, informational):
  c :: filetypes/c recall@3FP/M +0.11pp (13.82% → 13.93%)
  javascript :: filegroups/scripts recall@3FP/M +0.34pp (75.73% → 76.07%)
  perl :: filegroups/scripts recall@3FP/M +7.41pp (85.19% → 92.59%)
  powershell :: filegroups/scripts recall@3FP/M +8.08pp (51.15% → 59.23%)
  python :: filegroups/scripts recall@3FP/M +1.48pp (63.42% → 64.91%)
  shell :: filegroups/scripts recall@3FP/M +0.24pp (81.32% → 81.56%)

per-route regressions (informational; does not block deploy):
  batch :: filegroups/scripts recall@3FP/M dropped 98.30pp (99.01% → 0.71%)
  lua :: filegroups/scripts recall@3FP/M dropped 16.67pp (66.67% → 50.00%)
  php :: filegroups/scripts recall@3FP/M dropped 3.32pp (66.60% → 63.28%)

13 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + c: L3 hostile ensemble recall +2.72pp above LWM (10.02% → 12.74%)
  + java_class: L3 hostile ensemble recall +2.89pp above LWM (73.41% → 76.30%)
  + javascript: L3 hostile ensemble recall +7.16pp above LWM (66.20% → 73.36%)
  + lnk: L3 hostile ensemble recall +13.03pp above LWM (48.66% → 61.69%)
  + package.json: L3 hostile ensemble recall +4.35pp above LWM (86.78% → 91.12%)
  + pdf: L3 hostile ensemble recall +1.09pp above LWM (6.41% → 7.50%)
  + perl: L3 hostile ensemble recall +7.41pp above LWM (77.78% → 85.19%)
  + png: L3 hostile ensemble recall +3.20pp above LWM (1.07% → 4.26%)
  + powershell: L3 hostile ensemble recall +2.69pp above LWM (29.62% → 32.31%)
  + pptx: L3 hostile ensemble recall +9.09pp above LWM (9.09% → 18.18%)
  + python: L3 hostile ensemble recall +2.14pp above LWM (64.28% → 66.42%)
  + xls: L3 hostile ensemble recall +2.78pp above LWM (92.44% → 95.22%)
  + xml: L3 hostile ensemble recall +8.22pp above LWM (2.74% → 10.96%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - batch: L3 hostile ENSEMBLE recall dropped 4.91pp BELOW LOW-WATER-MARK (98.83% → 93.92%; LWM tolerance 0.90pp)

compared 63 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: deployed-tolerance gate (1.70pp), low-water-mark gate (0.90pp vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1136: azoth-validate] Error 1)
