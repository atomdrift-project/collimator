# Promote REJECTED — `a4cd85ee0477c434` on `general`

Generated 2026-05-28T02:22:24Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-28T02-17-08_20260528T020322-promote-a4cd85ee0477c434_azoth-validate.log; tail: 
per-route improvements (≥0.10pp, informational):
  c :: filetypes/c recall@3FP/M +4.70pp (11.94% → 16.64%)

22 low-water-mark improvement(s) (>0.90pp above LWM, informational):
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
  + tar: L3 hostile ensemble recall +35.37pp above LWM (62.00% → 97.37%)
  + tar.gz: L3 hostile ensemble recall +12.57pp above LWM (56.69% → 69.27%)
  + xls: L3 hostile ensemble recall +2.72pp above LWM (92.44% → 95.16%)
  + xlsx: L3 hostile ensemble recall +4.47pp above LWM (29.01% → 33.48%)
  + xml: L3 hostile ensemble recall +6.06pp above LWM (2.74% → 8.79%)
  + zip: L3 hostile ensemble recall +11.38pp above LWM (40.61% → 51.99%)
  + zst: L3 hostile ensemble recall +1.98pp above LWM (76.60% → 78.58%)

13 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - batch: L3 hostile ENSEMBLE recall dropped 4.80pp BELOW LOW-WATER-MARK (98.83% → 94.04%; LWM tolerance 0.90pp)
  - doc: L3 hostile ENSEMBLE recall dropped 18.73pp BELOW LOW-WATER-MARK (90.99% → 72.26%; LWM tolerance 0.90pp)
  - jar: L3 hostile ENSEMBLE recall dropped 2.66pp BELOW LOW-WATER-MARK (57.29% → 54.63%; LWM tolerance 0.90pp)
  - javascript: L3 hostile ENSEMBLE recall dropped 2.89pp BELOW LOW-WATER-MARK (66.20% → 63.31%; LWM tolerance 0.90pp)
  - kotlin: L3 hostile ENSEMBLE recall dropped 1.14pp BELOW LOW-WATER-MARK (52.67% → 51.53%; LWM tolerance 0.90pp)
  - macho: L3 hostile ENSEMBLE recall dropped 13.65pp BELOW LOW-WATER-MARK (86.64% → 72.99%; LWM tolerance 0.90pp)
  - msi: L3 hostile ENSEMBLE recall dropped 35.82pp BELOW LOW-WATER-MARK (76.17% → 40.35%; LWM tolerance 0.90pp)
  - powershell: L3 hostile ENSEMBLE recall dropped 4.48pp BELOW LOW-WATER-MARK (29.62% → 25.13%; LWM tolerance 0.90pp)
  - pptx: L3 hostile ENSEMBLE recall dropped 4.55pp BELOW LOW-WATER-MARK (9.09% → 4.55%; LWM tolerance 0.90pp)
  - python: L3 hostile ENSEMBLE recall dropped 5.03pp BELOW LOW-WATER-MARK (64.28% → 59.25%; LWM tolerance 0.90pp)
  - python-bytecode: L3 hostile ENSEMBLE recall dropped 5.27pp BELOW LOW-WATER-MARK (90.99% → 85.71%; LWM tolerance 0.90pp)
  - shell: L3 hostile ENSEMBLE recall dropped 13.06pp BELOW LOW-WATER-MARK (82.78% → 69.73%; LWM tolerance 0.90pp)
  - vbs: L3 hostile ENSEMBLE recall dropped 8.04pp BELOW LOW-WATER-MARK (25.70% → 17.66%; LWM tolerance 0.90pp)

compared 64 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: low-water-mark gate (0.90pp vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[1]: *** [Makefile:1136: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9986)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `a4cd85ee0477c434` | `7d2b23f980972c43` | `478a5d699d7a837f` |
| PR AUC | 0.9986 | 0.9998 | 0.9996 |
| ROC AUC | 0.9987 | 0.9996 | 0.9996 |
| F1 | 0.9826 | 0.9940 | 0.9897 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-28T02-17-08_20260528T020322-promote-a4cd85ee0477c434_azoth-validate.log; tail: 
per-route improvements (≥0.10pp, informational):
  c :: filetypes/c recall@3FP/M +4.70pp (11.94% → 16.64%)

22 low-water-mark improvement(s) (>0.90pp above LWM, informational):
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
  + tar: L3 hostile ensemble recall +35.37pp above LWM (62.00% → 97.37%)
  + tar.gz: L3 hostile ensemble recall +12.57pp above LWM (56.69% → 69.27%)
  + xls: L3 hostile ensemble recall +2.72pp above LWM (92.44% → 95.16%)
  + xlsx: L3 hostile ensemble recall +4.47pp above LWM (29.01% → 33.48%)
  + xml: L3 hostile ensemble recall +6.06pp above LWM (2.74% → 8.79%)
  + zip: L3 hostile ensemble recall +11.38pp above LWM (40.61% → 51.99%)
  + zst: L3 hostile ensemble recall +1.98pp above LWM (76.60% → 78.58%)

13 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - batch: L3 hostile ENSEMBLE recall dropped 4.80pp BELOW LOW-WATER-MARK (98.83% → 94.04%; LWM tolerance 0.90pp)
  - doc: L3 hostile ENSEMBLE recall dropped 18.73pp BELOW LOW-WATER-MARK (90.99% → 72.26%; LWM tolerance 0.90pp)
  - jar: L3 hostile ENSEMBLE recall dropped 2.66pp BELOW LOW-WATER-MARK (57.29% → 54.63%; LWM tolerance 0.90pp)
  - javascript: L3 hostile ENSEMBLE recall dropped 2.89pp BELOW LOW-WATER-MARK (66.20% → 63.31%; LWM tolerance 0.90pp)
  - kotlin: L3 hostile ENSEMBLE recall dropped 1.14pp BELOW LOW-WATER-MARK (52.67% → 51.53%; LWM tolerance 0.90pp)
  - macho: L3 hostile ENSEMBLE recall dropped 13.65pp BELOW LOW-WATER-MARK (86.64% → 72.99%; LWM tolerance 0.90pp)
  - msi: L3 hostile ENSEMBLE recall dropped 35.82pp BELOW LOW-WATER-MARK (76.17% → 40.35%; LWM tolerance 0.90pp)
  - powershell: L3 hostile ENSEMBLE recall dropped 4.48pp BELOW LOW-WATER-MARK (29.62% → 25.13%; LWM tolerance 0.90pp)
  - pptx: L3 hostile ENSEMBLE recall dropped 4.55pp BELOW LOW-WATER-MARK (9.09% → 4.55%; LWM tolerance 0.90pp)
  - python: L3 hostile ENSEMBLE recall dropped 5.03pp BELOW LOW-WATER-MARK (64.28% → 59.25%; LWM tolerance 0.90pp)
  - python-bytecode: L3 hostile ENSEMBLE recall dropped 5.27pp BELOW LOW-WATER-MARK (90.99% → 85.71%; LWM tolerance 0.90pp)
  - shell: L3 hostile ENSEMBLE recall dropped 13.06pp BELOW LOW-WATER-MARK (82.78% → 69.73%; LWM tolerance 0.90pp)
  - vbs: L3 hostile ENSEMBLE recall dropped 8.04pp BELOW LOW-WATER-MARK (25.70% → 17.66%; LWM tolerance 0.90pp)

compared 64 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: low-water-mark gate (0.90pp vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[1]: *** [Makefile:1136: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')
