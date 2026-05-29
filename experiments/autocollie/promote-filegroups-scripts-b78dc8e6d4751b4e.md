# Promote REJECTED — `b78dc8e6d4751b4e` on `filegroups/scripts`

Generated 2026-05-28T10:22:23Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-28T10-14-36_20260528T101007-promote-b78dc8e6d4751b4e_azoth-validate.log; tail:   powershell :: filegroups/scripts recall@3FP/M +19.25pp (37.43% → 56.68%)
  python :: filegroups/scripts recall@3FP/M +1.70pp (65.08% → 66.78%)
  shell :: filegroups/scripts recall@3FP/M +4.07pp (75.47% → 79.54%)
  shell :: filetypes/shell recall@3FP/M +32.15pp (55.01% → 87.16%)

per-route regressions (informational; does not block deploy):
  batch :: filegroups/scripts recall@3FP/M dropped 98.33pp (98.94% → 0.61%)
  lua :: filegroups/scripts recall@3FP/M dropped 16.67pp (66.67% → 50.00%)
  ruby :: filegroups/scripts recall@3FP/M dropped 14.29pp (100.00% → 85.71%)

27 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + 7z: L3 hostile ensemble recall +14.84pp above LWM (72.74% → 87.59%)
  + c: L3 hostile ensemble recall +2.26pp above LWM (10.02% → 12.28%)
  + cab: L3 hostile ensemble recall +46.55pp above LWM (3.45% → 50.00%)
  + chrome-manifest: L3 hostile ensemble recall +16.67pp above LWM (50.00% → 66.67%)
  + crx: L3 hostile ensemble recall +10.81pp above LWM (0.00% → 10.81%)
  + docx: L3 hostile ensemble recall +1.09pp above LWM (71.59% → 72.68%)
  + go: L3 hostile ensemble recall +3.40pp above LWM (1.36% → 4.76%)
  + html: L3 hostile ensemble recall +83.33pp above LWM (16.67% → 100.00%)
  + javascript: L3 hostile ensemble recall +9.79pp above LWM (66.20% → 75.99%)
  + jpeg: L3 hostile ensemble recall +9.12pp above LWM (1.56% → 10.69%)
  + lnk: L3 hostile ensemble recall +22.72pp above LWM (48.66% → 71.38%)
  + package.json: L3 hostile ensemble recall +2.50pp above LWM (86.78% → 89.28%)
  + pe: L3 hostile ensemble recall +7.30pp above LWM (61.96% → 69.26%)
  + perl: L3 hostile ensemble recall +11.51pp above LWM (77.78% → 89.29%)
  + php: L3 hostile ensemble recall +3.93pp above LWM (62.11% → 66.04%)
  + plist: L3 hostile ensemble recall +1.47pp above LWM (2.94% → 4.41%)
  + png: L3 hostile ensemble recall +7.72pp above LWM (1.07% → 8.79%)
  + powershell: L3 hostile ensemble recall +1.94pp above LWM (29.62% → 31.55%)
  + ruby: L3 hostile ensemble recall +14.29pp above LWM (28.57% → 42.86%)
  + shell: L3 hostile ensemble recall +1.25pp above LWM (82.78% → 84.03%)
  + tar: L3 hostile ensemble recall +35.37pp above LWM (62.00% → 97.37%)
  + tar.gz: L3 hostile ensemble recall +12.57pp above LWM (56.69% → 69.27%)
  + xls: L3 hostile ensemble recall +2.72pp above LWM (92.44% → 95.16%)
  + xlsx: L3 hostile ensemble recall +4.47pp above LWM (29.01% → 33.48%)
  + xml: L3 hostile ensemble recall +6.06pp above LWM (2.74% → 8.79%)
  + zip: L3 hostile ensemble recall +11.38pp above LWM (40.61% → 51.99%)
  + zst: L3 hostile ensemble recall +1.98pp above LWM (76.60% → 78.58%)

2 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - batch: L3 hostile ENSEMBLE recall dropped 4.80pp BELOW LOW-WATER-MARK (98.83% → 94.04%; LWM tolerance 0.90pp)
  - python: L3 hostile ENSEMBLE recall dropped 2.41pp BELOW LOW-WATER-MARK (64.28% → 61.86%; LWM tolerance 0.90pp)

compared 64 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: low-water-mark gate (0.90pp vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[1]: *** [Makefile:1136: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9974)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `b78dc8e6d4751b4e` | `b4d89319f564efea` | `4f19a93906ef48b2` |
| PR AUC | 0.9974 | 0.9988 | 0.9990 |
| ROC AUC | 0.9972 | 0.9986 | 0.9989 |
| F1 | 0.9731 | 0.9766 | 0.9800 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-28T10-14-36_20260528T101007-promote-b78dc8e6d4751b4e_azoth-validate.log; tail:   powershell :: filegroups/scripts recall@3FP/M +19.25pp (37.43% → 56.68%)
  python :: filegroups/scripts recall@3FP/M +1.70pp (65.08% → 66.78%)
  shell :: filegroups/scripts recall@3FP/M +4.07pp (75.47% → 79.54%)
  shell :: filetypes/shell recall@3FP/M +32.15pp (55.01% → 87.16%)

per-route regressions (informational; does not block deploy):
  batch :: filegroups/scripts recall@3FP/M dropped 98.33pp (98.94% → 0.61%)
  lua :: filegroups/scripts recall@3FP/M dropped 16.67pp (66.67% → 50.00%)
  ruby :: filegroups/scripts recall@3FP/M dropped 14.29pp (100.00% → 85.71%)

27 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + 7z: L3 hostile ensemble recall +14.84pp above LWM (72.74% → 87.59%)
  + c: L3 hostile ensemble recall +2.26pp above LWM (10.02% → 12.28%)
  + cab: L3 hostile ensemble recall +46.55pp above LWM (3.45% → 50.00%)
  + chrome-manifest: L3 hostile ensemble recall +16.67pp above LWM (50.00% → 66.67%)
  + crx: L3 hostile ensemble recall +10.81pp above LWM (0.00% → 10.81%)
  + docx: L3 hostile ensemble recall +1.09pp above LWM (71.59% → 72.68%)
  + go: L3 hostile ensemble recall +3.40pp above LWM (1.36% → 4.76%)
  + html: L3 hostile ensemble recall +83.33pp above LWM (16.67% → 100.00%)
  + javascript: L3 hostile ensemble recall +9.79pp above LWM (66.20% → 75.99%)
  + jpeg: L3 hostile ensemble recall +9.12pp above LWM (1.56% → 10.69%)
  + lnk: L3 hostile ensemble recall +22.72pp above LWM (48.66% → 71.38%)
  + package.json: L3 hostile ensemble recall +2.50pp above LWM (86.78% → 89.28%)
  + pe: L3 hostile ensemble recall +7.30pp above LWM (61.96% → 69.26%)
  + perl: L3 hostile ensemble recall +11.51pp above LWM (77.78% → 89.29%)
  + php: L3 hostile ensemble recall +3.93pp above LWM (62.11% → 66.04%)
  + plist: L3 hostile ensemble recall +1.47pp above LWM (2.94% → 4.41%)
  + png: L3 hostile ensemble recall +7.72pp above LWM (1.07% → 8.79%)
  + powershell: L3 hostile ensemble recall +1.94pp above LWM (29.62% → 31.55%)
  + ruby: L3 hostile ensemble recall +14.29pp above LWM (28.57% → 42.86%)
  + shell: L3 hostile ensemble recall +1.25pp above LWM (82.78% → 84.03%)
  + tar: L3 hostile ensemble recall +35.37pp above LWM (62.00% → 97.37%)
  + tar.gz: L3 hostile ensemble recall +12.57pp above LWM (56.69% → 69.27%)
  + xls: L3 hostile ensemble recall +2.72pp above LWM (92.44% → 95.16%)
  + xlsx: L3 hostile ensemble recall +4.47pp above LWM (29.01% → 33.48%)
  + xml: L3 hostile ensemble recall +6.06pp above LWM (2.74% → 8.79%)
  + zip: L3 hostile ensemble recall +11.38pp above LWM (40.61% → 51.99%)
  + zst: L3 hostile ensemble recall +1.98pp above LWM (76.60% → 78.58%)

2 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - batch: L3 hostile ENSEMBLE recall dropped 4.80pp BELOW LOW-WATER-MARK (98.83% → 94.04%; LWM tolerance 0.90pp)
  - python: L3 hostile ENSEMBLE recall dropped 2.41pp BELOW LOW-WATER-MARK (64.28% → 61.86%; LWM tolerance 0.90pp)

compared 64 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: low-water-mark gate (0.90pp vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[1]: *** [Makefile:1136: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')
