# Promote REJECTED — `72a917b3a48a6a2a` on `filetypes/vbs`

Generated 2026-06-08T08:47:35Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-08T08-44-16_20260608T084408-promote-72a917b3a48a6a2a_azoth-validate.log; tail: 2026-06-08 04:47:29,343 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-72a917b3a48a6a2a/filetypes/vbs/models/seed_43.onnx
2026-06-08 04:47:29,413 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-08 04:47:30,405 INFO filetypes/vbs/models/seed_43.txt -> seed_43.onnx OK (delta=1.24e-07 on 200 rows, 1162 ms)
2026-06-08 04:47:30,498 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-72a917b3a48a6a2a/filetypes/vbs/models/seed_44.onnx
2026-06-08 04:47:30,570 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-08 04:47:31,464 INFO filetypes/vbs/models/seed_44.txt -> seed_44.onnx OK (delta=8.42e-08 on 200 rows, 1059 ms)

converted 3/3 files (0 intentionally skipped, 0 failed)
staged runtime azoth bundle: /tmp/tmp.TbD6OxEpEo
azoth bundle ok: /tmp/tmp.TbD6OxEpEo
--source-bundle out/models/azoth: 1 routes changed → 1 filetypes impacted, 77 unimpacted (drift treated as pre-existing)

per-route regressions (informational; does not block deploy):
  vbs :: filetypes/vbs recall@1FP-on-slice dropped 11.98pp (69.71% → 57.73%)

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
  + package.json: L50 hostile ensemble recall +7.50pp above LWM (78.39% → 85.89%)
  + pe: L50 hostile ensemble recall +17.11pp above LWM (37.61% → 54.72%)
  + pkg-info: L50 hostile ensemble recall +10.73pp above LWM (65.47% → 76.19%)
  + powershell: L50 hostile ensemble recall +9.37pp above LWM (43.71% → 53.08%)
  + shell: L50 hostile ensemble recall +28.14pp above LWM (43.91% → 72.05%)
  + vbs: L50 hostile ensemble recall +16.06pp above LWM (42.09% → 58.15%)
  + xls: L50 hostile ensemble recall +3.44pp above LWM (90.97% → 94.40%)
  + xlsx: L50 hostile ensemble recall +1.37pp above LWM (29.09% → 30.46%)
  + zip: L50 hostile ensemble recall +2.12pp above LWM (31.98% → 34.10%)
  + zst: L50 hostile ensemble recall +5.22pp above LWM (8.42% → 13.64%)

1 DEPLOYED-TOLERANCE regression(s) (vs currently-deployed bundle /home/t/.local/share/litmus/models/azoth) — THIS IS WHAT BLOCKS THE DEPLOY:
  - vbs: L50 hostile ENSEMBLE recall dropped 10.86pp (69.01% → 58.15%; tolerance 1.70pp; deployed 95% CI lower = 66.55%)

compared 75 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: deployed-tolerance gate (1 filetype(s) regressed vs deployed beyond the 1.70pp tolerance; see list above for the actual drops)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[1]: *** [Makefile:1310: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9978)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `72a917b3a48a6a2a` | `91dbfac33b0c3480` | `defb8785559b94af` |
| PR AUC | 0.9978 | 0.9980 | 0.9979 |
| ROC AUC | 0.9926 | 0.9931 | 0.9928 |
| F1 | 0.9593 | 0.9752 | 0.9769 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-08T08-44-16_20260608T084408-promote-72a917b3a48a6a2a_azoth-validate.log; tail: 2026-06-08 04:47:29,343 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-72a917b3a48a6a2a/filetypes/vbs/models/seed_43.onnx
2026-06-08 04:47:29,413 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-08 04:47:30,405 INFO filetypes/vbs/models/seed_43.txt -> seed_43.onnx OK (delta=1.24e-07 on 200 rows, 1162 ms)
2026-06-08 04:47:30,498 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-72a917b3a48a6a2a/filetypes/vbs/models/seed_44.onnx
2026-06-08 04:47:30,570 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-08 04:47:31,464 INFO filetypes/vbs/models/seed_44.txt -> seed_44.onnx OK (delta=8.42e-08 on 200 rows, 1059 ms)

converted 3/3 files (0 intentionally skipped, 0 failed)
staged runtime azoth bundle: /tmp/tmp.TbD6OxEpEo
azoth bundle ok: /tmp/tmp.TbD6OxEpEo
--source-bundle out/models/azoth: 1 routes changed → 1 filetypes impacted, 77 unimpacted (drift treated as pre-existing)

per-route regressions (informational; does not block deploy):
  vbs :: filetypes/vbs recall@1FP-on-slice dropped 11.98pp (69.71% → 57.73%)

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
  + package.json: L50 hostile ensemble recall +7.50pp above LWM (78.39% → 85.89%)
  + pe: L50 hostile ensemble recall +17.11pp above LWM (37.61% → 54.72%)
  + pkg-info: L50 hostile ensemble recall +10.73pp above LWM (65.47% → 76.19%)
  + powershell: L50 hostile ensemble recall +9.37pp above LWM (43.71% → 53.08%)
  + shell: L50 hostile ensemble recall +28.14pp above LWM (43.91% → 72.05%)
  + vbs: L50 hostile ensemble recall +16.06pp above LWM (42.09% → 58.15%)
  + xls: L50 hostile ensemble recall +3.44pp above LWM (90.97% → 94.40%)
  + xlsx: L50 hostile ensemble recall +1.37pp above LWM (29.09% → 30.46%)
  + zip: L50 hostile ensemble recall +2.12pp above LWM (31.98% → 34.10%)
  + zst: L50 hostile ensemble recall +5.22pp above LWM (8.42% → 13.64%)

1 DEPLOYED-TOLERANCE regression(s) (vs currently-deployed bundle /home/t/.local/share/litmus/models/azoth) — THIS IS WHAT BLOCKS THE DEPLOY:
  - vbs: L50 hostile ENSEMBLE recall dropped 10.86pp (69.01% → 58.15%; tolerance 1.70pp; deployed 95% CI lower = 66.55%)

compared 75 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: deployed-tolerance gate (1 filetype(s) regressed vs deployed beyond the 1.70pp tolerance; see list above for the actual drops)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[1]: *** [Makefile:1310: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')
