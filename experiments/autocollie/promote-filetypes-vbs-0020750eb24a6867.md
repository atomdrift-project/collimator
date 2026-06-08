# Promote REJECTED — `0020750eb24a6867` on `filetypes/vbs`

Generated 2026-06-08T02:29:40Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-08T02-25-40_20260608T022523-promote-0020750eb24a6867_azoth-validate.log; tail: 2026-06-07 22:29:33,137 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-0020750eb24a6867/filetypes/zip already has seed_42.onnx; skipping
2026-06-07 22:29:33,137 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-0020750eb24a6867/filetypes/zip already has seed_43.onnx; skipping
2026-06-07 22:29:33,137 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-0020750eb24a6867/filetypes/zip already has seed_44.onnx; skipping
2026-06-07 22:29:33,137 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-0020750eb24a6867/filetypes/zst already has seed_42.onnx; skipping
2026-06-07 22:29:33,137 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-0020750eb24a6867/filetypes/zst already has seed_43.onnx; skipping
2026-06-07 22:29:33,137 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-0020750eb24a6867/filetypes/zst already has seed_44.onnx; skipping
2026-06-07 22:29:33,137 INFO found 3 .txt files to convert
2026-06-07 22:29:33,263 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-0020750eb24a6867/filetypes/vbs/models/seed_42.onnx
2026-06-07 22:29:33,351 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-07 22:29:34,204 INFO filetypes/vbs/models/seed_42.txt -> seed_42.onnx OK (delta=8.90e-08 on 200 rows, 1066 ms)
2026-06-07 22:29:34,284 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-0020750eb24a6867/filetypes/vbs/models/seed_43.onnx
2026-06-07 22:29:34,346 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-07 22:29:35,210 INFO filetypes/vbs/models/seed_43.txt -> seed_43.onnx OK (delta=7.84e-08 on 200 rows, 1006 ms)
2026-06-07 22:29:35,288 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-0020750eb24a6867/filetypes/vbs/models/seed_44.onnx
2026-06-07 22:29:35,348 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-07 22:29:36,121 INFO filetypes/vbs/models/seed_44.txt -> seed_44.onnx OK (delta=9.35e-08 on 200 rows, 911 ms)

converted 3/3 files (0 intentionally skipped, 0 failed)
staged runtime azoth bundle: /tmp/tmp.kekxvOdSiM
azoth bundle ok: /tmp/tmp.kekxvOdSiM
--source-bundle out/models/azoth: 1 routes changed → 1 filetypes impacted, 77 unimpacted (drift treated as pre-existing)

per-route regressions (informational; does not block deploy):
  vbs :: filetypes/vbs recall@1FP-on-slice dropped 34.54pp (69.71% → 35.17%)

13 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + 7z: L50 hostile ensemble recall +7.60pp above LWM (13.53% → 21.13%)
  + c: L50 hostile ensemble recall +2.07pp above LWM (8.53% → 10.60%)
  + cargo.toml: L50 hostile ensemble recall +22.22pp above LWM (0.00% → 22.22%)
  + crx: L50 hostile ensemble recall +30.51pp above LWM (37.98% → 68.49%)
  + docx: L50 hostile ensemble recall +7.20pp above LWM (44.66% → 51.87%)
  + kotlin: L50 hostile ensemble recall +4.02pp above LWM (46.48% → 50.50%)
  + lnk: L50 hostile ensemble recall +10.76pp above LWM (66.73% → 77.49%)
  + macho: L50 hostile ensemble recall +0.99pp above LWM (68.26% → 69.25%)
  + msi: L50 hostile ensemble recall +6.97pp above LWM (38.34% → 45.31%)
  + ole: L50 hostile ensemble recall +30.02pp above LWM (50.88% → 80.90%)
  + package.json: L50 hostile ensemble recall +8.83pp above LWM (78.39% → 87.22%)
  + pkg-info: L50 hostile ensemble recall +10.73pp above LWM (65.47% → 76.19%)
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
| key | `0020750eb24a6867` | `801bdc9ae17238d4` | `e05f11f0820cc900` |
| PR AUC | 0.9977 | 0.9975 | 0.9976 |
| ROC AUC | 0.9922 | 0.9916 | 0.9919 |
| F1 | 0.9590 | 0.9786 | 0.9782 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-08T02-25-40_20260608T022523-promote-0020750eb24a6867_azoth-validate.log; tail: 2026-06-07 22:29:33,137 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-0020750eb24a6867/filetypes/zip already has seed_42.onnx; skipping
2026-06-07 22:29:33,137 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-0020750eb24a6867/filetypes/zip already has seed_43.onnx; skipping
2026-06-07 22:29:33,137 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-0020750eb24a6867/filetypes/zip already has seed_44.onnx; skipping
2026-06-07 22:29:33,137 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-0020750eb24a6867/filetypes/zst already has seed_42.onnx; skipping
2026-06-07 22:29:33,137 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-0020750eb24a6867/filetypes/zst already has seed_43.onnx; skipping
2026-06-07 22:29:33,137 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-0020750eb24a6867/filetypes/zst already has seed_44.onnx; skipping
2026-06-07 22:29:33,137 INFO found 3 .txt files to convert
2026-06-07 22:29:33,263 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-0020750eb24a6867/filetypes/vbs/models/seed_42.onnx
2026-06-07 22:29:33,351 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-07 22:29:34,204 INFO filetypes/vbs/models/seed_42.txt -> seed_42.onnx OK (delta=8.90e-08 on 200 rows, 1066 ms)
2026-06-07 22:29:34,284 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-0020750eb24a6867/filetypes/vbs/models/seed_43.onnx
2026-06-07 22:29:34,346 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-07 22:29:35,210 INFO filetypes/vbs/models/seed_43.txt -> seed_43.onnx OK (delta=7.84e-08 on 200 rows, 1006 ms)
2026-06-07 22:29:35,288 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-0020750eb24a6867/filetypes/vbs/models/seed_44.onnx
2026-06-07 22:29:35,348 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-07 22:29:36,121 INFO filetypes/vbs/models/seed_44.txt -> seed_44.onnx OK (delta=9.35e-08 on 200 rows, 911 ms)

converted 3/3 files (0 intentionally skipped, 0 failed)
staged runtime azoth bundle: /tmp/tmp.kekxvOdSiM
azoth bundle ok: /tmp/tmp.kekxvOdSiM
--source-bundle out/models/azoth: 1 routes changed → 1 filetypes impacted, 77 unimpacted (drift treated as pre-existing)

per-route regressions (informational; does not block deploy):
  vbs :: filetypes/vbs recall@1FP-on-slice dropped 34.54pp (69.71% → 35.17%)

13 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + 7z: L50 hostile ensemble recall +7.60pp above LWM (13.53% → 21.13%)
  + c: L50 hostile ensemble recall +2.07pp above LWM (8.53% → 10.60%)
  + cargo.toml: L50 hostile ensemble recall +22.22pp above LWM (0.00% → 22.22%)
  + crx: L50 hostile ensemble recall +30.51pp above LWM (37.98% → 68.49%)
  + docx: L50 hostile ensemble recall +7.20pp above LWM (44.66% → 51.87%)
  + kotlin: L50 hostile ensemble recall +4.02pp above LWM (46.48% → 50.50%)
  + lnk: L50 hostile ensemble recall +10.76pp above LWM (66.73% → 77.49%)
  + macho: L50 hostile ensemble recall +0.99pp above LWM (68.26% → 69.25%)
  + msi: L50 hostile ensemble recall +6.97pp above LWM (38.34% → 45.31%)
  + ole: L50 hostile ensemble recall +30.02pp above LWM (50.88% → 80.90%)
  + package.json: L50 hostile ensemble recall +8.83pp above LWM (78.39% → 87.22%)
  + pkg-info: L50 hostile ensemble recall +10.73pp above LWM (65.47% → 76.19%)
  + zst: L50 hostile ensemble recall +5.22pp above LWM (8.42% → 13.64%)

1 DEPLOYED-TOLERANCE regression(s) (vs currently-deployed bundle /home/t/.local/share/litmus/models/azoth) — THIS IS WHAT BLOCKS THE DEPLOY:
  - vbs: L50 hostile ENSEMBLE recall dropped 27.79pp (69.01% → 41.23%; tolerance 1.70pp; deployed 95% CI lower = 66.55%)

compared 75 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: deployed-tolerance gate (1 filetype(s) regressed vs deployed beyond the 1.70pp tolerance; see list above for the actual drops)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[1]: *** [Makefile:1310: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')
