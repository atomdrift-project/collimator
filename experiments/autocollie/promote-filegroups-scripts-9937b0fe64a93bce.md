# Promote REJECTED — `9937b0fe64a93bce` on `filegroups/scripts`

Generated 2026-06-06T08:00:50Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-06T07-57-40_20260606T075739-promote-9937b0fe64a93bce_azoth-validate.log; tail:   ~ pdf: pre-existing drift, recall 6.50% → 4.25% (+2.25pp; unimpacted by this promote)
  ~ pe: pre-existing drift, recall 51.78% → 56.91% (+5.12pp; unimpacted by this promote)
  ~ pkg-info: pre-existing drift, recall 87.00% → 65.47% (+21.53pp; unimpacted by this promote)
  ~ png: pre-existing drift, recall 0.00% → 7.27% (+7.27pp; unimpacted by this promote)
  ~ pptx: pre-existing drift, recall 22.22% → 1.39% (+20.83pp; unimpacted by this promote)
  ~ python-bytecode: pre-existing drift, recall 92.09% → 88.14% (+3.95pp; unimpacted by this promote)
  ~ tar: pre-existing drift, recall 88.19% → 81.54% (+6.65pp; unimpacted by this promote)
  ~ vbs: pre-existing drift, recall 42.72% → 48.04% (+5.32pp; unimpacted by this promote)
  ~ xls: pre-existing drift, recall 93.19% → 90.97% (+2.22pp; unimpacted by this promote)
  ~ xlsx: pre-existing drift, recall 36.08% → 29.09% (+6.99pp; unimpacted by this promote)
  ~ xml: pre-existing drift, recall 2.55% → 13.23% (+10.68pp; unimpacted by this promote)
  ~ zip: pre-existing drift, recall 31.45% → 31.98% (+0.53pp; unimpacted by this promote)

17 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + crx: L4 hostile ensemble recall +34.88pp above LWM (0.00% → 34.88%)
  + deb: L4 hostile ensemble recall +11.11pp above LWM (0.00% → 11.11%)
  + elf: L4 hostile ensemble recall +5.82pp above LWM (92.79% → 98.61%)
  + go: L4 hostile ensemble recall +4.11pp above LWM (1.78% → 5.90%)
  + html: L4 hostile ensemble recall +83.33pp above LWM (16.67% → 100.00%)
  + jar: L4 hostile ensemble recall +28.10pp above LWM (57.29% → 85.39%)
  + jpeg: L4 hostile ensemble recall +11.68pp above LWM (1.56% → 13.25%)
  + lnk: L4 hostile ensemble recall +18.07pp above LWM (48.66% → 66.73%)
  + lua: L4 hostile ensemble recall +61.54pp above LWM (0.00% → 61.54%)
  + package.json: L4 hostile ensemble recall +2.44pp above LWM (86.78% → 89.22%)
  + png: L4 hostile ensemble recall +6.21pp above LWM (1.07% → 7.27%)
  + powershell: L4 hostile ensemble recall +25.89pp above LWM (29.62% → 55.50%)
  + ruby: L4 hostile ensemble recall +38.10pp above LWM (28.57% → 66.67%)
  + shell: L4 hostile ensemble recall +5.25pp above LWM (82.78% → 88.03%)
  + tar: L4 hostile ensemble recall +19.54pp above LWM (62.00% → 81.54%)
  + vbs: L4 hostile ensemble recall +22.34pp above LWM (25.70% → 48.04%)
  + xml: L4 hostile ensemble recall +10.49pp above LWM (2.74% → 13.23%)

2 DEPLOYED-TOLERANCE regression(s) (vs currently-deployed bundle /home/t/.local/share/litmus/models/azoth) — THIS IS WHAT BLOCKS THE DEPLOY:
  - batch: L4 hostile ENSEMBLE recall dropped 95.34pp (97.46% → 2.12%; tolerance 1.70pp; deployed 95% CI lower = 97.25%)
  - python: L4 hostile ENSEMBLE recall dropped 2.08pp (48.01% → 45.93%; tolerance 1.70pp; deployed 95% CI lower = 45.98%)

5 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - batch: L4 hostile ENSEMBLE recall dropped 96.71pp BELOW LOW-WATER-MARK (98.83% → 2.12%; LWM tolerance 0.90pp)
  - javascript: L4 hostile ENSEMBLE recall dropped 4.08pp BELOW LOW-WATER-MARK (66.20% → 62.12%; LWM tolerance 0.90pp)
  - perl: L4 hostile ENSEMBLE recall dropped 5.56pp BELOW LOW-WATER-MARK (77.78% → 72.22%; LWM tolerance 0.90pp)
  - php: L4 hostile ENSEMBLE recall dropped 14.53pp BELOW LOW-WATER-MARK (64.84% → 50.31%; LWM tolerance 0.90pp)
  - python: L4 hostile ENSEMBLE recall dropped 18.35pp BELOW LOW-WATER-MARK (64.28% → 45.93%; LWM tolerance 0.90pp)

compared 75 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: deployed-tolerance gate (2 filetype(s) regressed vs deployed beyond the 1.70pp tolerance; see list above for the actual drops), low-water-mark gate (5 filetype(s) below LWM beyond the 0.90pp tolerance vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[1]: *** [Makefile:1291: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9970)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `9937b0fe64a93bce` | `d1d79b588536aa2b` | `6b88271fc4e09acf` |
| PR AUC | 0.9970 | 0.9989 | 0.9989 |
| ROC AUC | 0.9964 | 0.9986 | 0.9986 |
| F1 | 0.9737 | 0.9859 | 0.9864 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-06T07-57-40_20260606T075739-promote-9937b0fe64a93bce_azoth-validate.log; tail:   ~ pdf: pre-existing drift, recall 6.50% → 4.25% (+2.25pp; unimpacted by this promote)
  ~ pe: pre-existing drift, recall 51.78% → 56.91% (+5.12pp; unimpacted by this promote)
  ~ pkg-info: pre-existing drift, recall 87.00% → 65.47% (+21.53pp; unimpacted by this promote)
  ~ png: pre-existing drift, recall 0.00% → 7.27% (+7.27pp; unimpacted by this promote)
  ~ pptx: pre-existing drift, recall 22.22% → 1.39% (+20.83pp; unimpacted by this promote)
  ~ python-bytecode: pre-existing drift, recall 92.09% → 88.14% (+3.95pp; unimpacted by this promote)
  ~ tar: pre-existing drift, recall 88.19% → 81.54% (+6.65pp; unimpacted by this promote)
  ~ vbs: pre-existing drift, recall 42.72% → 48.04% (+5.32pp; unimpacted by this promote)
  ~ xls: pre-existing drift, recall 93.19% → 90.97% (+2.22pp; unimpacted by this promote)
  ~ xlsx: pre-existing drift, recall 36.08% → 29.09% (+6.99pp; unimpacted by this promote)
  ~ xml: pre-existing drift, recall 2.55% → 13.23% (+10.68pp; unimpacted by this promote)
  ~ zip: pre-existing drift, recall 31.45% → 31.98% (+0.53pp; unimpacted by this promote)

17 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + crx: L4 hostile ensemble recall +34.88pp above LWM (0.00% → 34.88%)
  + deb: L4 hostile ensemble recall +11.11pp above LWM (0.00% → 11.11%)
  + elf: L4 hostile ensemble recall +5.82pp above LWM (92.79% → 98.61%)
  + go: L4 hostile ensemble recall +4.11pp above LWM (1.78% → 5.90%)
  + html: L4 hostile ensemble recall +83.33pp above LWM (16.67% → 100.00%)
  + jar: L4 hostile ensemble recall +28.10pp above LWM (57.29% → 85.39%)
  + jpeg: L4 hostile ensemble recall +11.68pp above LWM (1.56% → 13.25%)
  + lnk: L4 hostile ensemble recall +18.07pp above LWM (48.66% → 66.73%)
  + lua: L4 hostile ensemble recall +61.54pp above LWM (0.00% → 61.54%)
  + package.json: L4 hostile ensemble recall +2.44pp above LWM (86.78% → 89.22%)
  + png: L4 hostile ensemble recall +6.21pp above LWM (1.07% → 7.27%)
  + powershell: L4 hostile ensemble recall +25.89pp above LWM (29.62% → 55.50%)
  + ruby: L4 hostile ensemble recall +38.10pp above LWM (28.57% → 66.67%)
  + shell: L4 hostile ensemble recall +5.25pp above LWM (82.78% → 88.03%)
  + tar: L4 hostile ensemble recall +19.54pp above LWM (62.00% → 81.54%)
  + vbs: L4 hostile ensemble recall +22.34pp above LWM (25.70% → 48.04%)
  + xml: L4 hostile ensemble recall +10.49pp above LWM (2.74% → 13.23%)

2 DEPLOYED-TOLERANCE regression(s) (vs currently-deployed bundle /home/t/.local/share/litmus/models/azoth) — THIS IS WHAT BLOCKS THE DEPLOY:
  - batch: L4 hostile ENSEMBLE recall dropped 95.34pp (97.46% → 2.12%; tolerance 1.70pp; deployed 95% CI lower = 97.25%)
  - python: L4 hostile ENSEMBLE recall dropped 2.08pp (48.01% → 45.93%; tolerance 1.70pp; deployed 95% CI lower = 45.98%)

5 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - batch: L4 hostile ENSEMBLE recall dropped 96.71pp BELOW LOW-WATER-MARK (98.83% → 2.12%; LWM tolerance 0.90pp)
  - javascript: L4 hostile ENSEMBLE recall dropped 4.08pp BELOW LOW-WATER-MARK (66.20% → 62.12%; LWM tolerance 0.90pp)
  - perl: L4 hostile ENSEMBLE recall dropped 5.56pp BELOW LOW-WATER-MARK (77.78% → 72.22%; LWM tolerance 0.90pp)
  - php: L4 hostile ENSEMBLE recall dropped 14.53pp BELOW LOW-WATER-MARK (64.84% → 50.31%; LWM tolerance 0.90pp)
  - python: L4 hostile ENSEMBLE recall dropped 18.35pp BELOW LOW-WATER-MARK (64.28% → 45.93%; LWM tolerance 0.90pp)

compared 75 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: deployed-tolerance gate (2 filetype(s) regressed vs deployed beyond the 1.70pp tolerance; see list above for the actual drops), low-water-mark gate (5 filetype(s) below LWM beyond the 0.90pp tolerance vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[1]: *** [Makefile:1291: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')
