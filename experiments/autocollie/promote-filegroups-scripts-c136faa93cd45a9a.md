# Promote REJECTED — `c136faa93cd45a9a` on `filegroups/scripts`

Generated 2026-05-28T04:00:50Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-28T03-53-18_20260528T034722-promote-c136faa93cd45a9a_azoth-validate.log; tail:   perl :: filegroups/scripts recall@3FP/M +3.57pp (85.71% → 89.29%)
  powershell :: filegroups/scripts recall@3FP/M +21.66pp (37.43% → 59.09%)
  python :: filegroups/scripts recall@3FP/M +3.22pp (65.08% → 68.31%)
  shell :: filegroups/scripts recall@3FP/M +4.49pp (75.47% → 79.96%)

per-route regressions (informational; does not block deploy):
  batch :: filegroups/scripts recall@3FP/M dropped 98.30pp (98.94% → 0.64%)
  lua :: filegroups/scripts recall@3FP/M dropped 16.67pp (66.67% → 50.00%)
  php :: filegroups/scripts recall@3FP/M dropped 3.77pp (66.60% → 62.83%)
  ruby :: filegroups/scripts recall@3FP/M dropped 14.29pp (100.00% → 85.71%)

24 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + 7z: L3 hostile ensemble recall +14.84pp above LWM (72.74% → 87.59%)
  + c: L3 hostile ensemble recall +2.60pp above LWM (10.02% → 12.62%)
  + cab: L3 hostile ensemble recall +46.55pp above LWM (3.45% → 50.00%)
  + chrome-manifest: L3 hostile ensemble recall +16.67pp above LWM (50.00% → 66.67%)
  + crx: L3 hostile ensemble recall +10.81pp above LWM (0.00% → 10.81%)
  + docx: L3 hostile ensemble recall +1.09pp above LWM (71.59% → 72.68%)
  + html: L3 hostile ensemble recall +83.33pp above LWM (16.67% → 100.00%)
  + jpeg: L3 hostile ensemble recall +9.12pp above LWM (1.56% → 10.69%)
  + lnk: L3 hostile ensemble recall +22.72pp above LWM (48.66% → 71.38%)
  + package.json: L3 hostile ensemble recall +2.50pp above LWM (86.78% → 89.28%)
  + pe: L3 hostile ensemble recall +7.30pp above LWM (61.96% → 69.26%)
  + perl: L3 hostile ensemble recall +11.51pp above LWM (77.78% → 89.29%)
  + php: L3 hostile ensemble recall +4.12pp above LWM (62.11% → 66.23%)
  + plist: L3 hostile ensemble recall +1.47pp above LWM (2.94% → 4.41%)
  + png: L3 hostile ensemble recall +7.72pp above LWM (1.07% → 8.79%)
  + powershell: L3 hostile ensemble recall +8.89pp above LWM (29.62% → 38.50%)
  + ruby: L3 hostile ensemble recall +14.29pp above LWM (28.57% → 42.86%)
  + tar: L3 hostile ensemble recall +35.37pp above LWM (62.00% → 97.37%)
  + tar.gz: L3 hostile ensemble recall +12.57pp above LWM (56.69% → 69.27%)
  + xls: L3 hostile ensemble recall +2.72pp above LWM (92.44% → 95.16%)
  + xlsx: L3 hostile ensemble recall +4.47pp above LWM (29.01% → 33.48%)
  + xml: L3 hostile ensemble recall +6.06pp above LWM (2.74% → 8.79%)
  + zip: L3 hostile ensemble recall +11.38pp above LWM (40.61% → 51.99%)
  + zst: L3 hostile ensemble recall +1.98pp above LWM (76.60% → 78.58%)

4 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - batch: L3 hostile ENSEMBLE recall dropped 4.80pp BELOW LOW-WATER-MARK (98.83% → 94.04%; LWM tolerance 0.90pp)
  - javascript: L3 hostile ENSEMBLE recall dropped 2.12pp BELOW LOW-WATER-MARK (66.20% → 64.08%; LWM tolerance 0.90pp)
  - python: L3 hostile ENSEMBLE recall dropped 3.41pp BELOW LOW-WATER-MARK (64.28% → 60.86%; LWM tolerance 0.90pp)
  - shell: L3 hostile ENSEMBLE recall dropped 8.46pp BELOW LOW-WATER-MARK (82.78% → 74.32%; LWM tolerance 0.90pp)

compared 64 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: low-water-mark gate (0.90pp vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[1]: *** [Makefile:1136: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9975)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `c136faa93cd45a9a` | `ca39521ad01b4fb6` | `4cdb5cd33f8184dc` |
| PR AUC | 0.9975 | 0.9989 | 0.9991 |
| ROC AUC | 0.9973 | 0.9988 | 0.9989 |
| F1 | 0.9706 | 0.9778 | 0.9815 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-28T03-53-18_20260528T034722-promote-c136faa93cd45a9a_azoth-validate.log; tail:   perl :: filegroups/scripts recall@3FP/M +3.57pp (85.71% → 89.29%)
  powershell :: filegroups/scripts recall@3FP/M +21.66pp (37.43% → 59.09%)
  python :: filegroups/scripts recall@3FP/M +3.22pp (65.08% → 68.31%)
  shell :: filegroups/scripts recall@3FP/M +4.49pp (75.47% → 79.96%)

per-route regressions (informational; does not block deploy):
  batch :: filegroups/scripts recall@3FP/M dropped 98.30pp (98.94% → 0.64%)
  lua :: filegroups/scripts recall@3FP/M dropped 16.67pp (66.67% → 50.00%)
  php :: filegroups/scripts recall@3FP/M dropped 3.77pp (66.60% → 62.83%)
  ruby :: filegroups/scripts recall@3FP/M dropped 14.29pp (100.00% → 85.71%)

24 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + 7z: L3 hostile ensemble recall +14.84pp above LWM (72.74% → 87.59%)
  + c: L3 hostile ensemble recall +2.60pp above LWM (10.02% → 12.62%)
  + cab: L3 hostile ensemble recall +46.55pp above LWM (3.45% → 50.00%)
  + chrome-manifest: L3 hostile ensemble recall +16.67pp above LWM (50.00% → 66.67%)
  + crx: L3 hostile ensemble recall +10.81pp above LWM (0.00% → 10.81%)
  + docx: L3 hostile ensemble recall +1.09pp above LWM (71.59% → 72.68%)
  + html: L3 hostile ensemble recall +83.33pp above LWM (16.67% → 100.00%)
  + jpeg: L3 hostile ensemble recall +9.12pp above LWM (1.56% → 10.69%)
  + lnk: L3 hostile ensemble recall +22.72pp above LWM (48.66% → 71.38%)
  + package.json: L3 hostile ensemble recall +2.50pp above LWM (86.78% → 89.28%)
  + pe: L3 hostile ensemble recall +7.30pp above LWM (61.96% → 69.26%)
  + perl: L3 hostile ensemble recall +11.51pp above LWM (77.78% → 89.29%)
  + php: L3 hostile ensemble recall +4.12pp above LWM (62.11% → 66.23%)
  + plist: L3 hostile ensemble recall +1.47pp above LWM (2.94% → 4.41%)
  + png: L3 hostile ensemble recall +7.72pp above LWM (1.07% → 8.79%)
  + powershell: L3 hostile ensemble recall +8.89pp above LWM (29.62% → 38.50%)
  + ruby: L3 hostile ensemble recall +14.29pp above LWM (28.57% → 42.86%)
  + tar: L3 hostile ensemble recall +35.37pp above LWM (62.00% → 97.37%)
  + tar.gz: L3 hostile ensemble recall +12.57pp above LWM (56.69% → 69.27%)
  + xls: L3 hostile ensemble recall +2.72pp above LWM (92.44% → 95.16%)
  + xlsx: L3 hostile ensemble recall +4.47pp above LWM (29.01% → 33.48%)
  + xml: L3 hostile ensemble recall +6.06pp above LWM (2.74% → 8.79%)
  + zip: L3 hostile ensemble recall +11.38pp above LWM (40.61% → 51.99%)
  + zst: L3 hostile ensemble recall +1.98pp above LWM (76.60% → 78.58%)

4 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - batch: L3 hostile ENSEMBLE recall dropped 4.80pp BELOW LOW-WATER-MARK (98.83% → 94.04%; LWM tolerance 0.90pp)
  - javascript: L3 hostile ENSEMBLE recall dropped 2.12pp BELOW LOW-WATER-MARK (66.20% → 64.08%; LWM tolerance 0.90pp)
  - python: L3 hostile ENSEMBLE recall dropped 3.41pp BELOW LOW-WATER-MARK (64.28% → 60.86%; LWM tolerance 0.90pp)
  - shell: L3 hostile ENSEMBLE recall dropped 8.46pp BELOW LOW-WATER-MARK (82.78% → 74.32%; LWM tolerance 0.90pp)

compared 64 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: low-water-mark gate (0.90pp vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[1]: *** [Makefile:1136: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')
