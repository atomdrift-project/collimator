# Promote REJECTED — `1892b3a81a651262` on `general`

Generated 2026-06-06T09:22:43Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-06T09-18-19_20260606T091818-promote-1892b3a81a651262_azoth-validate.log; tail:   + powershell: L4 hostile ensemble recall +26.99pp above LWM (29.62% → 56.60%)
  + ruby: L4 hostile ensemble recall +38.10pp above LWM (28.57% → 66.67%)
  + shell: L4 hostile ensemble recall +4.93pp above LWM (82.78% → 87.71%)
  + tar: L4 hostile ensemble recall +24.97pp above LWM (62.00% → 86.97%)
  + vbs: L4 hostile ensemble recall +22.34pp above LWM (25.70% → 48.04%)
  + xlsx: L4 hostile ensemble recall +1.59pp above LWM (29.01% → 30.61%)
  + xml: L4 hostile ensemble recall +10.75pp above LWM (2.74% → 13.49%)

8 DEPLOYED-TOLERANCE regression(s) (vs currently-deployed bundle /home/t/.local/share/litmus/models/azoth) — THIS IS WHAT BLOCKS THE DEPLOY:
  - batch: L4 hostile ENSEMBLE recall dropped 96.17pp (97.46% → 1.29%; tolerance 1.70pp; deployed 95% CI lower = 97.25%)
  - docx: L4 hostile ENSEMBLE recall dropped 4.09pp (82.92% → 78.83%; tolerance 1.70pp; deployed 95% CI lower = 79.55%)
  - elf: L4 hostile ENSEMBLE recall dropped 2.46pp (95.93% → 93.47%; tolerance 1.70pp; deployed 95% CI lower = 95.66%)
  - jar: L4 hostile ENSEMBLE recall dropped 15.15pp (70.65% → 55.51%; tolerance 1.70pp; deployed 95% CI lower = 66.17%)
  - javascript: L4 hostile ENSEMBLE recall dropped 8.19pp (59.50% → 51.31%; tolerance 1.70pp; deployed 95% CI lower = 58.69%)
  - lnk: L4 hostile ENSEMBLE recall dropped 12.05pp (82.68% → 70.63%; tolerance 1.70pp; deployed 95% CI lower = 79.21%)
  - python-bytecode: L4 hostile ENSEMBLE recall dropped 5.65pp (92.09% → 86.44%; tolerance 1.70pp; deployed 95% CI lower = 88.77%)
  - xlsx: L4 hostile ENSEMBLE recall dropped 5.47pp (36.08% → 30.61%; tolerance 1.70pp; deployed 95% CI lower = 34.98%)

23 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - 7z: L4 hostile ENSEMBLE recall dropped 56.76pp BELOW LOW-WATER-MARK (72.74% → 15.98%; LWM tolerance 0.90pp)
  - batch: L4 hostile ENSEMBLE recall dropped 97.54pp BELOW LOW-WATER-MARK (98.83% → 1.29%; LWM tolerance 0.90pp)
  - c: L4 hostile ENSEMBLE recall dropped 3.33pp BELOW LOW-WATER-MARK (10.31% → 6.97%; LWM tolerance 0.90pp)
  - cab: L4 hostile ENSEMBLE recall dropped 3.45pp BELOW LOW-WATER-MARK (3.45% → 0.00%; LWM tolerance 0.90pp)
  - chrome-manifest: L4 hostile ENSEMBLE recall dropped 7.14pp BELOW LOW-WATER-MARK (50.00% → 42.86%; LWM tolerance 0.90pp)
  - gz: L4 hostile ENSEMBLE recall dropped 28.32pp BELOW LOW-WATER-MARK (28.32% → 0.00%; LWM tolerance 0.90pp)
  - jar: L4 hostile ENSEMBLE recall dropped 1.79pp BELOW LOW-WATER-MARK (57.29% → 55.51%; LWM tolerance 0.90pp)
  - java: L4 hostile ENSEMBLE recall dropped 20.00pp BELOW LOW-WATER-MARK (50.00% → 30.00%; LWM tolerance 0.90pp)
  - java_class: L4 hostile ENSEMBLE recall dropped 34.04pp BELOW LOW-WATER-MARK (73.41% → 39.37%; LWM tolerance 0.90pp)
  - javascript: L4 hostile ENSEMBLE recall dropped 14.89pp BELOW LOW-WATER-MARK (66.20% → 51.31%; LWM tolerance 0.90pp)
  - macho: L4 hostile ENSEMBLE recall dropped 10.29pp BELOW LOW-WATER-MARK (86.64% → 76.35%; LWM tolerance 0.90pp)
  - msi: L4 hostile ENSEMBLE recall dropped 10.17pp BELOW LOW-WATER-MARK (76.17% → 66.00%; LWM tolerance 0.90pp)
  - ole: L4 hostile ENSEMBLE recall dropped 9.70pp BELOW LOW-WATER-MARK (91.27% → 81.57%; LWM tolerance 0.90pp)
  - pe: L4 hostile ENSEMBLE recall dropped 9.47pp BELOW LOW-WATER-MARK (61.96% → 52.49%; LWM tolerance 0.90pp)
  - perl: L4 hostile ENSEMBLE recall dropped 5.56pp BELOW LOW-WATER-MARK (77.78% → 72.22%; LWM tolerance 0.90pp)
  - php: L4 hostile ENSEMBLE recall dropped 15.31pp BELOW LOW-WATER-MARK (64.84% → 49.53%; LWM tolerance 0.90pp)
  - pkg-info: L4 hostile ENSEMBLE recall dropped 1.33pp BELOW LOW-WATER-MARK (97.02% → 95.69%; LWM tolerance 0.90pp)
  - python: L4 hostile ENSEMBLE recall dropped 16.09pp BELOW LOW-WATER-MARK (64.28% → 48.19%; LWM tolerance 0.90pp)
  - python-bytecode: L4 hostile ENSEMBLE recall dropped 4.55pp BELOW LOW-WATER-MARK (90.99% → 86.44%; LWM tolerance 0.90pp)
  - text: L4 hostile ENSEMBLE recall dropped 2.84pp BELOW LOW-WATER-MARK (11.25% → 8.41%; LWM tolerance 0.90pp)
  - xz: L4 hostile ENSEMBLE recall dropped 25.00pp BELOW LOW-WATER-MARK (25.00% → 0.00%; LWM tolerance 0.90pp)
  - zip: L4 hostile ENSEMBLE recall dropped 5.28pp BELOW LOW-WATER-MARK (40.61% → 35.33%; LWM tolerance 0.90pp)
  - zst: L4 hostile ENSEMBLE recall dropped 64.75pp BELOW LOW-WATER-MARK (76.60% → 11.85%; LWM tolerance 0.90pp)

compared 75 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: deployed-tolerance gate (8 filetype(s) regressed vs deployed beyond the 1.70pp tolerance; see list above for the actual drops), low-water-mark gate (23 filetype(s) below LWM beyond the 0.90pp tolerance vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[1]: *** [Makefile:1291: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9984)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `1892b3a81a651262` | `475fe486ea57c6dc` | `e5b0a2ffa08fb554` |
| PR AUC | 0.9984 | 0.9999 | 0.9996 |
| ROC AUC | 0.9983 | 0.9995 | 0.9995 |
| F1 | 0.9840 | 0.9955 | 0.9918 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-06T09-18-19_20260606T091818-promote-1892b3a81a651262_azoth-validate.log; tail:   + powershell: L4 hostile ensemble recall +26.99pp above LWM (29.62% → 56.60%)
  + ruby: L4 hostile ensemble recall +38.10pp above LWM (28.57% → 66.67%)
  + shell: L4 hostile ensemble recall +4.93pp above LWM (82.78% → 87.71%)
  + tar: L4 hostile ensemble recall +24.97pp above LWM (62.00% → 86.97%)
  + vbs: L4 hostile ensemble recall +22.34pp above LWM (25.70% → 48.04%)
  + xlsx: L4 hostile ensemble recall +1.59pp above LWM (29.01% → 30.61%)
  + xml: L4 hostile ensemble recall +10.75pp above LWM (2.74% → 13.49%)

8 DEPLOYED-TOLERANCE regression(s) (vs currently-deployed bundle /home/t/.local/share/litmus/models/azoth) — THIS IS WHAT BLOCKS THE DEPLOY:
  - batch: L4 hostile ENSEMBLE recall dropped 96.17pp (97.46% → 1.29%; tolerance 1.70pp; deployed 95% CI lower = 97.25%)
  - docx: L4 hostile ENSEMBLE recall dropped 4.09pp (82.92% → 78.83%; tolerance 1.70pp; deployed 95% CI lower = 79.55%)
  - elf: L4 hostile ENSEMBLE recall dropped 2.46pp (95.93% → 93.47%; tolerance 1.70pp; deployed 95% CI lower = 95.66%)
  - jar: L4 hostile ENSEMBLE recall dropped 15.15pp (70.65% → 55.51%; tolerance 1.70pp; deployed 95% CI lower = 66.17%)
  - javascript: L4 hostile ENSEMBLE recall dropped 8.19pp (59.50% → 51.31%; tolerance 1.70pp; deployed 95% CI lower = 58.69%)
  - lnk: L4 hostile ENSEMBLE recall dropped 12.05pp (82.68% → 70.63%; tolerance 1.70pp; deployed 95% CI lower = 79.21%)
  - python-bytecode: L4 hostile ENSEMBLE recall dropped 5.65pp (92.09% → 86.44%; tolerance 1.70pp; deployed 95% CI lower = 88.77%)
  - xlsx: L4 hostile ENSEMBLE recall dropped 5.47pp (36.08% → 30.61%; tolerance 1.70pp; deployed 95% CI lower = 34.98%)

23 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - 7z: L4 hostile ENSEMBLE recall dropped 56.76pp BELOW LOW-WATER-MARK (72.74% → 15.98%; LWM tolerance 0.90pp)
  - batch: L4 hostile ENSEMBLE recall dropped 97.54pp BELOW LOW-WATER-MARK (98.83% → 1.29%; LWM tolerance 0.90pp)
  - c: L4 hostile ENSEMBLE recall dropped 3.33pp BELOW LOW-WATER-MARK (10.31% → 6.97%; LWM tolerance 0.90pp)
  - cab: L4 hostile ENSEMBLE recall dropped 3.45pp BELOW LOW-WATER-MARK (3.45% → 0.00%; LWM tolerance 0.90pp)
  - chrome-manifest: L4 hostile ENSEMBLE recall dropped 7.14pp BELOW LOW-WATER-MARK (50.00% → 42.86%; LWM tolerance 0.90pp)
  - gz: L4 hostile ENSEMBLE recall dropped 28.32pp BELOW LOW-WATER-MARK (28.32% → 0.00%; LWM tolerance 0.90pp)
  - jar: L4 hostile ENSEMBLE recall dropped 1.79pp BELOW LOW-WATER-MARK (57.29% → 55.51%; LWM tolerance 0.90pp)
  - java: L4 hostile ENSEMBLE recall dropped 20.00pp BELOW LOW-WATER-MARK (50.00% → 30.00%; LWM tolerance 0.90pp)
  - java_class: L4 hostile ENSEMBLE recall dropped 34.04pp BELOW LOW-WATER-MARK (73.41% → 39.37%; LWM tolerance 0.90pp)
  - javascript: L4 hostile ENSEMBLE recall dropped 14.89pp BELOW LOW-WATER-MARK (66.20% → 51.31%; LWM tolerance 0.90pp)
  - macho: L4 hostile ENSEMBLE recall dropped 10.29pp BELOW LOW-WATER-MARK (86.64% → 76.35%; LWM tolerance 0.90pp)
  - msi: L4 hostile ENSEMBLE recall dropped 10.17pp BELOW LOW-WATER-MARK (76.17% → 66.00%; LWM tolerance 0.90pp)
  - ole: L4 hostile ENSEMBLE recall dropped 9.70pp BELOW LOW-WATER-MARK (91.27% → 81.57%; LWM tolerance 0.90pp)
  - pe: L4 hostile ENSEMBLE recall dropped 9.47pp BELOW LOW-WATER-MARK (61.96% → 52.49%; LWM tolerance 0.90pp)
  - perl: L4 hostile ENSEMBLE recall dropped 5.56pp BELOW LOW-WATER-MARK (77.78% → 72.22%; LWM tolerance 0.90pp)
  - php: L4 hostile ENSEMBLE recall dropped 15.31pp BELOW LOW-WATER-MARK (64.84% → 49.53%; LWM tolerance 0.90pp)
  - pkg-info: L4 hostile ENSEMBLE recall dropped 1.33pp BELOW LOW-WATER-MARK (97.02% → 95.69%; LWM tolerance 0.90pp)
  - python: L4 hostile ENSEMBLE recall dropped 16.09pp BELOW LOW-WATER-MARK (64.28% → 48.19%; LWM tolerance 0.90pp)
  - python-bytecode: L4 hostile ENSEMBLE recall dropped 4.55pp BELOW LOW-WATER-MARK (90.99% → 86.44%; LWM tolerance 0.90pp)
  - text: L4 hostile ENSEMBLE recall dropped 2.84pp BELOW LOW-WATER-MARK (11.25% → 8.41%; LWM tolerance 0.90pp)
  - xz: L4 hostile ENSEMBLE recall dropped 25.00pp BELOW LOW-WATER-MARK (25.00% → 0.00%; LWM tolerance 0.90pp)
  - zip: L4 hostile ENSEMBLE recall dropped 5.28pp BELOW LOW-WATER-MARK (40.61% → 35.33%; LWM tolerance 0.90pp)
  - zst: L4 hostile ENSEMBLE recall dropped 64.75pp BELOW LOW-WATER-MARK (76.60% → 11.85%; LWM tolerance 0.90pp)

compared 75 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: deployed-tolerance gate (8 filetype(s) regressed vs deployed beyond the 1.70pp tolerance; see list above for the actual drops), low-water-mark gate (23 filetype(s) below LWM beyond the 0.90pp tolerance vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[1]: *** [Makefile:1291: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')
