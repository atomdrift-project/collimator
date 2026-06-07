# Promote REJECTED — `a13f4ea43589ee4c` on `filetypes/elf`

Generated 2026-06-07T03:09:05Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-07T03-05-06_20260607T030032-promote-a13f4ea43589ee4c_azoth-validate.log; tail: 2026-06-06 23:08:55,890 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-elf-a13f4ea43589ee4c/filetypes/zip already has seed_42.onnx; skipping
2026-06-06 23:08:55,890 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-elf-a13f4ea43589ee4c/filetypes/zip already has seed_43.onnx; skipping
2026-06-06 23:08:55,890 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-elf-a13f4ea43589ee4c/filetypes/zip already has seed_44.onnx; skipping
2026-06-06 23:08:55,890 INFO found 6 .txt files to convert
2026-06-06 23:08:56,490 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-elf-a13f4ea43589ee4c/filetypes/elf/models/seed_42.onnx
2026-06-06 23:08:57,535 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-06 23:08:58,459 INFO filetypes/elf/models/seed_42.txt -> seed_42.onnx OK (delta=1.12e-07 on 200 rows, 2569 ms)
2026-06-06 23:08:59,015 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-elf-a13f4ea43589ee4c/filetypes/elf/models/seed_43.onnx
2026-06-06 23:09:00,160 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-06 23:09:01,060 INFO filetypes/elf/models/seed_43.txt -> seed_43.onnx OK (delta=1.26e-07 on 200 rows, 2601 ms)
2026-06-06 23:09:01,610 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-elf-a13f4ea43589ee4c/filetypes/elf/models/seed_44.onnx
2026-06-06 23:09:02,682 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-06 23:09:03,593 INFO filetypes/elf/models/seed_44.txt -> seed_44.onnx OK (delta=9.52e-08 on 200 rows, 2532 ms)
2026-06-06 23:09:03,642 INFO skipping ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-elf-a13f4ea43589ee4c/filetypes/json/models/seed_42.onnx: model is a constant predictor (no split learned — trips the TreeEnsembleClassifier 0-split bug)
2026-06-06 23:09:03,642 INFO skipped filetypes/json/models/seed_42.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-elf-a13f4ea43589ee4c/filetypes/json/models/seed_42.txt: constant-predictor model (1 leaf). .txt remains canonical.
2026-06-06 23:09:03,649 INFO skipping ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-elf-a13f4ea43589ee4c/filetypes/json/models/seed_43.onnx: model is a constant predictor (no split learned — trips the TreeEnsembleClassifier 0-split bug)
2026-06-06 23:09:03,649 INFO skipped filetypes/json/models/seed_43.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-elf-a13f4ea43589ee4c/filetypes/json/models/seed_43.txt: constant-predictor model (1 leaf). .txt remains canonical.
2026-06-06 23:09:03,653 INFO skipping ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-elf-a13f4ea43589ee4c/filetypes/json/models/seed_44.onnx: model is a constant predictor (no split learned — trips the TreeEnsembleClassifier 0-split bug)
2026-06-06 23:09:03,653 INFO skipped filetypes/json/models/seed_44.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-elf-a13f4ea43589ee4c/filetypes/json/models/seed_44.txt: constant-predictor model (1 leaf). .txt remains canonical.

converted 3/6 files (3 intentionally skipped, 0 failed)
skipped (3, .txt remains canonical):
  filetypes/json/models/seed_42.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-elf-a13f4ea43589ee4c/filetypes/json/models/seed_42.txt: constant-predictor model (1 leaf). .txt remains canonical.
  filetypes/json/models/seed_43.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-elf-a13f4ea43589ee4c/filetypes/json/models/seed_43.txt: constant-predictor model (1 leaf). .txt remains canonical.
  filetypes/json/models/seed_44.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-elf-a13f4ea43589ee4c/filetypes/json/models/seed_44.txt: constant-predictor model (1 leaf). .txt remains canonical.
staged runtime azoth bundle: /tmp/tmp.9hgM2V7C29
azoth bundle ok: /tmp/tmp.9hgM2V7C29
--source-bundle out/models/azoth: 1 routes changed → 1 filetypes impacted, 77 unimpacted (drift treated as pre-existing)

10 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + csharp: L50 hostile ensemble recall +2.07pp above LWM (19.42% → 21.49%)
  + jar: L50 hostile ensemble recall +38.43pp above LWM (46.97% → 85.39%)
  + javascript: L50 hostile ensemble recall +24.16pp above LWM (37.28% → 61.44%)
  + jpeg: L50 hostile ensemble recall +1.32pp above LWM (11.92% → 13.25%)
  + msi: L50 hostile ensemble recall +19.71pp above LWM (38.34% → 58.05%)
  + pe: L50 hostile ensemble recall +15.22pp above LWM (41.69% → 56.91%)
  + perl: L50 hostile ensemble recall +13.89pp above LWM (69.44% → 83.33%)
  + png: L50 hostile ensemble recall +7.15pp above LWM (0.12% → 7.27%)
  + shell: L50 hostile ensemble recall +19.60pp above LWM (68.11% → 87.71%)
  + xml: L50 hostile ensemble recall +9.67pp above LWM (3.56% → 13.23%)

1 DEPLOYED-TOLERANCE regression(s) (vs currently-deployed bundle /home/t/.local/share/litmus/models/azoth) — THIS IS WHAT BLOCKS THE DEPLOY:
  - elf: L50 hostile ENSEMBLE recall dropped 6.56pp (98.61% → 92.05%; tolerance 1.70pp; deployed 95% CI lower = 98.45%)

compared 75 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: deployed-tolerance gate (1 filetype(s) regressed vs deployed beyond the 1.70pp tolerance; see list above for the actual drops)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1310: azoth-validate] Error 1)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 1.0000)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `a13f4ea43589ee4c` | `c738f38e16634281` | `dd7a1e275ead5312` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 1.0000 | 1.0000 | 1.0000 |
| F1 | 0.9970 | 0.9985 | 0.9990 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-07T03-05-06_20260607T030032-promote-a13f4ea43589ee4c_azoth-validate.log; tail: 2026-06-06 23:08:55,890 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-elf-a13f4ea43589ee4c/filetypes/zip already has seed_42.onnx; skipping
2026-06-06 23:08:55,890 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-elf-a13f4ea43589ee4c/filetypes/zip already has seed_43.onnx; skipping
2026-06-06 23:08:55,890 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-elf-a13f4ea43589ee4c/filetypes/zip already has seed_44.onnx; skipping
2026-06-06 23:08:55,890 INFO found 6 .txt files to convert
2026-06-06 23:08:56,490 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-elf-a13f4ea43589ee4c/filetypes/elf/models/seed_42.onnx
2026-06-06 23:08:57,535 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-06 23:08:58,459 INFO filetypes/elf/models/seed_42.txt -> seed_42.onnx OK (delta=1.12e-07 on 200 rows, 2569 ms)
2026-06-06 23:08:59,015 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-elf-a13f4ea43589ee4c/filetypes/elf/models/seed_43.onnx
2026-06-06 23:09:00,160 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-06 23:09:01,060 INFO filetypes/elf/models/seed_43.txt -> seed_43.onnx OK (delta=1.26e-07 on 200 rows, 2601 ms)
2026-06-06 23:09:01,610 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-elf-a13f4ea43589ee4c/filetypes/elf/models/seed_44.onnx
2026-06-06 23:09:02,682 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-06 23:09:03,593 INFO filetypes/elf/models/seed_44.txt -> seed_44.onnx OK (delta=9.52e-08 on 200 rows, 2532 ms)
2026-06-06 23:09:03,642 INFO skipping ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-elf-a13f4ea43589ee4c/filetypes/json/models/seed_42.onnx: model is a constant predictor (no split learned — trips the TreeEnsembleClassifier 0-split bug)
2026-06-06 23:09:03,642 INFO skipped filetypes/json/models/seed_42.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-elf-a13f4ea43589ee4c/filetypes/json/models/seed_42.txt: constant-predictor model (1 leaf). .txt remains canonical.
2026-06-06 23:09:03,649 INFO skipping ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-elf-a13f4ea43589ee4c/filetypes/json/models/seed_43.onnx: model is a constant predictor (no split learned — trips the TreeEnsembleClassifier 0-split bug)
2026-06-06 23:09:03,649 INFO skipped filetypes/json/models/seed_43.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-elf-a13f4ea43589ee4c/filetypes/json/models/seed_43.txt: constant-predictor model (1 leaf). .txt remains canonical.
2026-06-06 23:09:03,653 INFO skipping ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-elf-a13f4ea43589ee4c/filetypes/json/models/seed_44.onnx: model is a constant predictor (no split learned — trips the TreeEnsembleClassifier 0-split bug)
2026-06-06 23:09:03,653 INFO skipped filetypes/json/models/seed_44.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-elf-a13f4ea43589ee4c/filetypes/json/models/seed_44.txt: constant-predictor model (1 leaf). .txt remains canonical.

converted 3/6 files (3 intentionally skipped, 0 failed)
skipped (3, .txt remains canonical):
  filetypes/json/models/seed_42.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-elf-a13f4ea43589ee4c/filetypes/json/models/seed_42.txt: constant-predictor model (1 leaf). .txt remains canonical.
  filetypes/json/models/seed_43.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-elf-a13f4ea43589ee4c/filetypes/json/models/seed_43.txt: constant-predictor model (1 leaf). .txt remains canonical.
  filetypes/json/models/seed_44.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-elf-a13f4ea43589ee4c/filetypes/json/models/seed_44.txt: constant-predictor model (1 leaf). .txt remains canonical.
staged runtime azoth bundle: /tmp/tmp.9hgM2V7C29
azoth bundle ok: /tmp/tmp.9hgM2V7C29
--source-bundle out/models/azoth: 1 routes changed → 1 filetypes impacted, 77 unimpacted (drift treated as pre-existing)

10 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + csharp: L50 hostile ensemble recall +2.07pp above LWM (19.42% → 21.49%)
  + jar: L50 hostile ensemble recall +38.43pp above LWM (46.97% → 85.39%)
  + javascript: L50 hostile ensemble recall +24.16pp above LWM (37.28% → 61.44%)
  + jpeg: L50 hostile ensemble recall +1.32pp above LWM (11.92% → 13.25%)
  + msi: L50 hostile ensemble recall +19.71pp above LWM (38.34% → 58.05%)
  + pe: L50 hostile ensemble recall +15.22pp above LWM (41.69% → 56.91%)
  + perl: L50 hostile ensemble recall +13.89pp above LWM (69.44% → 83.33%)
  + png: L50 hostile ensemble recall +7.15pp above LWM (0.12% → 7.27%)
  + shell: L50 hostile ensemble recall +19.60pp above LWM (68.11% → 87.71%)
  + xml: L50 hostile ensemble recall +9.67pp above LWM (3.56% → 13.23%)

1 DEPLOYED-TOLERANCE regression(s) (vs currently-deployed bundle /home/t/.local/share/litmus/models/azoth) — THIS IS WHAT BLOCKS THE DEPLOY:
  - elf: L50 hostile ENSEMBLE recall dropped 6.56pp (98.61% → 92.05%; tolerance 1.70pp; deployed 95% CI lower = 98.45%)

compared 75 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: deployed-tolerance gate (1 filetype(s) regressed vs deployed beyond the 1.70pp tolerance; see list above for the actual drops)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1310: azoth-validate] Error 1)
