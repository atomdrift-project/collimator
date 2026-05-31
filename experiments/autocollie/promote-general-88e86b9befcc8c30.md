# Promote REJECTED — `88e86b9befcc8c30` on `general`

Generated 2026-05-30T22:17:45Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-30T22-11-56_20260530T221154-promote-88e86b9befcc8c30_azoth-validate.log; tail:   + c: L3 hostile ensemble recall +1.24pp above LWM (10.02% → 11.26%)
  + chrome-manifest: L3 hostile ensemble recall +16.67pp above LWM (50.00% → 66.67%)
  + crx: L3 hostile ensemble recall +89.74pp above LWM (0.00% → 89.74%)
  + deb: L3 hostile ensemble recall +7.14pp above LWM (0.00% → 7.14%)
  + doc: L3 hostile ensemble recall +3.75pp above LWM (90.99% → 94.74%)
  + html: L3 hostile ensemble recall +48.33pp above LWM (16.67% → 65.00%)
  + jar: L3 hostile ensemble recall +3.15pp above LWM (57.29% → 60.44%)
  + javascript: L3 hostile ensemble recall +2.07pp above LWM (66.20% → 68.27%)
  + jpeg: L3 hostile ensemble recall +11.32pp above LWM (1.56% → 12.88%)
  + lnk: L3 hostile ensemble recall +23.83pp above LWM (48.66% → 72.49%)
  + lua: L3 hostile ensemble recall +54.55pp above LWM (0.00% → 54.55%)
  + objc: L3 hostile ensemble recall +25.00pp above LWM (0.00% → 25.00%)
  + package.json: L3 hostile ensemble recall +4.32pp above LWM (86.78% → 91.10%)
  + pdf: L3 hostile ensemble recall +1.04pp above LWM (6.41% → 7.45%)
  + pe: L3 hostile ensemble recall +7.86pp above LWM (61.96% → 69.82%)
  + pkg-info: L3 hostile ensemble recall +2.90pp above LWM (97.02% → 99.92%)
  + plist: L3 hostile ensemble recall +3.12pp above LWM (2.94% → 6.06%)
  + png: L3 hostile ensemble recall +7.91pp above LWM (1.07% → 8.98%)
  + powershell: L3 hostile ensemble recall +26.76pp above LWM (29.62% → 56.38%)
  + pptx: L3 hostile ensemble recall +15.91pp above LWM (9.09% → 25.00%)
  + python: L3 hostile ensemble recall +2.23pp above LWM (64.28% → 66.51%)
  + ruby: L3 hostile ensemble recall +26.98pp above LWM (28.57% → 55.56%)
  + rust: L3 hostile ensemble recall +1.20pp above LWM (1.22% → 2.42%)
  + shell: L3 hostile ensemble recall +1.27pp above LWM (82.78% → 84.05%)
  + tar: L3 hostile ensemble recall +34.77pp above LWM (62.00% → 96.77%)
  + tar.gz: L3 hostile ensemble recall +19.39pp above LWM (56.69% → 76.08%)
  + vbs: L3 hostile ensemble recall +6.05pp above LWM (25.70% → 31.75%)

14 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - 7z: L3 hostile ENSEMBLE recall dropped 29.74pp BELOW LOW-WATER-MARK (72.74% → 43.00%; LWM tolerance 0.90pp)
  - cab: L3 hostile ENSEMBLE recall dropped 3.45pp BELOW LOW-WATER-MARK (3.45% → 0.00%; LWM tolerance 0.90pp)
  - docx: L3 hostile ENSEMBLE recall dropped 5.90pp BELOW LOW-WATER-MARK (71.59% → 65.69%; LWM tolerance 0.90pp)
  - gz: L3 hostile ENSEMBLE recall dropped 2.28pp BELOW LOW-WATER-MARK (28.32% → 26.05%; LWM tolerance 0.90pp)
  - java: L3 hostile ENSEMBLE recall dropped 35.71pp BELOW LOW-WATER-MARK (50.00% → 14.29%; LWM tolerance 0.90pp)
  - java_class: L3 hostile ENSEMBLE recall dropped 3.30pp BELOW LOW-WATER-MARK (73.41% → 70.11%; LWM tolerance 0.90pp)
  - macho: L3 hostile ENSEMBLE recall dropped 15.26pp BELOW LOW-WATER-MARK (86.64% → 71.38%; LWM tolerance 0.90pp)
  - msi: L3 hostile ENSEMBLE recall dropped 21.57pp BELOW LOW-WATER-MARK (76.17% → 54.60%; LWM tolerance 0.90pp)
  - ole: L3 hostile ENSEMBLE recall dropped 2.83pp BELOW LOW-WATER-MARK (91.27% → 88.44%; LWM tolerance 0.90pp)
  - perl: L3 hostile ENSEMBLE recall dropped 9.92pp BELOW LOW-WATER-MARK (77.78% → 67.86%; LWM tolerance 0.90pp)
  - php: L3 hostile ENSEMBLE recall dropped 6.53pp BELOW LOW-WATER-MARK (62.11% → 55.58%; LWM tolerance 0.90pp)
  - xlsx: L3 hostile ENSEMBLE recall dropped 28.86pp BELOW LOW-WATER-MARK (29.01% → 0.15%; LWM tolerance 0.90pp)
  - zip: L3 hostile ENSEMBLE recall dropped 5.30pp BELOW LOW-WATER-MARK (40.61% → 35.32%; LWM tolerance 0.90pp)
  - zst: L3 hostile ENSEMBLE recall dropped 21.95pp BELOW LOW-WATER-MARK (76.60% → 54.65%; LWM tolerance 0.90pp)

compared 70 filetypes (mal≥1, ben≥1); 4 below threshold and skipped.

blocked by: low-water-mark gate (14 filetype(s) below LWM beyond the 0.90pp tolerance vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1158: azoth-validate] Error 1)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9996)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `88e86b9befcc8c30` | `86988e8c29120326` | `88e86b9befcc8c30` |
| PR AUC | 0.9996 | 0.9999 | 0.9996 |
| ROC AUC | 0.9995 | 0.9996 | 0.9995 |
| F1 | 0.9910 | 0.9948 | 0.9910 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-30T22-11-56_20260530T221154-promote-88e86b9befcc8c30_azoth-validate.log; tail:   + c: L3 hostile ensemble recall +1.24pp above LWM (10.02% → 11.26%)
  + chrome-manifest: L3 hostile ensemble recall +16.67pp above LWM (50.00% → 66.67%)
  + crx: L3 hostile ensemble recall +89.74pp above LWM (0.00% → 89.74%)
  + deb: L3 hostile ensemble recall +7.14pp above LWM (0.00% → 7.14%)
  + doc: L3 hostile ensemble recall +3.75pp above LWM (90.99% → 94.74%)
  + html: L3 hostile ensemble recall +48.33pp above LWM (16.67% → 65.00%)
  + jar: L3 hostile ensemble recall +3.15pp above LWM (57.29% → 60.44%)
  + javascript: L3 hostile ensemble recall +2.07pp above LWM (66.20% → 68.27%)
  + jpeg: L3 hostile ensemble recall +11.32pp above LWM (1.56% → 12.88%)
  + lnk: L3 hostile ensemble recall +23.83pp above LWM (48.66% → 72.49%)
  + lua: L3 hostile ensemble recall +54.55pp above LWM (0.00% → 54.55%)
  + objc: L3 hostile ensemble recall +25.00pp above LWM (0.00% → 25.00%)
  + package.json: L3 hostile ensemble recall +4.32pp above LWM (86.78% → 91.10%)
  + pdf: L3 hostile ensemble recall +1.04pp above LWM (6.41% → 7.45%)
  + pe: L3 hostile ensemble recall +7.86pp above LWM (61.96% → 69.82%)
  + pkg-info: L3 hostile ensemble recall +2.90pp above LWM (97.02% → 99.92%)
  + plist: L3 hostile ensemble recall +3.12pp above LWM (2.94% → 6.06%)
  + png: L3 hostile ensemble recall +7.91pp above LWM (1.07% → 8.98%)
  + powershell: L3 hostile ensemble recall +26.76pp above LWM (29.62% → 56.38%)
  + pptx: L3 hostile ensemble recall +15.91pp above LWM (9.09% → 25.00%)
  + python: L3 hostile ensemble recall +2.23pp above LWM (64.28% → 66.51%)
  + ruby: L3 hostile ensemble recall +26.98pp above LWM (28.57% → 55.56%)
  + rust: L3 hostile ensemble recall +1.20pp above LWM (1.22% → 2.42%)
  + shell: L3 hostile ensemble recall +1.27pp above LWM (82.78% → 84.05%)
  + tar: L3 hostile ensemble recall +34.77pp above LWM (62.00% → 96.77%)
  + tar.gz: L3 hostile ensemble recall +19.39pp above LWM (56.69% → 76.08%)
  + vbs: L3 hostile ensemble recall +6.05pp above LWM (25.70% → 31.75%)

14 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - 7z: L3 hostile ENSEMBLE recall dropped 29.74pp BELOW LOW-WATER-MARK (72.74% → 43.00%; LWM tolerance 0.90pp)
  - cab: L3 hostile ENSEMBLE recall dropped 3.45pp BELOW LOW-WATER-MARK (3.45% → 0.00%; LWM tolerance 0.90pp)
  - docx: L3 hostile ENSEMBLE recall dropped 5.90pp BELOW LOW-WATER-MARK (71.59% → 65.69%; LWM tolerance 0.90pp)
  - gz: L3 hostile ENSEMBLE recall dropped 2.28pp BELOW LOW-WATER-MARK (28.32% → 26.05%; LWM tolerance 0.90pp)
  - java: L3 hostile ENSEMBLE recall dropped 35.71pp BELOW LOW-WATER-MARK (50.00% → 14.29%; LWM tolerance 0.90pp)
  - java_class: L3 hostile ENSEMBLE recall dropped 3.30pp BELOW LOW-WATER-MARK (73.41% → 70.11%; LWM tolerance 0.90pp)
  - macho: L3 hostile ENSEMBLE recall dropped 15.26pp BELOW LOW-WATER-MARK (86.64% → 71.38%; LWM tolerance 0.90pp)
  - msi: L3 hostile ENSEMBLE recall dropped 21.57pp BELOW LOW-WATER-MARK (76.17% → 54.60%; LWM tolerance 0.90pp)
  - ole: L3 hostile ENSEMBLE recall dropped 2.83pp BELOW LOW-WATER-MARK (91.27% → 88.44%; LWM tolerance 0.90pp)
  - perl: L3 hostile ENSEMBLE recall dropped 9.92pp BELOW LOW-WATER-MARK (77.78% → 67.86%; LWM tolerance 0.90pp)
  - php: L3 hostile ENSEMBLE recall dropped 6.53pp BELOW LOW-WATER-MARK (62.11% → 55.58%; LWM tolerance 0.90pp)
  - xlsx: L3 hostile ENSEMBLE recall dropped 28.86pp BELOW LOW-WATER-MARK (29.01% → 0.15%; LWM tolerance 0.90pp)
  - zip: L3 hostile ENSEMBLE recall dropped 5.30pp BELOW LOW-WATER-MARK (40.61% → 35.32%; LWM tolerance 0.90pp)
  - zst: L3 hostile ENSEMBLE recall dropped 21.95pp BELOW LOW-WATER-MARK (76.60% → 54.65%; LWM tolerance 0.90pp)

compared 70 filetypes (mal≥1, ben≥1); 4 below threshold and skipped.

blocked by: low-water-mark gate (14 filetype(s) below LWM beyond the 0.90pp tolerance vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1158: azoth-validate] Error 1)
