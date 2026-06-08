# Promote REJECTED — `68d6e54d9c7b48c2` on `general`

Generated 2026-06-08T11:34:04Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-08T11-29-31_20260608T112930-promote-68d6e54d9c7b48c2_azoth-validate.log; tail:   + 7z: L50 hostile ensemble recall +16.64pp above LWM (13.53% → 30.17%)
  + c: L50 hostile ensemble recall +1.45pp above LWM (8.53% → 9.98%)
  + cab: L50 hostile ensemble recall +1.04pp above LWM (0.00% → 1.04%)
  + cargo.toml: L50 hostile ensemble recall +22.22pp above LWM (0.00% → 22.22%)
  + chrome-manifest: L50 hostile ensemble recall +19.64pp above LWM (42.86% → 62.50%)
  + crx: L50 hostile ensemble recall +30.51pp above LWM (37.98% → 68.49%)
  + docx: L50 hostile ensemble recall +34.91pp above LWM (44.66% → 79.57%)
  + elf: L50 hostile ensemble recall +4.32pp above LWM (91.77% → 96.09%)
  + jar: L50 hostile ensemble recall +7.42pp above LWM (48.09% → 55.51%)
  + java_class: L50 hostile ensemble recall +39.53pp above LWM (23.08% → 62.61%)
  + javascript: L50 hostile ensemble recall +24.16pp above LWM (39.17% → 63.33%)
  + kotlin: L50 hostile ensemble recall +7.88pp above LWM (46.48% → 54.35%)
  + lnk: L50 hostile ensemble recall +12.05pp above LWM (66.73% → 78.78%)
  + lua: L50 hostile ensemble recall +15.38pp above LWM (53.85% → 69.23%)
  + macho: L50 hostile ensemble recall +9.65pp above LWM (68.26% → 77.91%)
  + msi: L50 hostile ensemble recall +34.23pp above LWM (38.34% → 72.56%)
  + ole: L50 hostile ensemble recall +30.02pp above LWM (50.88% → 80.90%)
  + package.json: L50 hostile ensemble recall +7.50pp above LWM (78.39% → 85.89%)
  + pe: L50 hostile ensemble recall +17.11pp above LWM (37.61% → 54.72%)
  + pkg-info: L50 hostile ensemble recall +29.29pp above LWM (65.47% → 94.75%)
  + plist: L50 hostile ensemble recall +3.82pp above LWM (1.52% → 5.33%)
  + png: L50 hostile ensemble recall +5.40pp above LWM (0.12% → 5.52%)
  + powershell: L50 hostile ensemble recall +9.37pp above LWM (43.71% → 53.08%)
  + shell: L50 hostile ensemble recall +28.14pp above LWM (43.91% → 72.05%)
  + tar: L50 hostile ensemble recall +4.77pp above LWM (81.54% → 86.30%)
  + vbs: L50 hostile ensemble recall +14.60pp above LWM (42.09% → 56.69%)
  + xls: L50 hostile ensemble recall +3.44pp above LWM (90.97% → 94.40%)
  + xlsx: L50 hostile ensemble recall +1.37pp above LWM (29.09% → 30.46%)
  + zip: L50 hostile ensemble recall +2.12pp above LWM (31.98% → 34.10%)
  + zst: L50 hostile ensemble recall +28.22pp above LWM (8.42% → 36.63%)

1 DEPLOYED-TOLERANCE regression(s) (vs currently-deployed bundle /home/t/.local/share/litmus/models/azoth) — THIS IS WHAT BLOCKS THE DEPLOY:
  - vbs: L50 hostile ENSEMBLE recall dropped 12.33pp (69.01% → 56.69%; tolerance 1.70pp; deployed 95% CI lower = 66.55%)

7 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - csharp: L50 hostile ENSEMBLE recall dropped 8.53pp BELOW LOW-WATER-MARK (25.62% → 17.09%; LWM tolerance 0.90pp)
  - deb: L50 hostile ENSEMBLE recall dropped 1.11pp BELOW LOW-WATER-MARK (11.11% → 10.00%; LWM tolerance 0.90pp)
  - java: L50 hostile ENSEMBLE recall dropped 25.07pp BELOW LOW-WATER-MARK (30.00% → 4.93%; LWM tolerance 0.90pp)
  - jpeg: L50 hostile ENSEMBLE recall dropped 7.43pp BELOW LOW-WATER-MARK (11.92% → 4.49%; LWM tolerance 0.90pp)
  - perl: L50 hostile ENSEMBLE recall dropped 18.16pp BELOW LOW-WATER-MARK (69.44% → 51.28%; LWM tolerance 0.90pp)
  - php: L50 hostile ENSEMBLE recall dropped 3.81pp BELOW LOW-WATER-MARK (47.03% → 43.22%; LWM tolerance 0.90pp)
  - python-bytecode: L50 hostile ENSEMBLE recall dropped 4.80pp BELOW LOW-WATER-MARK (88.14% → 83.33%; LWM tolerance 0.90pp)

compared 75 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: deployed-tolerance gate (1 filetype(s) regressed vs deployed beyond the 1.70pp tolerance; see list above for the actual drops), low-water-mark gate (7 filetype(s) below LWM beyond the 0.90pp tolerance vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[1]: *** [Makefile:1310: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9981)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `68d6e54d9c7b48c2` | `f1f65b09593fd9f7` | `c4e6357792205071` |
| PR AUC | 0.9981 | 0.9998 | 0.9994 |
| ROC AUC | 0.9980 | 0.9994 | 0.9994 |
| F1 | 0.9813 | 0.9947 | 0.9901 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-08T11-29-31_20260608T112930-promote-68d6e54d9c7b48c2_azoth-validate.log; tail:   + 7z: L50 hostile ensemble recall +16.64pp above LWM (13.53% → 30.17%)
  + c: L50 hostile ensemble recall +1.45pp above LWM (8.53% → 9.98%)
  + cab: L50 hostile ensemble recall +1.04pp above LWM (0.00% → 1.04%)
  + cargo.toml: L50 hostile ensemble recall +22.22pp above LWM (0.00% → 22.22%)
  + chrome-manifest: L50 hostile ensemble recall +19.64pp above LWM (42.86% → 62.50%)
  + crx: L50 hostile ensemble recall +30.51pp above LWM (37.98% → 68.49%)
  + docx: L50 hostile ensemble recall +34.91pp above LWM (44.66% → 79.57%)
  + elf: L50 hostile ensemble recall +4.32pp above LWM (91.77% → 96.09%)
  + jar: L50 hostile ensemble recall +7.42pp above LWM (48.09% → 55.51%)
  + java_class: L50 hostile ensemble recall +39.53pp above LWM (23.08% → 62.61%)
  + javascript: L50 hostile ensemble recall +24.16pp above LWM (39.17% → 63.33%)
  + kotlin: L50 hostile ensemble recall +7.88pp above LWM (46.48% → 54.35%)
  + lnk: L50 hostile ensemble recall +12.05pp above LWM (66.73% → 78.78%)
  + lua: L50 hostile ensemble recall +15.38pp above LWM (53.85% → 69.23%)
  + macho: L50 hostile ensemble recall +9.65pp above LWM (68.26% → 77.91%)
  + msi: L50 hostile ensemble recall +34.23pp above LWM (38.34% → 72.56%)
  + ole: L50 hostile ensemble recall +30.02pp above LWM (50.88% → 80.90%)
  + package.json: L50 hostile ensemble recall +7.50pp above LWM (78.39% → 85.89%)
  + pe: L50 hostile ensemble recall +17.11pp above LWM (37.61% → 54.72%)
  + pkg-info: L50 hostile ensemble recall +29.29pp above LWM (65.47% → 94.75%)
  + plist: L50 hostile ensemble recall +3.82pp above LWM (1.52% → 5.33%)
  + png: L50 hostile ensemble recall +5.40pp above LWM (0.12% → 5.52%)
  + powershell: L50 hostile ensemble recall +9.37pp above LWM (43.71% → 53.08%)
  + shell: L50 hostile ensemble recall +28.14pp above LWM (43.91% → 72.05%)
  + tar: L50 hostile ensemble recall +4.77pp above LWM (81.54% → 86.30%)
  + vbs: L50 hostile ensemble recall +14.60pp above LWM (42.09% → 56.69%)
  + xls: L50 hostile ensemble recall +3.44pp above LWM (90.97% → 94.40%)
  + xlsx: L50 hostile ensemble recall +1.37pp above LWM (29.09% → 30.46%)
  + zip: L50 hostile ensemble recall +2.12pp above LWM (31.98% → 34.10%)
  + zst: L50 hostile ensemble recall +28.22pp above LWM (8.42% → 36.63%)

1 DEPLOYED-TOLERANCE regression(s) (vs currently-deployed bundle /home/t/.local/share/litmus/models/azoth) — THIS IS WHAT BLOCKS THE DEPLOY:
  - vbs: L50 hostile ENSEMBLE recall dropped 12.33pp (69.01% → 56.69%; tolerance 1.70pp; deployed 95% CI lower = 66.55%)

7 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - csharp: L50 hostile ENSEMBLE recall dropped 8.53pp BELOW LOW-WATER-MARK (25.62% → 17.09%; LWM tolerance 0.90pp)
  - deb: L50 hostile ENSEMBLE recall dropped 1.11pp BELOW LOW-WATER-MARK (11.11% → 10.00%; LWM tolerance 0.90pp)
  - java: L50 hostile ENSEMBLE recall dropped 25.07pp BELOW LOW-WATER-MARK (30.00% → 4.93%; LWM tolerance 0.90pp)
  - jpeg: L50 hostile ENSEMBLE recall dropped 7.43pp BELOW LOW-WATER-MARK (11.92% → 4.49%; LWM tolerance 0.90pp)
  - perl: L50 hostile ENSEMBLE recall dropped 18.16pp BELOW LOW-WATER-MARK (69.44% → 51.28%; LWM tolerance 0.90pp)
  - php: L50 hostile ENSEMBLE recall dropped 3.81pp BELOW LOW-WATER-MARK (47.03% → 43.22%; LWM tolerance 0.90pp)
  - python-bytecode: L50 hostile ENSEMBLE recall dropped 4.80pp BELOW LOW-WATER-MARK (88.14% → 83.33%; LWM tolerance 0.90pp)

compared 75 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: deployed-tolerance gate (1 filetype(s) regressed vs deployed beyond the 1.70pp tolerance; see list above for the actual drops), low-water-mark gate (7 filetype(s) below LWM beyond the 0.90pp tolerance vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[1]: *** [Makefile:1310: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')
