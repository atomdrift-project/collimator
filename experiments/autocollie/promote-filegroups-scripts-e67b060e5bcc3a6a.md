# Promote REJECTED — `e67b060e5bcc3a6a` on `filegroups/scripts`

Generated 2026-05-25T18:51:46Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-25T18-46-36_20260525T184634-promote-e67b060e5bcc3a6a_azoth-validate.log; tail: wrote /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-e67b060e5bcc3a6a/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-e67b060e5bcc3a6a/route_policy_eval_oof.md
.venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-e67b060e5bcc3a6a
staged runtime azoth bundle: /tmp/tmp.zVxFLwVXLK
azoth bundle ok: /tmp/tmp.zVxFLwVXLK
--source-bundle out/models/azoth: 1 routes changed → 9 filetypes impacted, 56 unimpacted (drift treated as pre-existing)

ensemble improvements (≥0.10pp):
  c: L3 hostile ensemble recall +1.30pp (10.02% → 11.33%)
  elf: L3 hostile ensemble recall +0.70pp (92.79% → 93.49%)
  javascript: L3 hostile ensemble recall +9.80pp (66.20% → 76.00%)
  package.json: L3 hostile ensemble recall +4.25pp (86.78% → 91.03%)
  perl: L3 hostile ensemble recall +3.70pp (77.78% → 81.48%)
  powershell: L3 hostile ensemble recall +3.08pp (29.62% → 32.69%)
  xml: L3 hostile ensemble recall +6.16pp (2.74% → 8.90%)

per-route improvements (≥0.10pp, informational):
  c :: filetypes/c recall@3FP/M +0.28pp (13.53% → 13.82%)
  elf :: filetypes/elf recall@3FP/M +3.40pp (93.40% → 96.81%)
  go :: filetypes/go recall@3FP/M +0.59pp (4.84% → 5.44%)
  javascript :: filetypes/javascript recall@3FP/M +12.81pp (65.71% → 78.52%)
  package.json :: filegroups/config recall@3FP/M +0.83pp (98.71% → 99.54%)
  package.json :: filetypes/package.json recall@3FP/M +1.02pp (98.66% → 99.68%)
  perl :: filegroups/scripts recall@3FP/M +7.41pp (85.19% → 92.59%)
  powershell :: filegroups/scripts recall@3FP/M +6.54pp (51.15% → 57.69%)
  python :: filegroups/scripts recall@3FP/M +4.83pp (63.40% → 68.22%)
  xml :: filegroups/config recall@3FP/M +12.33pp (3.42% → 15.75%)

per-route regressions (informational; does not block deploy):
  batch :: filegroups/scripts recall@3FP/M dropped 98.32pp (99.01% → 0.70%)
  lua :: filegroups/scripts recall@3FP/M dropped 16.67pp (66.67% → 50.00%)
  php :: filegroups/scripts recall@3FP/M dropped 2.15pp (66.60% → 64.45%)

6 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + c: L3 hostile ensemble recall +1.30pp above LWM (10.02% → 11.33%)
  + javascript: L3 hostile ensemble recall +9.80pp above LWM (66.20% → 76.00%)
  + package.json: L3 hostile ensemble recall +4.25pp above LWM (86.78% → 91.03%)
  + perl: L3 hostile ensemble recall +3.70pp above LWM (77.78% → 81.48%)
  + powershell: L3 hostile ensemble recall +3.08pp above LWM (29.62% → 32.69%)
  + xml: L3 hostile ensemble recall +6.16pp above LWM (2.74% → 8.90%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - batch: L3 hostile ENSEMBLE recall dropped 4.89pp BELOW LOW-WATER-MARK (98.83% → 93.94%; LWM tolerance 0.90pp)

compared 63 filetypes (mal≥1, ben≥1); 2 below threshold and skipped.

blocked by: deployed-tolerance gate (1.70pp), low-water-mark gate (0.90pp vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1136: azoth-validate] Error 1)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9979)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `e67b060e5bcc3a6a` | `2b909e7b127047e7` | `525cc1261f5dd553` |
| PR AUC | 0.9979 | 0.9993 | 0.9994 |
| ROC AUC | 0.9977 | 0.9992 | 0.9993 |
| F1 | 0.9725 | 0.9834 | 0.9840 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-25T18-46-36_20260525T184634-promote-e67b060e5bcc3a6a_azoth-validate.log; tail: wrote /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-e67b060e5bcc3a6a/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-e67b060e5bcc3a6a/route_policy_eval_oof.md
.venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-e67b060e5bcc3a6a
staged runtime azoth bundle: /tmp/tmp.zVxFLwVXLK
azoth bundle ok: /tmp/tmp.zVxFLwVXLK
--source-bundle out/models/azoth: 1 routes changed → 9 filetypes impacted, 56 unimpacted (drift treated as pre-existing)

ensemble improvements (≥0.10pp):
  c: L3 hostile ensemble recall +1.30pp (10.02% → 11.33%)
  elf: L3 hostile ensemble recall +0.70pp (92.79% → 93.49%)
  javascript: L3 hostile ensemble recall +9.80pp (66.20% → 76.00%)
  package.json: L3 hostile ensemble recall +4.25pp (86.78% → 91.03%)
  perl: L3 hostile ensemble recall +3.70pp (77.78% → 81.48%)
  powershell: L3 hostile ensemble recall +3.08pp (29.62% → 32.69%)
  xml: L3 hostile ensemble recall +6.16pp (2.74% → 8.90%)

per-route improvements (≥0.10pp, informational):
  c :: filetypes/c recall@3FP/M +0.28pp (13.53% → 13.82%)
  elf :: filetypes/elf recall@3FP/M +3.40pp (93.40% → 96.81%)
  go :: filetypes/go recall@3FP/M +0.59pp (4.84% → 5.44%)
  javascript :: filetypes/javascript recall@3FP/M +12.81pp (65.71% → 78.52%)
  package.json :: filegroups/config recall@3FP/M +0.83pp (98.71% → 99.54%)
  package.json :: filetypes/package.json recall@3FP/M +1.02pp (98.66% → 99.68%)
  perl :: filegroups/scripts recall@3FP/M +7.41pp (85.19% → 92.59%)
  powershell :: filegroups/scripts recall@3FP/M +6.54pp (51.15% → 57.69%)
  python :: filegroups/scripts recall@3FP/M +4.83pp (63.40% → 68.22%)
  xml :: filegroups/config recall@3FP/M +12.33pp (3.42% → 15.75%)

per-route regressions (informational; does not block deploy):
  batch :: filegroups/scripts recall@3FP/M dropped 98.32pp (99.01% → 0.70%)
  lua :: filegroups/scripts recall@3FP/M dropped 16.67pp (66.67% → 50.00%)
  php :: filegroups/scripts recall@3FP/M dropped 2.15pp (66.60% → 64.45%)

6 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + c: L3 hostile ensemble recall +1.30pp above LWM (10.02% → 11.33%)
  + javascript: L3 hostile ensemble recall +9.80pp above LWM (66.20% → 76.00%)
  + package.json: L3 hostile ensemble recall +4.25pp above LWM (86.78% → 91.03%)
  + perl: L3 hostile ensemble recall +3.70pp above LWM (77.78% → 81.48%)
  + powershell: L3 hostile ensemble recall +3.08pp above LWM (29.62% → 32.69%)
  + xml: L3 hostile ensemble recall +6.16pp above LWM (2.74% → 8.90%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - batch: L3 hostile ENSEMBLE recall dropped 4.89pp BELOW LOW-WATER-MARK (98.83% → 93.94%; LWM tolerance 0.90pp)

compared 63 filetypes (mal≥1, ben≥1); 2 below threshold and skipped.

blocked by: deployed-tolerance gate (1.70pp), low-water-mark gate (0.90pp vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1136: azoth-validate] Error 1)
