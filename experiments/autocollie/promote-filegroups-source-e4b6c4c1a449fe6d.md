# Promote REJECTED — `e4b6c4c1a449fe6d` on `filegroups/source`

Generated 2026-06-08T10:46:58Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-08T10-43-02_20260608T104300-promote-e4b6c4c1a449fe6d_azoth-validate.log; tail: 
ensemble improvements (≥0.10pp):
  csharp: L50 hostile ensemble recall +2.53pp (16.46% → 18.99%)
  java: L50 hostile ensemble recall +2.11pp (2.82% → 4.93%)
  kotlin: L50 hostile ensemble recall +0.61pp (50.50% → 51.11%)

per-route improvements (≥0.10pp, informational):
  go :: filegroups/source recall@1FP-on-slice +2.30pp (2.07% → 4.37%)
  makefile :: filetypes/makefile recall@1FP-on-slice +2.67pp (0.00% → 2.67%)

per-route regressions (informational; does not block deploy):
  csharp :: filegroups/source recall@1FP-on-slice dropped 1.90pp (25.00% → 23.10%)
  kotlin :: filegroups/source recall@1FP-on-slice dropped 2.53pp (57.72% → 55.20%)

23 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + 7z: L50 hostile ensemble recall +7.60pp above LWM (13.53% → 21.13%)
  + c: L50 hostile ensemble recall +1.29pp above LWM (8.53% → 9.82%)
  + cargo.toml: L50 hostile ensemble recall +22.22pp above LWM (0.00% → 22.22%)
  + crx: L50 hostile ensemble recall +30.51pp above LWM (37.98% → 68.49%)
  + docx: L50 hostile ensemble recall +34.91pp above LWM (44.66% → 79.57%)
  + elf: L50 hostile ensemble recall +4.32pp above LWM (91.77% → 96.09%)
  + jar: L50 hostile ensemble recall +7.42pp above LWM (48.09% → 55.51%)
  + javascript: L50 hostile ensemble recall +24.16pp above LWM (39.17% → 63.33%)
  + kotlin: L50 hostile ensemble recall +4.64pp above LWM (46.48% → 51.11%)
  + lnk: L50 hostile ensemble recall +12.05pp above LWM (66.73% → 78.78%)
  + macho: L50 hostile ensemble recall +9.65pp above LWM (68.26% → 77.91%)
  + msi: L50 hostile ensemble recall +6.97pp above LWM (38.34% → 45.31%)
  + ole: L50 hostile ensemble recall +30.02pp above LWM (50.88% → 80.90%)
  + package.json: L50 hostile ensemble recall +7.50pp above LWM (78.39% → 85.89%)
  + pe: L50 hostile ensemble recall +17.11pp above LWM (37.61% → 54.72%)
  + pkg-info: L50 hostile ensemble recall +10.73pp above LWM (65.47% → 76.19%)
  + powershell: L50 hostile ensemble recall +9.37pp above LWM (43.71% → 53.08%)
  + shell: L50 hostile ensemble recall +28.14pp above LWM (43.91% → 72.05%)
  + vbs: L50 hostile ensemble recall +26.92pp above LWM (42.09% → 69.01%)
  + xls: L50 hostile ensemble recall +3.44pp above LWM (90.97% → 94.40%)
  + xlsx: L50 hostile ensemble recall +1.37pp above LWM (29.09% → 30.46%)
  + zip: L50 hostile ensemble recall +2.12pp above LWM (31.98% → 34.10%)
  + zst: L50 hostile ensemble recall +5.22pp above LWM (8.42% → 13.64%)

2 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - csharp: L50 hostile ENSEMBLE recall dropped 6.63pp BELOW LOW-WATER-MARK (25.62% → 18.99%; LWM tolerance 0.90pp)
  - java: L50 hostile ENSEMBLE recall dropped 25.07pp BELOW LOW-WATER-MARK (30.00% → 4.93%; LWM tolerance 0.90pp)

compared 75 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: low-water-mark gate (2 filetype(s) below LWM beyond the 0.90pp tolerance vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[1]: *** [Makefile:1310: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9982)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `e4b6c4c1a449fe6d` | `8c56283bd76abc76` | `bf8e4e83d87a19a2` |
| PR AUC | 0.9982 | 0.9984 | 0.9984 |
| ROC AUC | 0.9975 | 0.9978 | 0.9979 |
| F1 | 0.9740 | 0.9820 | 0.9821 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-08T10-43-02_20260608T104300-promote-e4b6c4c1a449fe6d_azoth-validate.log; tail: 
ensemble improvements (≥0.10pp):
  csharp: L50 hostile ensemble recall +2.53pp (16.46% → 18.99%)
  java: L50 hostile ensemble recall +2.11pp (2.82% → 4.93%)
  kotlin: L50 hostile ensemble recall +0.61pp (50.50% → 51.11%)

per-route improvements (≥0.10pp, informational):
  go :: filegroups/source recall@1FP-on-slice +2.30pp (2.07% → 4.37%)
  makefile :: filetypes/makefile recall@1FP-on-slice +2.67pp (0.00% → 2.67%)

per-route regressions (informational; does not block deploy):
  csharp :: filegroups/source recall@1FP-on-slice dropped 1.90pp (25.00% → 23.10%)
  kotlin :: filegroups/source recall@1FP-on-slice dropped 2.53pp (57.72% → 55.20%)

23 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + 7z: L50 hostile ensemble recall +7.60pp above LWM (13.53% → 21.13%)
  + c: L50 hostile ensemble recall +1.29pp above LWM (8.53% → 9.82%)
  + cargo.toml: L50 hostile ensemble recall +22.22pp above LWM (0.00% → 22.22%)
  + crx: L50 hostile ensemble recall +30.51pp above LWM (37.98% → 68.49%)
  + docx: L50 hostile ensemble recall +34.91pp above LWM (44.66% → 79.57%)
  + elf: L50 hostile ensemble recall +4.32pp above LWM (91.77% → 96.09%)
  + jar: L50 hostile ensemble recall +7.42pp above LWM (48.09% → 55.51%)
  + javascript: L50 hostile ensemble recall +24.16pp above LWM (39.17% → 63.33%)
  + kotlin: L50 hostile ensemble recall +4.64pp above LWM (46.48% → 51.11%)
  + lnk: L50 hostile ensemble recall +12.05pp above LWM (66.73% → 78.78%)
  + macho: L50 hostile ensemble recall +9.65pp above LWM (68.26% → 77.91%)
  + msi: L50 hostile ensemble recall +6.97pp above LWM (38.34% → 45.31%)
  + ole: L50 hostile ensemble recall +30.02pp above LWM (50.88% → 80.90%)
  + package.json: L50 hostile ensemble recall +7.50pp above LWM (78.39% → 85.89%)
  + pe: L50 hostile ensemble recall +17.11pp above LWM (37.61% → 54.72%)
  + pkg-info: L50 hostile ensemble recall +10.73pp above LWM (65.47% → 76.19%)
  + powershell: L50 hostile ensemble recall +9.37pp above LWM (43.71% → 53.08%)
  + shell: L50 hostile ensemble recall +28.14pp above LWM (43.91% → 72.05%)
  + vbs: L50 hostile ensemble recall +26.92pp above LWM (42.09% → 69.01%)
  + xls: L50 hostile ensemble recall +3.44pp above LWM (90.97% → 94.40%)
  + xlsx: L50 hostile ensemble recall +1.37pp above LWM (29.09% → 30.46%)
  + zip: L50 hostile ensemble recall +2.12pp above LWM (31.98% → 34.10%)
  + zst: L50 hostile ensemble recall +5.22pp above LWM (8.42% → 13.64%)

2 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - csharp: L50 hostile ENSEMBLE recall dropped 6.63pp BELOW LOW-WATER-MARK (25.62% → 18.99%; LWM tolerance 0.90pp)
  - java: L50 hostile ENSEMBLE recall dropped 25.07pp BELOW LOW-WATER-MARK (30.00% → 4.93%; LWM tolerance 0.90pp)

compared 75 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: low-water-mark gate (2 filetype(s) below LWM beyond the 0.90pp tolerance vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[1]: *** [Makefile:1310: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')
