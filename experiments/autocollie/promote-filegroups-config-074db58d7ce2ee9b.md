# Promote REJECTED — `074db58d7ce2ee9b` on `filegroups/config`

Generated 2026-06-08T11:15:43Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-08T11-12-30_20260608T111229-promote-074db58d7ce2ee9b_azoth-validate.log; tail: 
ensemble improvements (≥0.10pp):
  xml: L50 hostile ensemble recall +10.53pp (2.29% → 12.81%)

per-route improvements (≥0.10pp, informational):
  plist :: filegroups/config recall@1FP-on-slice +1.33pp (5.33% → 6.67%)
  xml :: filegroups/config recall@1FP-on-slice +10.30pp (2.52% → 12.81%)

per-route regressions (informational; does not block deploy):
  package.json :: filegroups/config recall@1FP-on-slice dropped 8.55pp (95.77% → 87.22%)
  package.json :: filetypes/package.json recall@1FP-on-slice dropped 2.85pp (93.37% → 90.52%)

23 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + 7z: L50 hostile ensemble recall +7.60pp above LWM (13.53% → 21.13%)
  + c: L50 hostile ensemble recall +2.07pp above LWM (8.53% → 10.60%)
  + cargo.toml: L50 hostile ensemble recall +22.22pp above LWM (0.00% → 22.22%)
  + crx: L50 hostile ensemble recall +30.51pp above LWM (37.98% → 68.49%)
  + docx: L50 hostile ensemble recall +34.91pp above LWM (44.66% → 79.57%)
  + elf: L50 hostile ensemble recall +4.32pp above LWM (91.77% → 96.09%)
  + jar: L50 hostile ensemble recall +7.42pp above LWM (48.09% → 55.51%)
  + javascript: L50 hostile ensemble recall +24.16pp above LWM (39.17% → 63.33%)
  + kotlin: L50 hostile ensemble recall +4.02pp above LWM (46.48% → 50.50%)
  + lnk: L50 hostile ensemble recall +12.05pp above LWM (66.73% → 78.78%)
  + macho: L50 hostile ensemble recall +9.65pp above LWM (68.26% → 77.91%)
  + msi: L50 hostile ensemble recall +6.97pp above LWM (38.34% → 45.31%)
  + ole: L50 hostile ensemble recall +30.02pp above LWM (50.88% → 80.90%)
  + pe: L50 hostile ensemble recall +17.11pp above LWM (37.61% → 54.72%)
  + pkg-info: L50 hostile ensemble recall +10.73pp above LWM (65.47% → 76.19%)
  + powershell: L50 hostile ensemble recall +9.37pp above LWM (43.71% → 53.08%)
  + shell: L50 hostile ensemble recall +28.14pp above LWM (43.91% → 72.05%)
  + vbs: L50 hostile ensemble recall +26.92pp above LWM (42.09% → 69.01%)
  + xls: L50 hostile ensemble recall +3.44pp above LWM (90.97% → 94.40%)
  + xlsx: L50 hostile ensemble recall +1.37pp above LWM (29.09% → 30.46%)
  + xml: L50 hostile ensemble recall +10.27pp above LWM (2.54% → 12.81%)
  + zip: L50 hostile ensemble recall +2.12pp above LWM (31.98% → 34.10%)
  + zst: L50 hostile ensemble recall +5.22pp above LWM (8.42% → 13.64%)

1 DEPLOYED-TOLERANCE regression(s) (vs currently-deployed bundle /home/t/.local/share/litmus/models/azoth) — THIS IS WHAT BLOCKS THE DEPLOY:
  - package.json: L50 hostile ENSEMBLE recall dropped 12.47pp (87.22% → 74.76%; tolerance 1.70pp; deployed 95% CI lower = 85.77%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - package.json: L50 hostile ENSEMBLE recall dropped 3.63pp BELOW LOW-WATER-MARK (78.39% → 74.76%; LWM tolerance 0.90pp)

compared 75 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: deployed-tolerance gate (1 filetype(s) regressed vs deployed beyond the 1.70pp tolerance; see list above for the actual drops), low-water-mark gate (1 filetype(s) below LWM beyond the 0.90pp tolerance vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[1]: *** [Makefile:1310: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9987)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `074db58d7ce2ee9b` | `8ac66087d18d9a9c` | `494f5d305bd323e8` |
| PR AUC | 0.9987 | 0.9988 | 0.9988 |
| ROC AUC | 0.9981 | 0.9983 | 0.9983 |
| F1 | 0.9929 | 0.9939 | 0.9937 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-08T11-12-30_20260608T111229-promote-074db58d7ce2ee9b_azoth-validate.log; tail: 
ensemble improvements (≥0.10pp):
  xml: L50 hostile ensemble recall +10.53pp (2.29% → 12.81%)

per-route improvements (≥0.10pp, informational):
  plist :: filegroups/config recall@1FP-on-slice +1.33pp (5.33% → 6.67%)
  xml :: filegroups/config recall@1FP-on-slice +10.30pp (2.52% → 12.81%)

per-route regressions (informational; does not block deploy):
  package.json :: filegroups/config recall@1FP-on-slice dropped 8.55pp (95.77% → 87.22%)
  package.json :: filetypes/package.json recall@1FP-on-slice dropped 2.85pp (93.37% → 90.52%)

23 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + 7z: L50 hostile ensemble recall +7.60pp above LWM (13.53% → 21.13%)
  + c: L50 hostile ensemble recall +2.07pp above LWM (8.53% → 10.60%)
  + cargo.toml: L50 hostile ensemble recall +22.22pp above LWM (0.00% → 22.22%)
  + crx: L50 hostile ensemble recall +30.51pp above LWM (37.98% → 68.49%)
  + docx: L50 hostile ensemble recall +34.91pp above LWM (44.66% → 79.57%)
  + elf: L50 hostile ensemble recall +4.32pp above LWM (91.77% → 96.09%)
  + jar: L50 hostile ensemble recall +7.42pp above LWM (48.09% → 55.51%)
  + javascript: L50 hostile ensemble recall +24.16pp above LWM (39.17% → 63.33%)
  + kotlin: L50 hostile ensemble recall +4.02pp above LWM (46.48% → 50.50%)
  + lnk: L50 hostile ensemble recall +12.05pp above LWM (66.73% → 78.78%)
  + macho: L50 hostile ensemble recall +9.65pp above LWM (68.26% → 77.91%)
  + msi: L50 hostile ensemble recall +6.97pp above LWM (38.34% → 45.31%)
  + ole: L50 hostile ensemble recall +30.02pp above LWM (50.88% → 80.90%)
  + pe: L50 hostile ensemble recall +17.11pp above LWM (37.61% → 54.72%)
  + pkg-info: L50 hostile ensemble recall +10.73pp above LWM (65.47% → 76.19%)
  + powershell: L50 hostile ensemble recall +9.37pp above LWM (43.71% → 53.08%)
  + shell: L50 hostile ensemble recall +28.14pp above LWM (43.91% → 72.05%)
  + vbs: L50 hostile ensemble recall +26.92pp above LWM (42.09% → 69.01%)
  + xls: L50 hostile ensemble recall +3.44pp above LWM (90.97% → 94.40%)
  + xlsx: L50 hostile ensemble recall +1.37pp above LWM (29.09% → 30.46%)
  + xml: L50 hostile ensemble recall +10.27pp above LWM (2.54% → 12.81%)
  + zip: L50 hostile ensemble recall +2.12pp above LWM (31.98% → 34.10%)
  + zst: L50 hostile ensemble recall +5.22pp above LWM (8.42% → 13.64%)

1 DEPLOYED-TOLERANCE regression(s) (vs currently-deployed bundle /home/t/.local/share/litmus/models/azoth) — THIS IS WHAT BLOCKS THE DEPLOY:
  - package.json: L50 hostile ENSEMBLE recall dropped 12.47pp (87.22% → 74.76%; tolerance 1.70pp; deployed 95% CI lower = 85.77%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - package.json: L50 hostile ENSEMBLE recall dropped 3.63pp BELOW LOW-WATER-MARK (78.39% → 74.76%; LWM tolerance 0.90pp)

compared 75 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: deployed-tolerance gate (1 filetype(s) regressed vs deployed beyond the 1.70pp tolerance; see list above for the actual drops), low-water-mark gate (1 filetype(s) below LWM beyond the 0.90pp tolerance vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[1]: *** [Makefile:1310: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')
