# Promote REJECTED — `affdf7987dbfb9b2` on `filegroups/scripts`

Generated 2026-05-26T05:15:29Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-26T05-08-12_20260526T050410-promote-affdf7987dbfb9b2_azoth-validate.log; tail: wrote /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-affdf7987dbfb9b2/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-affdf7987dbfb9b2/route_policy_eval_oof.md
.venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-affdf7987dbfb9b2
staged runtime azoth bundle: /tmp/tmp.2XqmWL1qTk
azoth bundle ok: /tmp/tmp.2XqmWL1qTk
--source-bundle out/models/azoth: 1 routes changed → 9 filetypes impacted, 57 unimpacted (drift treated as pre-existing)

ensemble improvements (≥0.10pp):
  c: L3 hostile ensemble recall +1.42pp (11.33% → 12.74%)
  javascript: L3 hostile ensemble recall +2.95pp (72.12% → 75.07%)
  powershell: L3 hostile ensemble recall +4.62pp (31.15% → 35.77%)
  python: L3 hostile ensemble recall +0.48pp (66.33% → 66.81%)

per-route improvements (≥0.10pp, informational):
  c :: filetypes/c recall@3FP/M +0.11pp (13.82% → 13.93%)
  javascript :: filegroups/scripts recall@3FP/M +0.28pp (75.73% → 76.01%)
  perl :: filegroups/scripts recall@3FP/M +7.41pp (85.19% → 92.59%)
  powershell :: filegroups/scripts recall@3FP/M +3.08pp (51.15% → 54.23%)
  python :: filegroups/scripts recall@3FP/M +3.64pp (63.42% → 67.06%)

per-route regressions (informational; does not block deploy):
  batch :: filegroups/scripts recall@3FP/M dropped 98.32pp (99.01% → 0.69%)
  lua :: filegroups/scripts recall@3FP/M dropped 16.67pp (66.67% → 50.00%)
  php :: filegroups/scripts recall@3FP/M dropped 2.34pp (66.60% → 64.26%)
  shell :: filegroups/scripts recall@3FP/M dropped 1.71pp (81.32% → 79.61%)

13 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + c: L3 hostile ensemble recall +2.72pp above LWM (10.02% → 12.74%)
  + java_class: L3 hostile ensemble recall +2.89pp above LWM (73.41% → 76.30%)
  + javascript: L3 hostile ensemble recall +8.87pp above LWM (66.20% → 75.07%)
  + lnk: L3 hostile ensemble recall +13.03pp above LWM (48.66% → 61.69%)
  + package.json: L3 hostile ensemble recall +4.35pp above LWM (86.78% → 91.12%)
  + pdf: L3 hostile ensemble recall +1.09pp above LWM (6.41% → 7.50%)
  + perl: L3 hostile ensemble recall +7.41pp above LWM (77.78% → 85.19%)
  + png: L3 hostile ensemble recall +3.20pp above LWM (1.07% → 4.26%)
  + powershell: L3 hostile ensemble recall +6.15pp above LWM (29.62% → 35.77%)
  + pptx: L3 hostile ensemble recall +9.09pp above LWM (9.09% → 18.18%)
  + python: L3 hostile ensemble recall +2.54pp above LWM (64.28% → 66.81%)
  + xls: L3 hostile ensemble recall +2.78pp above LWM (92.44% → 95.22%)
  + xml: L3 hostile ensemble recall +8.22pp above LWM (2.74% → 10.96%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - batch: L3 hostile ENSEMBLE recall dropped 4.94pp BELOW LOW-WATER-MARK (98.83% → 93.89%; LWM tolerance 0.90pp)

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
| key | `affdf7987dbfb9b2` | `7ac45566219f1064` | `02ba2685eabe7992` |
| PR AUC | 0.9978 | 0.9993 | 0.9994 |
| ROC AUC | 0.9977 | 0.9992 | 0.9992 |
| F1 | 0.9772 | 0.9834 | 0.9853 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-26T05-08-12_20260526T050410-promote-affdf7987dbfb9b2_azoth-validate.log; tail: wrote /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-affdf7987dbfb9b2/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-affdf7987dbfb9b2/route_policy_eval_oof.md
.venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-affdf7987dbfb9b2
staged runtime azoth bundle: /tmp/tmp.2XqmWL1qTk
azoth bundle ok: /tmp/tmp.2XqmWL1qTk
--source-bundle out/models/azoth: 1 routes changed → 9 filetypes impacted, 57 unimpacted (drift treated as pre-existing)

ensemble improvements (≥0.10pp):
  c: L3 hostile ensemble recall +1.42pp (11.33% → 12.74%)
  javascript: L3 hostile ensemble recall +2.95pp (72.12% → 75.07%)
  powershell: L3 hostile ensemble recall +4.62pp (31.15% → 35.77%)
  python: L3 hostile ensemble recall +0.48pp (66.33% → 66.81%)

per-route improvements (≥0.10pp, informational):
  c :: filetypes/c recall@3FP/M +0.11pp (13.82% → 13.93%)
  javascript :: filegroups/scripts recall@3FP/M +0.28pp (75.73% → 76.01%)
  perl :: filegroups/scripts recall@3FP/M +7.41pp (85.19% → 92.59%)
  powershell :: filegroups/scripts recall@3FP/M +3.08pp (51.15% → 54.23%)
  python :: filegroups/scripts recall@3FP/M +3.64pp (63.42% → 67.06%)

per-route regressions (informational; does not block deploy):
  batch :: filegroups/scripts recall@3FP/M dropped 98.32pp (99.01% → 0.69%)
  lua :: filegroups/scripts recall@3FP/M dropped 16.67pp (66.67% → 50.00%)
  php :: filegroups/scripts recall@3FP/M dropped 2.34pp (66.60% → 64.26%)
  shell :: filegroups/scripts recall@3FP/M dropped 1.71pp (81.32% → 79.61%)

13 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + c: L3 hostile ensemble recall +2.72pp above LWM (10.02% → 12.74%)
  + java_class: L3 hostile ensemble recall +2.89pp above LWM (73.41% → 76.30%)
  + javascript: L3 hostile ensemble recall +8.87pp above LWM (66.20% → 75.07%)
  + lnk: L3 hostile ensemble recall +13.03pp above LWM (48.66% → 61.69%)
  + package.json: L3 hostile ensemble recall +4.35pp above LWM (86.78% → 91.12%)
  + pdf: L3 hostile ensemble recall +1.09pp above LWM (6.41% → 7.50%)
  + perl: L3 hostile ensemble recall +7.41pp above LWM (77.78% → 85.19%)
  + png: L3 hostile ensemble recall +3.20pp above LWM (1.07% → 4.26%)
  + powershell: L3 hostile ensemble recall +6.15pp above LWM (29.62% → 35.77%)
  + pptx: L3 hostile ensemble recall +9.09pp above LWM (9.09% → 18.18%)
  + python: L3 hostile ensemble recall +2.54pp above LWM (64.28% → 66.81%)
  + xls: L3 hostile ensemble recall +2.78pp above LWM (92.44% → 95.22%)
  + xml: L3 hostile ensemble recall +8.22pp above LWM (2.74% → 10.96%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - batch: L3 hostile ENSEMBLE recall dropped 4.94pp BELOW LOW-WATER-MARK (98.83% → 93.89%; LWM tolerance 0.90pp)

compared 63 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: deployed-tolerance gate (1.70pp), low-water-mark gate (0.90pp vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1136: azoth-validate] Error 1)
