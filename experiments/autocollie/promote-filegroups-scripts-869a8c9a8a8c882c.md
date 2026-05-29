# Promote REJECTED — `869a8c9a8a8c882c` on `filegroups/scripts`

Generated 2026-05-26T04:40:44Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-26T04-31-56_20260526T042855-promote-869a8c9a8a8c882c_azoth-validate.log; tail: 	--output-md /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-869a8c9a8a8c882c/route_policy_eval_oof.md \
	--output-json /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-869a8c9a8a8c882c/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-869a8c9a8a8c882c/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-869a8c9a8a8c882c/route_policy_eval_oof.md
.venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-869a8c9a8a8c882c
staged runtime azoth bundle: /tmp/tmp.GJFVc5Ir0S
azoth bundle ok: /tmp/tmp.GJFVc5Ir0S
--source-bundle out/models/azoth: 1 routes changed → 9 filetypes impacted, 57 unimpacted (drift treated as pre-existing)

ensemble improvements (≥0.10pp):
  c: L3 hostile ensemble recall +1.42pp (11.33% → 12.74%)
  javascript: L3 hostile ensemble recall +3.11pp (72.12% → 75.23%)
  powershell: L3 hostile ensemble recall +1.15pp (31.15% → 32.31%)
  python: L3 hostile ensemble recall +0.31pp (66.33% → 66.64%)

per-route improvements (≥0.10pp, informational):
  c :: filetypes/c recall@3FP/M +0.11pp (13.82% → 13.93%)
  perl :: filegroups/scripts recall@3FP/M +7.41pp (85.19% → 92.59%)
  powershell :: filegroups/scripts recall@3FP/M +11.15pp (51.15% → 62.31%)
  python :: filegroups/scripts recall@3FP/M +4.65pp (63.42% → 68.08%)

per-route regressions (informational; does not block deploy):
  batch :: filegroups/scripts recall@3FP/M dropped 98.31pp (99.01% → 0.71%)
  lua :: filegroups/scripts recall@3FP/M dropped 16.67pp (66.67% → 50.00%)
  php :: filegroups/scripts recall@3FP/M dropped 2.73pp (66.60% → 63.87%)

13 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + c: L3 hostile ensemble recall +2.72pp above LWM (10.02% → 12.74%)
  + java_class: L3 hostile ensemble recall +2.89pp above LWM (73.41% → 76.30%)
  + javascript: L3 hostile ensemble recall +9.03pp above LWM (66.20% → 75.23%)
  + lnk: L3 hostile ensemble recall +13.03pp above LWM (48.66% → 61.69%)
  + package.json: L3 hostile ensemble recall +4.35pp above LWM (86.78% → 91.12%)
  + pdf: L3 hostile ensemble recall +1.09pp above LWM (6.41% → 7.50%)
  + perl: L3 hostile ensemble recall +7.41pp above LWM (77.78% → 85.19%)
  + png: L3 hostile ensemble recall +3.20pp above LWM (1.07% → 4.26%)
  + powershell: L3 hostile ensemble recall +2.69pp above LWM (29.62% → 32.31%)
  + pptx: L3 hostile ensemble recall +9.09pp above LWM (9.09% → 18.18%)
  + python: L3 hostile ensemble recall +2.36pp above LWM (64.28% → 66.64%)
  + xls: L3 hostile ensemble recall +2.78pp above LWM (92.44% → 95.22%)
  + xml: L3 hostile ensemble recall +8.22pp above LWM (2.74% → 10.96%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - batch: L3 hostile ENSEMBLE recall dropped 4.92pp BELOW LOW-WATER-MARK (98.83% → 93.91%; LWM tolerance 0.90pp)

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
| key | `869a8c9a8a8c882c` | `c4079c88a61fb8be` | `91e630261066c42e` |
| PR AUC | 0.9978 | 0.9993 | 0.9994 |
| ROC AUC | 0.9977 | 0.9992 | 0.9992 |
| F1 | 0.9730 | 0.9827 | 0.9846 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-26T04-31-56_20260526T042855-promote-869a8c9a8a8c882c_azoth-validate.log; tail: 	--output-md /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-869a8c9a8a8c882c/route_policy_eval_oof.md \
	--output-json /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-869a8c9a8a8c882c/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-869a8c9a8a8c882c/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-869a8c9a8a8c882c/route_policy_eval_oof.md
.venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-869a8c9a8a8c882c
staged runtime azoth bundle: /tmp/tmp.GJFVc5Ir0S
azoth bundle ok: /tmp/tmp.GJFVc5Ir0S
--source-bundle out/models/azoth: 1 routes changed → 9 filetypes impacted, 57 unimpacted (drift treated as pre-existing)

ensemble improvements (≥0.10pp):
  c: L3 hostile ensemble recall +1.42pp (11.33% → 12.74%)
  javascript: L3 hostile ensemble recall +3.11pp (72.12% → 75.23%)
  powershell: L3 hostile ensemble recall +1.15pp (31.15% → 32.31%)
  python: L3 hostile ensemble recall +0.31pp (66.33% → 66.64%)

per-route improvements (≥0.10pp, informational):
  c :: filetypes/c recall@3FP/M +0.11pp (13.82% → 13.93%)
  perl :: filegroups/scripts recall@3FP/M +7.41pp (85.19% → 92.59%)
  powershell :: filegroups/scripts recall@3FP/M +11.15pp (51.15% → 62.31%)
  python :: filegroups/scripts recall@3FP/M +4.65pp (63.42% → 68.08%)

per-route regressions (informational; does not block deploy):
  batch :: filegroups/scripts recall@3FP/M dropped 98.31pp (99.01% → 0.71%)
  lua :: filegroups/scripts recall@3FP/M dropped 16.67pp (66.67% → 50.00%)
  php :: filegroups/scripts recall@3FP/M dropped 2.73pp (66.60% → 63.87%)

13 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + c: L3 hostile ensemble recall +2.72pp above LWM (10.02% → 12.74%)
  + java_class: L3 hostile ensemble recall +2.89pp above LWM (73.41% → 76.30%)
  + javascript: L3 hostile ensemble recall +9.03pp above LWM (66.20% → 75.23%)
  + lnk: L3 hostile ensemble recall +13.03pp above LWM (48.66% → 61.69%)
  + package.json: L3 hostile ensemble recall +4.35pp above LWM (86.78% → 91.12%)
  + pdf: L3 hostile ensemble recall +1.09pp above LWM (6.41% → 7.50%)
  + perl: L3 hostile ensemble recall +7.41pp above LWM (77.78% → 85.19%)
  + png: L3 hostile ensemble recall +3.20pp above LWM (1.07% → 4.26%)
  + powershell: L3 hostile ensemble recall +2.69pp above LWM (29.62% → 32.31%)
  + pptx: L3 hostile ensemble recall +9.09pp above LWM (9.09% → 18.18%)
  + python: L3 hostile ensemble recall +2.36pp above LWM (64.28% → 66.64%)
  + xls: L3 hostile ensemble recall +2.78pp above LWM (92.44% → 95.22%)
  + xml: L3 hostile ensemble recall +8.22pp above LWM (2.74% → 10.96%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - batch: L3 hostile ENSEMBLE recall dropped 4.92pp BELOW LOW-WATER-MARK (98.83% → 93.91%; LWM tolerance 0.90pp)

compared 63 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: deployed-tolerance gate (1.70pp), low-water-mark gate (0.90pp vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1136: azoth-validate] Error 1)
