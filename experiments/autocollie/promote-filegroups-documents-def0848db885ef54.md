# Promote REJECTED — `def0848db885ef54` on `filegroups/documents`

Generated 2026-06-06T11:23:29Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-06T11-20-30_20260606T112030-promote-def0848db885ef54_azoth-validate.log; tail:   ~ pkg-info: pre-existing drift, recall 87.00% → 65.47% (+21.53pp; unimpacted by this promote)
  ~ png: pre-existing drift, recall 0.00% → 7.27% (+7.27pp; unimpacted by this promote)
  ~ powershell: pre-existing drift, recall 52.76% → 43.71% (+9.05pp; unimpacted by this promote)
  ~ python: pre-existing drift, recall 48.01% → 48.19% (+0.18pp; unimpacted by this promote)
  ~ python-bytecode: pre-existing drift, recall 92.09% → 88.14% (+3.95pp; unimpacted by this promote)
  ~ shell: pre-existing drift, recall 81.64% → 87.71% (+6.08pp; unimpacted by this promote)
  ~ tar: pre-existing drift, recall 88.19% → 81.54% (+6.65pp; unimpacted by this promote)
  ~ vbs: pre-existing drift, recall 42.72% → 47.69% (+4.97pp; unimpacted by this promote)
  ~ xml: pre-existing drift, recall 2.55% → 13.23% (+10.68pp; unimpacted by this promote)
  ~ zip: pre-existing drift, recall 31.45% → 31.98% (+0.53pp; unimpacted by this promote)

21 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + crx: L4 hostile ensemble recall +34.88pp above LWM (0.00% → 34.88%)
  + deb: L4 hostile ensemble recall +11.11pp above LWM (0.00% → 11.11%)
  + docx: L4 hostile ensemble recall +7.77pp above LWM (71.59% → 79.36%)
  + elf: L4 hostile ensemble recall +5.82pp above LWM (92.79% → 98.61%)
  + go: L4 hostile ensemble recall +4.11pp above LWM (1.78% → 5.90%)
  + html: L4 hostile ensemble recall +83.33pp above LWM (16.67% → 100.00%)
  + jar: L4 hostile ensemble recall +28.10pp above LWM (57.29% → 85.39%)
  + javascript: L4 hostile ensemble recall +5.10pp above LWM (66.20% → 71.30%)
  + jpeg: L4 hostile ensemble recall +11.68pp above LWM (1.56% → 13.25%)
  + lnk: L4 hostile ensemble recall +18.07pp above LWM (48.66% → 66.73%)
  + lua: L4 hostile ensemble recall +53.85pp above LWM (0.00% → 53.85%)
  + package.json: L4 hostile ensemble recall +2.44pp above LWM (86.78% → 89.22%)
  + perl: L4 hostile ensemble recall +5.56pp above LWM (77.78% → 83.33%)
  + png: L4 hostile ensemble recall +6.21pp above LWM (1.07% → 7.27%)
  + powershell: L4 hostile ensemble recall +14.10pp above LWM (29.62% → 43.71%)
  + ruby: L4 hostile ensemble recall +13.10pp above LWM (28.57% → 41.67%)
  + shell: L4 hostile ensemble recall +4.93pp above LWM (82.78% → 87.71%)
  + tar: L4 hostile ensemble recall +19.54pp above LWM (62.00% → 81.54%)
  + vbs: L4 hostile ensemble recall +21.99pp above LWM (25.70% → 47.69%)
  + xlsx: L4 hostile ensemble recall +1.50pp above LWM (29.01% → 30.51%)
  + xml: L4 hostile ensemble recall +10.49pp above LWM (2.74% → 13.23%)

3 DEPLOYED-TOLERANCE regression(s) (vs currently-deployed bundle /home/t/.local/share/litmus/models/azoth) — THIS IS WHAT BLOCKS THE DEPLOY:
  - docx: L4 hostile ENSEMBLE recall dropped 3.56pp (82.92% → 79.36%; tolerance 1.70pp; deployed 95% CI lower = 79.55%)
  - pdf: L4 hostile ENSEMBLE recall dropped 2.24pp (6.50% → 4.25%; tolerance 1.70pp; deployed 95% CI lower = 6.18%)
  - xlsx: L4 hostile ENSEMBLE recall dropped 5.57pp (36.08% → 30.51%; tolerance 1.70pp; deployed 95% CI lower = 34.98%)

2 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - ole: L4 hostile ENSEMBLE recall dropped 9.95pp BELOW LOW-WATER-MARK (91.27% → 81.31%; LWM tolerance 0.90pp)
  - pdf: L4 hostile ENSEMBLE recall dropped 2.16pp BELOW LOW-WATER-MARK (6.41% → 4.25%; LWM tolerance 0.90pp)

compared 75 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: deployed-tolerance gate (3 filetype(s) regressed vs deployed beyond the 1.70pp tolerance; see list above for the actual drops), low-water-mark gate (2 filetype(s) below LWM beyond the 0.90pp tolerance vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[1]: *** [Makefile:1291: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 1.0000)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `def0848db885ef54` | `48e711ddf647f0d6` | `9f4de35a7507e755` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9995 | 0.9991 | 0.9991 |
| F1 | 0.9899 | 0.9975 | 0.9974 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-06T11-20-30_20260606T112030-promote-def0848db885ef54_azoth-validate.log; tail:   ~ pkg-info: pre-existing drift, recall 87.00% → 65.47% (+21.53pp; unimpacted by this promote)
  ~ png: pre-existing drift, recall 0.00% → 7.27% (+7.27pp; unimpacted by this promote)
  ~ powershell: pre-existing drift, recall 52.76% → 43.71% (+9.05pp; unimpacted by this promote)
  ~ python: pre-existing drift, recall 48.01% → 48.19% (+0.18pp; unimpacted by this promote)
  ~ python-bytecode: pre-existing drift, recall 92.09% → 88.14% (+3.95pp; unimpacted by this promote)
  ~ shell: pre-existing drift, recall 81.64% → 87.71% (+6.08pp; unimpacted by this promote)
  ~ tar: pre-existing drift, recall 88.19% → 81.54% (+6.65pp; unimpacted by this promote)
  ~ vbs: pre-existing drift, recall 42.72% → 47.69% (+4.97pp; unimpacted by this promote)
  ~ xml: pre-existing drift, recall 2.55% → 13.23% (+10.68pp; unimpacted by this promote)
  ~ zip: pre-existing drift, recall 31.45% → 31.98% (+0.53pp; unimpacted by this promote)

21 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + crx: L4 hostile ensemble recall +34.88pp above LWM (0.00% → 34.88%)
  + deb: L4 hostile ensemble recall +11.11pp above LWM (0.00% → 11.11%)
  + docx: L4 hostile ensemble recall +7.77pp above LWM (71.59% → 79.36%)
  + elf: L4 hostile ensemble recall +5.82pp above LWM (92.79% → 98.61%)
  + go: L4 hostile ensemble recall +4.11pp above LWM (1.78% → 5.90%)
  + html: L4 hostile ensemble recall +83.33pp above LWM (16.67% → 100.00%)
  + jar: L4 hostile ensemble recall +28.10pp above LWM (57.29% → 85.39%)
  + javascript: L4 hostile ensemble recall +5.10pp above LWM (66.20% → 71.30%)
  + jpeg: L4 hostile ensemble recall +11.68pp above LWM (1.56% → 13.25%)
  + lnk: L4 hostile ensemble recall +18.07pp above LWM (48.66% → 66.73%)
  + lua: L4 hostile ensemble recall +53.85pp above LWM (0.00% → 53.85%)
  + package.json: L4 hostile ensemble recall +2.44pp above LWM (86.78% → 89.22%)
  + perl: L4 hostile ensemble recall +5.56pp above LWM (77.78% → 83.33%)
  + png: L4 hostile ensemble recall +6.21pp above LWM (1.07% → 7.27%)
  + powershell: L4 hostile ensemble recall +14.10pp above LWM (29.62% → 43.71%)
  + ruby: L4 hostile ensemble recall +13.10pp above LWM (28.57% → 41.67%)
  + shell: L4 hostile ensemble recall +4.93pp above LWM (82.78% → 87.71%)
  + tar: L4 hostile ensemble recall +19.54pp above LWM (62.00% → 81.54%)
  + vbs: L4 hostile ensemble recall +21.99pp above LWM (25.70% → 47.69%)
  + xlsx: L4 hostile ensemble recall +1.50pp above LWM (29.01% → 30.51%)
  + xml: L4 hostile ensemble recall +10.49pp above LWM (2.74% → 13.23%)

3 DEPLOYED-TOLERANCE regression(s) (vs currently-deployed bundle /home/t/.local/share/litmus/models/azoth) — THIS IS WHAT BLOCKS THE DEPLOY:
  - docx: L4 hostile ENSEMBLE recall dropped 3.56pp (82.92% → 79.36%; tolerance 1.70pp; deployed 95% CI lower = 79.55%)
  - pdf: L4 hostile ENSEMBLE recall dropped 2.24pp (6.50% → 4.25%; tolerance 1.70pp; deployed 95% CI lower = 6.18%)
  - xlsx: L4 hostile ENSEMBLE recall dropped 5.57pp (36.08% → 30.51%; tolerance 1.70pp; deployed 95% CI lower = 34.98%)

2 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - ole: L4 hostile ENSEMBLE recall dropped 9.95pp BELOW LOW-WATER-MARK (91.27% → 81.31%; LWM tolerance 0.90pp)
  - pdf: L4 hostile ENSEMBLE recall dropped 2.16pp BELOW LOW-WATER-MARK (6.41% → 4.25%; LWM tolerance 0.90pp)

compared 75 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: deployed-tolerance gate (3 filetype(s) regressed vs deployed beyond the 1.70pp tolerance; see list above for the actual drops), low-water-mark gate (2 filetype(s) below LWM beyond the 0.90pp tolerance vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[1]: *** [Makefile:1291: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')
