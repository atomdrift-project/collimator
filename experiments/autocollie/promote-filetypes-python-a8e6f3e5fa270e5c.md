# Promote REJECTED — `a8e6f3e5fa270e5c` on `filetypes/python`

Generated 2026-06-06T09:28:57Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-06T09-26-05_20260606T092604-promote-a8e6f3e5fa270e5c_azoth-validate.log; tail:   ~ macho: pre-existing drift, recall 80.24% → 68.26% (+11.98pp; unimpacted by this promote)
  ~ msi: pre-existing drift, recall 0.00% → 58.05% (+58.05pp; unimpacted by this promote)
  ~ ole: pre-existing drift, recall 82.17% → 50.88% (+31.29pp; unimpacted by this promote)
  ~ pdf: pre-existing drift, recall 6.50% → 4.25% (+2.25pp; unimpacted by this promote)
  ~ pe: pre-existing drift, recall 51.78% → 56.91% (+5.12pp; unimpacted by this promote)
  ~ perl: pre-existing drift, recall 69.44% → 83.33% (+13.89pp; unimpacted by this promote)
  ~ pkg-info: pre-existing drift, recall 87.00% → 65.47% (+21.53pp; unimpacted by this promote)
  ~ png: pre-existing drift, recall 0.00% → 7.27% (+7.27pp; unimpacted by this promote)
  ~ powershell: pre-existing drift, recall 52.76% → 43.71% (+9.05pp; unimpacted by this promote)
  ~ pptx: pre-existing drift, recall 22.22% → 1.39% (+20.83pp; unimpacted by this promote)
  ~ python-bytecode: pre-existing drift, recall 92.09% → 88.14% (+3.95pp; unimpacted by this promote)
  ~ shell: pre-existing drift, recall 81.64% → 85.26% (+3.62pp; unimpacted by this promote)
  ~ tar: pre-existing drift, recall 88.19% → 81.54% (+6.65pp; unimpacted by this promote)
  ~ vbs: pre-existing drift, recall 42.72% → 47.69% (+4.97pp; unimpacted by this promote)
  ~ xls: pre-existing drift, recall 93.19% → 90.97% (+2.22pp; unimpacted by this promote)
  ~ xlsx: pre-existing drift, recall 36.08% → 29.09% (+6.99pp; unimpacted by this promote)
  ~ xml: pre-existing drift, recall 2.55% → 13.23% (+10.68pp; unimpacted by this promote)
  ~ zip: pre-existing drift, recall 31.45% → 31.98% (+0.53pp; unimpacted by this promote)

19 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + crx: L4 hostile ensemble recall +34.88pp above LWM (0.00% → 34.88%)
  + deb: L4 hostile ensemble recall +11.11pp above LWM (0.00% → 11.11%)
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
  + shell: L4 hostile ensemble recall +2.47pp above LWM (82.78% → 85.26%)
  + tar: L4 hostile ensemble recall +19.54pp above LWM (62.00% → 81.54%)
  + vbs: L4 hostile ensemble recall +21.99pp above LWM (25.70% → 47.69%)
  + xml: L4 hostile ensemble recall +10.49pp above LWM (2.74% → 13.23%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - python: L4 hostile ENSEMBLE recall dropped 12.96pp BELOW LOW-WATER-MARK (64.28% → 51.32%; LWM tolerance 0.90pp)

compared 75 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: low-water-mark gate (1 filetype(s) below LWM beyond the 0.90pp tolerance vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[1]: *** [Makefile:1291: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9958)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `a8e6f3e5fa270e5c` | `0afcefc0421a7093` | `1f32101250d1dcd1` |
| PR AUC | 0.9958 | 0.9962 | 0.9961 |
| ROC AUC | 0.9967 | 0.9969 | 0.9968 |
| F1 | 0.9710 | 0.9737 | 0.9739 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-06T09-26-05_20260606T092604-promote-a8e6f3e5fa270e5c_azoth-validate.log; tail:   ~ macho: pre-existing drift, recall 80.24% → 68.26% (+11.98pp; unimpacted by this promote)
  ~ msi: pre-existing drift, recall 0.00% → 58.05% (+58.05pp; unimpacted by this promote)
  ~ ole: pre-existing drift, recall 82.17% → 50.88% (+31.29pp; unimpacted by this promote)
  ~ pdf: pre-existing drift, recall 6.50% → 4.25% (+2.25pp; unimpacted by this promote)
  ~ pe: pre-existing drift, recall 51.78% → 56.91% (+5.12pp; unimpacted by this promote)
  ~ perl: pre-existing drift, recall 69.44% → 83.33% (+13.89pp; unimpacted by this promote)
  ~ pkg-info: pre-existing drift, recall 87.00% → 65.47% (+21.53pp; unimpacted by this promote)
  ~ png: pre-existing drift, recall 0.00% → 7.27% (+7.27pp; unimpacted by this promote)
  ~ powershell: pre-existing drift, recall 52.76% → 43.71% (+9.05pp; unimpacted by this promote)
  ~ pptx: pre-existing drift, recall 22.22% → 1.39% (+20.83pp; unimpacted by this promote)
  ~ python-bytecode: pre-existing drift, recall 92.09% → 88.14% (+3.95pp; unimpacted by this promote)
  ~ shell: pre-existing drift, recall 81.64% → 85.26% (+3.62pp; unimpacted by this promote)
  ~ tar: pre-existing drift, recall 88.19% → 81.54% (+6.65pp; unimpacted by this promote)
  ~ vbs: pre-existing drift, recall 42.72% → 47.69% (+4.97pp; unimpacted by this promote)
  ~ xls: pre-existing drift, recall 93.19% → 90.97% (+2.22pp; unimpacted by this promote)
  ~ xlsx: pre-existing drift, recall 36.08% → 29.09% (+6.99pp; unimpacted by this promote)
  ~ xml: pre-existing drift, recall 2.55% → 13.23% (+10.68pp; unimpacted by this promote)
  ~ zip: pre-existing drift, recall 31.45% → 31.98% (+0.53pp; unimpacted by this promote)

19 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + crx: L4 hostile ensemble recall +34.88pp above LWM (0.00% → 34.88%)
  + deb: L4 hostile ensemble recall +11.11pp above LWM (0.00% → 11.11%)
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
  + shell: L4 hostile ensemble recall +2.47pp above LWM (82.78% → 85.26%)
  + tar: L4 hostile ensemble recall +19.54pp above LWM (62.00% → 81.54%)
  + vbs: L4 hostile ensemble recall +21.99pp above LWM (25.70% → 47.69%)
  + xml: L4 hostile ensemble recall +10.49pp above LWM (2.74% → 13.23%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - python: L4 hostile ENSEMBLE recall dropped 12.96pp BELOW LOW-WATER-MARK (64.28% → 51.32%; LWM tolerance 0.90pp)

compared 75 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: low-water-mark gate (1 filetype(s) below LWM beyond the 0.90pp tolerance vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[1]: *** [Makefile:1291: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')
