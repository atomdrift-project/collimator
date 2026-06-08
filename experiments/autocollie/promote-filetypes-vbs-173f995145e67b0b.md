# Promote REJECTED — `173f995145e67b0b` on `filetypes/vbs`

Generated 2026-06-08T11:12:28Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-08T11-08-56_20260608T110839-promote-173f995145e67b0b_azoth-validate.log; tail: 2026-06-08 07:12:23,953 INFO filetypes/vbs/models/seed_43.txt -> seed_43.onnx OK (delta=7.80e-08 on 200 rows, 1088 ms)
2026-06-08 07:12:23,998 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-173f995145e67b0b/filetypes/vbs/models/seed_44.onnx
2026-06-08 07:12:24,094 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-08 07:12:24,937 INFO filetypes/vbs/models/seed_44.txt -> seed_44.onnx OK (delta=8.64e-08 on 200 rows, 984 ms)

converted 3/3 files (0 intentionally skipped, 0 failed)
staged runtime azoth bundle: /tmp/tmp.PgLAsOniq6
azoth bundle ok: /tmp/tmp.PgLAsOniq6
--source-bundle out/models/azoth: 1 routes changed → 1 filetypes impacted, 77 unimpacted (drift treated as pre-existing)

per-route regressions (informational; does not block deploy):
  vbs :: filetypes/vbs recall@1FP-on-slice dropped 32.03pp (69.71% → 37.67%)

22 low-water-mark improvement(s) (>0.90pp above LWM, informational):
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
  + package.json: L50 hostile ensemble recall +7.50pp above LWM (78.39% → 85.89%)
  + pe: L50 hostile ensemble recall +17.11pp above LWM (37.61% → 54.72%)
  + pkg-info: L50 hostile ensemble recall +10.73pp above LWM (65.47% → 76.19%)
  + powershell: L50 hostile ensemble recall +9.37pp above LWM (43.71% → 53.08%)
  + shell: L50 hostile ensemble recall +28.14pp above LWM (43.91% → 72.05%)
  + xls: L50 hostile ensemble recall +3.44pp above LWM (90.97% → 94.40%)
  + xlsx: L50 hostile ensemble recall +1.37pp above LWM (29.09% → 30.46%)
  + zip: L50 hostile ensemble recall +2.12pp above LWM (31.98% → 34.10%)
  + zst: L50 hostile ensemble recall +5.22pp above LWM (8.42% → 13.64%)

1 DEPLOYED-TOLERANCE regression(s) (vs currently-deployed bundle /home/t/.local/share/litmus/models/azoth) — THIS IS WHAT BLOCKS THE DEPLOY:
  - vbs: L50 hostile ENSEMBLE recall dropped 35.31pp (69.01% → 33.70%; tolerance 1.70pp; deployed 95% CI lower = 66.55%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - vbs: L50 hostile ENSEMBLE recall dropped 8.38pp BELOW LOW-WATER-MARK (42.09% → 33.70%; LWM tolerance 0.90pp)

compared 75 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: deployed-tolerance gate (1 filetype(s) regressed vs deployed beyond the 1.70pp tolerance; see list above for the actual drops), low-water-mark gate (1 filetype(s) below LWM beyond the 0.90pp tolerance vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[1]: *** [Makefile:1310: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9976)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `173f995145e67b0b` | `a49a77dc8c78b6d6` | `10effe31e2a91c01` |
| PR AUC | 0.9976 | 0.9975 | 0.9976 |
| ROC AUC | 0.9919 | 0.9914 | 0.9918 |
| F1 | 0.9591 | 0.9792 | 0.9638 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-08T11-08-56_20260608T110839-promote-173f995145e67b0b_azoth-validate.log; tail: 2026-06-08 07:12:23,953 INFO filetypes/vbs/models/seed_43.txt -> seed_43.onnx OK (delta=7.80e-08 on 200 rows, 1088 ms)
2026-06-08 07:12:23,998 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-173f995145e67b0b/filetypes/vbs/models/seed_44.onnx
2026-06-08 07:12:24,094 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-08 07:12:24,937 INFO filetypes/vbs/models/seed_44.txt -> seed_44.onnx OK (delta=8.64e-08 on 200 rows, 984 ms)

converted 3/3 files (0 intentionally skipped, 0 failed)
staged runtime azoth bundle: /tmp/tmp.PgLAsOniq6
azoth bundle ok: /tmp/tmp.PgLAsOniq6
--source-bundle out/models/azoth: 1 routes changed → 1 filetypes impacted, 77 unimpacted (drift treated as pre-existing)

per-route regressions (informational; does not block deploy):
  vbs :: filetypes/vbs recall@1FP-on-slice dropped 32.03pp (69.71% → 37.67%)

22 low-water-mark improvement(s) (>0.90pp above LWM, informational):
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
  + package.json: L50 hostile ensemble recall +7.50pp above LWM (78.39% → 85.89%)
  + pe: L50 hostile ensemble recall +17.11pp above LWM (37.61% → 54.72%)
  + pkg-info: L50 hostile ensemble recall +10.73pp above LWM (65.47% → 76.19%)
  + powershell: L50 hostile ensemble recall +9.37pp above LWM (43.71% → 53.08%)
  + shell: L50 hostile ensemble recall +28.14pp above LWM (43.91% → 72.05%)
  + xls: L50 hostile ensemble recall +3.44pp above LWM (90.97% → 94.40%)
  + xlsx: L50 hostile ensemble recall +1.37pp above LWM (29.09% → 30.46%)
  + zip: L50 hostile ensemble recall +2.12pp above LWM (31.98% → 34.10%)
  + zst: L50 hostile ensemble recall +5.22pp above LWM (8.42% → 13.64%)

1 DEPLOYED-TOLERANCE regression(s) (vs currently-deployed bundle /home/t/.local/share/litmus/models/azoth) — THIS IS WHAT BLOCKS THE DEPLOY:
  - vbs: L50 hostile ENSEMBLE recall dropped 35.31pp (69.01% → 33.70%; tolerance 1.70pp; deployed 95% CI lower = 66.55%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - vbs: L50 hostile ENSEMBLE recall dropped 8.38pp BELOW LOW-WATER-MARK (42.09% → 33.70%; LWM tolerance 0.90pp)

compared 75 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: deployed-tolerance gate (1 filetype(s) regressed vs deployed beyond the 1.70pp tolerance; see list above for the actual drops), low-water-mark gate (1 filetype(s) below LWM beyond the 0.90pp tolerance vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[1]: *** [Makefile:1310: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')
