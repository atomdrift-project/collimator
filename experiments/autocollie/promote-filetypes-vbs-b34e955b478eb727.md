# Promote REJECTED — `b34e955b478eb727` on `filetypes/vbs`

Generated 2026-06-07T21:14:09Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-07T21-10-35_20260607T211022-promote-b34e955b478eb727_azoth-validate.log; tail: 2026-06-07 17:13:59,275 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-b34e955b478eb727/filetypes/xml already has model.onnx; skipping
2026-06-07 17:13:59,275 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-b34e955b478eb727/filetypes/zip already has model.onnx; skipping
2026-06-07 17:13:59,275 INFO found 3 .txt files to convert
2026-06-07 17:13:59,391 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-b34e955b478eb727/filetypes/vbs/models/seed_42.onnx
2026-06-07 17:13:59,570 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-07 17:14:00,321 INFO filetypes/vbs/models/seed_42.txt -> seed_42.onnx OK (delta=8.90e-08 on 200 rows, 1046 ms)
2026-06-07 17:14:00,392 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-b34e955b478eb727/filetypes/vbs/models/seed_43.onnx
2026-06-07 17:14:00,471 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-07 17:14:01,206 INFO filetypes/vbs/models/seed_43.txt -> seed_43.onnx OK (delta=7.84e-08 on 200 rows, 886 ms)
2026-06-07 17:14:01,279 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-b34e955b478eb727/filetypes/vbs/models/seed_44.onnx
2026-06-07 17:14:01,359 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-07 17:14:02,051 INFO filetypes/vbs/models/seed_44.txt -> seed_44.onnx OK (delta=9.35e-08 on 200 rows, 844 ms)

converted 3/3 files (0 intentionally skipped, 0 failed)
staged runtime azoth bundle: /tmp/tmp.LeOd1PrAjn
azoth bundle ok: /tmp/tmp.LeOd1PrAjn
--source-bundle out/models/azoth: 1 routes changed → 1 filetypes impacted, 77 unimpacted (drift treated as pre-existing)

per-route regressions (informational; does not block deploy):
  vbs :: filetypes/vbs recall@1FP-on-slice dropped 34.54pp (69.71% → 35.17%)

17 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + 7z: L50 hostile ensemble recall +7.60pp above LWM (13.53% → 21.13%)
  + c: L50 hostile ensemble recall +3.31pp above LWM (8.53% → 11.84%)
  + cargo.toml: L50 hostile ensemble recall +22.22pp above LWM (0.00% → 22.22%)
  + doc: L50 hostile ensemble recall +17.59pp above LWM (66.45% → 84.05%)
  + docx: L50 hostile ensemble recall +24.08pp above LWM (44.66% → 68.74%)
  + go: L50 hostile ensemble recall +1.20pp above LWM (4.93% → 6.13%)
  + java_class: L50 hostile ensemble recall +38.66pp above LWM (23.08% → 61.74%)
  + lnk: L50 hostile ensemble recall +12.61pp above LWM (66.73% → 79.34%)
  + macho: L50 hostile ensemble recall +0.99pp above LWM (68.26% → 69.25%)
  + msi: L50 hostile ensemble recall +6.97pp above LWM (38.34% → 45.31%)
  + package.json: L50 hostile ensemble recall +8.83pp above LWM (78.39% → 87.22%)
  + pdf: L50 hostile ensemble recall +1.54pp above LWM (4.25% → 5.79%)
  + pkg-info: L50 hostile ensemble recall +10.73pp above LWM (65.47% → 76.19%)
  + powershell: L50 hostile ensemble recall +9.37pp above LWM (43.71% → 53.08%)
  + ruby: L50 hostile ensemble recall +17.16pp above LWM (41.67% → 58.82%)
  + xls: L50 hostile ensemble recall +3.33pp above LWM (90.97% → 94.30%)
  + zst: L50 hostile ensemble recall +5.22pp above LWM (8.42% → 13.64%)

1 DEPLOYED-TOLERANCE regression(s) (vs currently-deployed bundle /home/t/.local/share/litmus/models/azoth) — THIS IS WHAT BLOCKS THE DEPLOY:
  - vbs: L50 hostile ENSEMBLE recall dropped 27.79pp (69.01% → 41.23%; tolerance 1.70pp; deployed 95% CI lower = 66.55%)

compared 75 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: deployed-tolerance gate (1 filetype(s) regressed vs deployed beyond the 1.70pp tolerance; see list above for the actual drops)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[1]: *** [Makefile:1310: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9977)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `b34e955b478eb727` | `d50dcfca8ffb1647` | `86a70d4163a90f1b` |
| PR AUC | 0.9977 | 0.9975 | 0.9976 |
| ROC AUC | 0.9922 | 0.9916 | 0.9919 |
| F1 | 0.9590 | 0.9786 | 0.9782 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-07T21-10-35_20260607T211022-promote-b34e955b478eb727_azoth-validate.log; tail: 2026-06-07 17:13:59,275 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-b34e955b478eb727/filetypes/xml already has model.onnx; skipping
2026-06-07 17:13:59,275 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-b34e955b478eb727/filetypes/zip already has model.onnx; skipping
2026-06-07 17:13:59,275 INFO found 3 .txt files to convert
2026-06-07 17:13:59,391 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-b34e955b478eb727/filetypes/vbs/models/seed_42.onnx
2026-06-07 17:13:59,570 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-07 17:14:00,321 INFO filetypes/vbs/models/seed_42.txt -> seed_42.onnx OK (delta=8.90e-08 on 200 rows, 1046 ms)
2026-06-07 17:14:00,392 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-b34e955b478eb727/filetypes/vbs/models/seed_43.onnx
2026-06-07 17:14:00,471 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-07 17:14:01,206 INFO filetypes/vbs/models/seed_43.txt -> seed_43.onnx OK (delta=7.84e-08 on 200 rows, 886 ms)
2026-06-07 17:14:01,279 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-b34e955b478eb727/filetypes/vbs/models/seed_44.onnx
2026-06-07 17:14:01,359 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-07 17:14:02,051 INFO filetypes/vbs/models/seed_44.txt -> seed_44.onnx OK (delta=9.35e-08 on 200 rows, 844 ms)

converted 3/3 files (0 intentionally skipped, 0 failed)
staged runtime azoth bundle: /tmp/tmp.LeOd1PrAjn
azoth bundle ok: /tmp/tmp.LeOd1PrAjn
--source-bundle out/models/azoth: 1 routes changed → 1 filetypes impacted, 77 unimpacted (drift treated as pre-existing)

per-route regressions (informational; does not block deploy):
  vbs :: filetypes/vbs recall@1FP-on-slice dropped 34.54pp (69.71% → 35.17%)

17 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + 7z: L50 hostile ensemble recall +7.60pp above LWM (13.53% → 21.13%)
  + c: L50 hostile ensemble recall +3.31pp above LWM (8.53% → 11.84%)
  + cargo.toml: L50 hostile ensemble recall +22.22pp above LWM (0.00% → 22.22%)
  + doc: L50 hostile ensemble recall +17.59pp above LWM (66.45% → 84.05%)
  + docx: L50 hostile ensemble recall +24.08pp above LWM (44.66% → 68.74%)
  + go: L50 hostile ensemble recall +1.20pp above LWM (4.93% → 6.13%)
  + java_class: L50 hostile ensemble recall +38.66pp above LWM (23.08% → 61.74%)
  + lnk: L50 hostile ensemble recall +12.61pp above LWM (66.73% → 79.34%)
  + macho: L50 hostile ensemble recall +0.99pp above LWM (68.26% → 69.25%)
  + msi: L50 hostile ensemble recall +6.97pp above LWM (38.34% → 45.31%)
  + package.json: L50 hostile ensemble recall +8.83pp above LWM (78.39% → 87.22%)
  + pdf: L50 hostile ensemble recall +1.54pp above LWM (4.25% → 5.79%)
  + pkg-info: L50 hostile ensemble recall +10.73pp above LWM (65.47% → 76.19%)
  + powershell: L50 hostile ensemble recall +9.37pp above LWM (43.71% → 53.08%)
  + ruby: L50 hostile ensemble recall +17.16pp above LWM (41.67% → 58.82%)
  + xls: L50 hostile ensemble recall +3.33pp above LWM (90.97% → 94.30%)
  + zst: L50 hostile ensemble recall +5.22pp above LWM (8.42% → 13.64%)

1 DEPLOYED-TOLERANCE regression(s) (vs currently-deployed bundle /home/t/.local/share/litmus/models/azoth) — THIS IS WHAT BLOCKS THE DEPLOY:
  - vbs: L50 hostile ENSEMBLE recall dropped 27.79pp (69.01% → 41.23%; tolerance 1.70pp; deployed 95% CI lower = 66.55%)

compared 75 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: deployed-tolerance gate (1 filetype(s) regressed vs deployed beyond the 1.70pp tolerance; see list above for the actual drops)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[1]: *** [Makefile:1310: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')
