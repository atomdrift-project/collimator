# Promote REJECTED — `07066c4d765de183` on `filetypes/php`

Generated 2026-06-08T11:37:25Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-08T11-34-07_20260608T113406-promote-07066c4d765de183_azoth-validate.log; tail: 2026-06-08 07:37:17,622 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-php-07066c4d765de183/filetypes/php/models/seed_42.onnx
2026-06-08 07:37:18,110 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-08 07:37:18,958 INFO filetypes/php/models/seed_42.txt -> seed_42.onnx OK (delta=1.19e-07 on 200 rows, 1533 ms)
2026-06-08 07:37:19,104 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-php-07066c4d765de183/filetypes/php/models/seed_43.onnx
2026-06-08 07:37:19,542 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-08 07:37:20,357 INFO filetypes/php/models/seed_43.txt -> seed_43.onnx OK (delta=2.07e-07 on 200 rows, 1399 ms)
2026-06-08 07:37:20,603 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-php-07066c4d765de183/filetypes/php/models/seed_44.onnx
2026-06-08 07:37:21,085 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-08 07:37:21,846 INFO filetypes/php/models/seed_44.txt -> seed_44.onnx OK (delta=8.75e-08 on 200 rows, 1489 ms)

converted 3/3 files (0 intentionally skipped, 0 failed)
staged runtime azoth bundle: /tmp/tmp.tIqWkkg6IC
azoth bundle ok: /tmp/tmp.tIqWkkg6IC
--source-bundle out/models/azoth: 1 routes changed → 1 filetypes impacted, 77 unimpacted (drift treated as pre-existing)

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
  + vbs: L50 hostile ensemble recall +26.92pp above LWM (42.09% → 69.01%)
  + xls: L50 hostile ensemble recall +3.44pp above LWM (90.97% → 94.40%)
  + xlsx: L50 hostile ensemble recall +1.37pp above LWM (29.09% → 30.46%)
  + zip: L50 hostile ensemble recall +2.12pp above LWM (31.98% → 34.10%)
  + zst: L50 hostile ensemble recall +5.22pp above LWM (8.42% → 13.64%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - php: L50 hostile ENSEMBLE recall dropped 3.66pp BELOW LOW-WATER-MARK (47.03% → 43.37%; LWM tolerance 0.90pp)

compared 75 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: low-water-mark gate (1 filetype(s) below LWM beyond the 0.90pp tolerance vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[1]: *** [Makefile:1310: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9942)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `07066c4d765de183` | `6f902d0d6793a9c0` | `f77fa1e95d9ff4db` |
| PR AUC | 0.9942 | 0.9945 | 0.9945 |
| ROC AUC | 0.9969 | 0.9971 | 0.9971 |
| F1 | 0.9582 | 0.9773 | 0.9773 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-08T11-34-07_20260608T113406-promote-07066c4d765de183_azoth-validate.log; tail: 2026-06-08 07:37:17,622 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-php-07066c4d765de183/filetypes/php/models/seed_42.onnx
2026-06-08 07:37:18,110 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-08 07:37:18,958 INFO filetypes/php/models/seed_42.txt -> seed_42.onnx OK (delta=1.19e-07 on 200 rows, 1533 ms)
2026-06-08 07:37:19,104 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-php-07066c4d765de183/filetypes/php/models/seed_43.onnx
2026-06-08 07:37:19,542 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-08 07:37:20,357 INFO filetypes/php/models/seed_43.txt -> seed_43.onnx OK (delta=2.07e-07 on 200 rows, 1399 ms)
2026-06-08 07:37:20,603 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-php-07066c4d765de183/filetypes/php/models/seed_44.onnx
2026-06-08 07:37:21,085 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-08 07:37:21,846 INFO filetypes/php/models/seed_44.txt -> seed_44.onnx OK (delta=8.75e-08 on 200 rows, 1489 ms)

converted 3/3 files (0 intentionally skipped, 0 failed)
staged runtime azoth bundle: /tmp/tmp.tIqWkkg6IC
azoth bundle ok: /tmp/tmp.tIqWkkg6IC
--source-bundle out/models/azoth: 1 routes changed → 1 filetypes impacted, 77 unimpacted (drift treated as pre-existing)

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
  + vbs: L50 hostile ensemble recall +26.92pp above LWM (42.09% → 69.01%)
  + xls: L50 hostile ensemble recall +3.44pp above LWM (90.97% → 94.40%)
  + xlsx: L50 hostile ensemble recall +1.37pp above LWM (29.09% → 30.46%)
  + zip: L50 hostile ensemble recall +2.12pp above LWM (31.98% → 34.10%)
  + zst: L50 hostile ensemble recall +5.22pp above LWM (8.42% → 13.64%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - php: L50 hostile ENSEMBLE recall dropped 3.66pp BELOW LOW-WATER-MARK (47.03% → 43.37%; LWM tolerance 0.90pp)

compared 75 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: low-water-mark gate (1 filetype(s) below LWM beyond the 0.90pp tolerance vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[1]: *** [Makefile:1310: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')
