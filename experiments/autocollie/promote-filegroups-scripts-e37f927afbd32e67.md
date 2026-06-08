# Promote REJECTED — `e37f927afbd32e67` on `filegroups/scripts`

Generated 2026-06-08T10:30:41Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-08T10-26-02_20260608T102600-promote-e37f927afbd32e67_azoth-validate.log; tail:   python :: filegroups/scripts recall@1FP-on-slice +2.35pp (55.47% → 57.82%)
  python :: filetypes/python recall@1FP-on-slice +2.66pp (60.40% → 63.06%)
  ruby :: filegroups/scripts recall@1FP-on-slice +11.76pp (35.29% → 47.06%)
  shell :: filegroups/scripts recall@1FP-on-slice +12.31pp (60.70% → 73.01%)
  shell :: filetypes/shell recall@1FP-on-slice +17.33pp (63.55% → 80.88%)

per-route regressions (informational; does not block deploy):
  php :: filegroups/scripts recall@1FP-on-slice dropped 4.02pp (46.35% → 42.32%)
  powershell :: filetypes/powershell recall@1FP-on-slice dropped 11.69pp (60.15% → 48.46%)

23 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + 7z: L50 hostile ensemble recall +7.60pp above LWM (13.53% → 21.13%)
  + c: L50 hostile ensemble recall +2.07pp above LWM (8.53% → 10.60%)
  + cargo.toml: L50 hostile ensemble recall +22.22pp above LWM (0.00% → 22.22%)
  + crx: L50 hostile ensemble recall +30.51pp above LWM (37.98% → 68.49%)
  + docx: L50 hostile ensemble recall +34.91pp above LWM (44.66% → 79.57%)
  + elf: L50 hostile ensemble recall +4.32pp above LWM (91.77% → 96.09%)
  + jar: L50 hostile ensemble recall +7.42pp above LWM (48.09% → 55.51%)
  + javascript: L50 hostile ensemble recall +24.52pp above LWM (39.17% → 63.69%)
  + kotlin: L50 hostile ensemble recall +4.02pp above LWM (46.48% → 50.50%)
  + lnk: L50 hostile ensemble recall +12.05pp above LWM (66.73% → 78.78%)
  + lua: L50 hostile ensemble recall +7.69pp above LWM (53.85% → 61.54%)
  + macho: L50 hostile ensemble recall +9.65pp above LWM (68.26% → 77.91%)
  + msi: L50 hostile ensemble recall +6.97pp above LWM (38.34% → 45.31%)
  + ole: L50 hostile ensemble recall +30.02pp above LWM (50.88% → 80.90%)
  + package.json: L50 hostile ensemble recall +7.50pp above LWM (78.39% → 85.89%)
  + pe: L50 hostile ensemble recall +17.11pp above LWM (37.61% → 54.72%)
  + pkg-info: L50 hostile ensemble recall +10.73pp above LWM (65.47% → 76.19%)
  + shell: L50 hostile ensemble recall +30.52pp above LWM (43.91% → 74.43%)
  + vbs: L50 hostile ensemble recall +26.92pp above LWM (42.09% → 69.01%)
  + xls: L50 hostile ensemble recall +3.44pp above LWM (90.97% → 94.40%)
  + xlsx: L50 hostile ensemble recall +1.37pp above LWM (29.09% → 30.46%)
  + zip: L50 hostile ensemble recall +2.12pp above LWM (31.98% → 34.10%)
  + zst: L50 hostile ensemble recall +5.22pp above LWM (8.42% → 13.64%)

1 DEPLOYED-TOLERANCE regression(s) (vs currently-deployed bundle /home/t/.local/share/litmus/models/azoth) — THIS IS WHAT BLOCKS THE DEPLOY:
  - powershell: L50 hostile ENSEMBLE recall dropped 5.08pp (43.38% → 38.31%; tolerance 1.70pp; deployed 95% CI lower = 39.54%)

3 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - perl: L50 hostile ENSEMBLE recall dropped 15.60pp BELOW LOW-WATER-MARK (69.44% → 53.85%; LWM tolerance 0.90pp)
  - php: L50 hostile ENSEMBLE recall dropped 2.17pp BELOW LOW-WATER-MARK (47.03% → 44.86%; LWM tolerance 0.90pp)
  - powershell: L50 hostile ENSEMBLE recall dropped 5.40pp BELOW LOW-WATER-MARK (43.71% → 38.31%; LWM tolerance 0.90pp)

compared 75 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: deployed-tolerance gate (1 filetype(s) regressed vs deployed beyond the 1.70pp tolerance; see list above for the actual drops), low-water-mark gate (3 filetype(s) below LWM beyond the 0.90pp tolerance vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[1]: *** [Makefile:1310: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9970)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `e37f927afbd32e67` | `bcae0f6984fea346` | `664df9c2b3c32ad1` |
| PR AUC | 0.9970 | 0.9986 | 0.9986 |
| ROC AUC | 0.9964 | 0.9983 | 0.9983 |
| F1 | 0.9723 | 0.9833 | 0.9834 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-08T10-26-02_20260608T102600-promote-e37f927afbd32e67_azoth-validate.log; tail:   python :: filegroups/scripts recall@1FP-on-slice +2.35pp (55.47% → 57.82%)
  python :: filetypes/python recall@1FP-on-slice +2.66pp (60.40% → 63.06%)
  ruby :: filegroups/scripts recall@1FP-on-slice +11.76pp (35.29% → 47.06%)
  shell :: filegroups/scripts recall@1FP-on-slice +12.31pp (60.70% → 73.01%)
  shell :: filetypes/shell recall@1FP-on-slice +17.33pp (63.55% → 80.88%)

per-route regressions (informational; does not block deploy):
  php :: filegroups/scripts recall@1FP-on-slice dropped 4.02pp (46.35% → 42.32%)
  powershell :: filetypes/powershell recall@1FP-on-slice dropped 11.69pp (60.15% → 48.46%)

23 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + 7z: L50 hostile ensemble recall +7.60pp above LWM (13.53% → 21.13%)
  + c: L50 hostile ensemble recall +2.07pp above LWM (8.53% → 10.60%)
  + cargo.toml: L50 hostile ensemble recall +22.22pp above LWM (0.00% → 22.22%)
  + crx: L50 hostile ensemble recall +30.51pp above LWM (37.98% → 68.49%)
  + docx: L50 hostile ensemble recall +34.91pp above LWM (44.66% → 79.57%)
  + elf: L50 hostile ensemble recall +4.32pp above LWM (91.77% → 96.09%)
  + jar: L50 hostile ensemble recall +7.42pp above LWM (48.09% → 55.51%)
  + javascript: L50 hostile ensemble recall +24.52pp above LWM (39.17% → 63.69%)
  + kotlin: L50 hostile ensemble recall +4.02pp above LWM (46.48% → 50.50%)
  + lnk: L50 hostile ensemble recall +12.05pp above LWM (66.73% → 78.78%)
  + lua: L50 hostile ensemble recall +7.69pp above LWM (53.85% → 61.54%)
  + macho: L50 hostile ensemble recall +9.65pp above LWM (68.26% → 77.91%)
  + msi: L50 hostile ensemble recall +6.97pp above LWM (38.34% → 45.31%)
  + ole: L50 hostile ensemble recall +30.02pp above LWM (50.88% → 80.90%)
  + package.json: L50 hostile ensemble recall +7.50pp above LWM (78.39% → 85.89%)
  + pe: L50 hostile ensemble recall +17.11pp above LWM (37.61% → 54.72%)
  + pkg-info: L50 hostile ensemble recall +10.73pp above LWM (65.47% → 76.19%)
  + shell: L50 hostile ensemble recall +30.52pp above LWM (43.91% → 74.43%)
  + vbs: L50 hostile ensemble recall +26.92pp above LWM (42.09% → 69.01%)
  + xls: L50 hostile ensemble recall +3.44pp above LWM (90.97% → 94.40%)
  + xlsx: L50 hostile ensemble recall +1.37pp above LWM (29.09% → 30.46%)
  + zip: L50 hostile ensemble recall +2.12pp above LWM (31.98% → 34.10%)
  + zst: L50 hostile ensemble recall +5.22pp above LWM (8.42% → 13.64%)

1 DEPLOYED-TOLERANCE regression(s) (vs currently-deployed bundle /home/t/.local/share/litmus/models/azoth) — THIS IS WHAT BLOCKS THE DEPLOY:
  - powershell: L50 hostile ENSEMBLE recall dropped 5.08pp (43.38% → 38.31%; tolerance 1.70pp; deployed 95% CI lower = 39.54%)

3 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - perl: L50 hostile ENSEMBLE recall dropped 15.60pp BELOW LOW-WATER-MARK (69.44% → 53.85%; LWM tolerance 0.90pp)
  - php: L50 hostile ENSEMBLE recall dropped 2.17pp BELOW LOW-WATER-MARK (47.03% → 44.86%; LWM tolerance 0.90pp)
  - powershell: L50 hostile ENSEMBLE recall dropped 5.40pp BELOW LOW-WATER-MARK (43.71% → 38.31%; LWM tolerance 0.90pp)

compared 75 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: deployed-tolerance gate (1 filetype(s) regressed vs deployed beyond the 1.70pp tolerance; see list above for the actual drops), low-water-mark gate (3 filetype(s) below LWM beyond the 0.90pp tolerance vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[1]: *** [Makefile:1310: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')
