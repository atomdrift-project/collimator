# Promote REJECTED — `31323f3534358eee` on `filetypes/csharp`

Generated 2026-06-08T12:06:55Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-08T12-03-30_20260608T120324-promote-31323f3534358eee_azoth-validate.log; tail: 2026-06-08 08:06:48,711 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-csharp-31323f3534358eee/filetypes/csharp/models/seed_43.onnx
2026-06-08 08:06:49,501 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-08 08:06:50,216 INFO filetypes/csharp/models/seed_43.txt -> seed_43.onnx OK (delta=1.13e-07 on 200 rows, 1544 ms)
2026-06-08 08:06:50,263 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-csharp-31323f3534358eee/filetypes/csharp/models/seed_44.onnx
2026-06-08 08:06:50,996 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-08 08:06:51,778 INFO filetypes/csharp/models/seed_44.txt -> seed_44.onnx OK (delta=1.09e-07 on 200 rows, 1562 ms)

converted 3/3 files (0 intentionally skipped, 0 failed)
staged runtime azoth bundle: /tmp/tmp.2BB04xhXM9
azoth bundle ok: /tmp/tmp.2BB04xhXM9
--source-bundle out/models/azoth: 1 routes changed → 1 filetypes impacted, 77 unimpacted (drift treated as pre-existing)

per-route improvements (≥0.10pp, informational):
  csharp :: filetypes/csharp recall@1FP-on-slice +7.91pp (21.20% → 29.11%)

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
  - csharp: L50 hostile ENSEMBLE recall dropped 9.16pp BELOW LOW-WATER-MARK (25.62% → 16.46%; LWM tolerance 0.90pp)

compared 75 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: low-water-mark gate (1 filetype(s) below LWM beyond the 0.90pp tolerance vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[1]: *** [Makefile:1312: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9903)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `31323f3534358eee` | `d4d3131a89872a1e` | `ad7013b5cd05181c` |
| PR AUC | 0.9903 | 0.9896 | 0.9905 |
| ROC AUC | 0.9933 | 0.9932 | 0.9938 |
| F1 | 0.9556 | 0.9565 | 0.9617 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-08T12-03-30_20260608T120324-promote-31323f3534358eee_azoth-validate.log; tail: 2026-06-08 08:06:48,711 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-csharp-31323f3534358eee/filetypes/csharp/models/seed_43.onnx
2026-06-08 08:06:49,501 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-08 08:06:50,216 INFO filetypes/csharp/models/seed_43.txt -> seed_43.onnx OK (delta=1.13e-07 on 200 rows, 1544 ms)
2026-06-08 08:06:50,263 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-csharp-31323f3534358eee/filetypes/csharp/models/seed_44.onnx
2026-06-08 08:06:50,996 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-08 08:06:51,778 INFO filetypes/csharp/models/seed_44.txt -> seed_44.onnx OK (delta=1.09e-07 on 200 rows, 1562 ms)

converted 3/3 files (0 intentionally skipped, 0 failed)
staged runtime azoth bundle: /tmp/tmp.2BB04xhXM9
azoth bundle ok: /tmp/tmp.2BB04xhXM9
--source-bundle out/models/azoth: 1 routes changed → 1 filetypes impacted, 77 unimpacted (drift treated as pre-existing)

per-route improvements (≥0.10pp, informational):
  csharp :: filetypes/csharp recall@1FP-on-slice +7.91pp (21.20% → 29.11%)

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
  - csharp: L50 hostile ENSEMBLE recall dropped 9.16pp BELOW LOW-WATER-MARK (25.62% → 16.46%; LWM tolerance 0.90pp)

compared 75 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: low-water-mark gate (1 filetype(s) below LWM beyond the 0.90pp tolerance vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[1]: *** [Makefile:1312: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')
