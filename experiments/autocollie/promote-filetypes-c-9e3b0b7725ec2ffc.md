# Promote REJECTED — `9e3b0b7725ec2ffc` on `filetypes/c`

Generated 2026-06-07T01:04:36Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-07T01-00-42_20260607T010041-promote-9e3b0b7725ec2ffc_azoth-validate.log; tail: 2026-06-06 21:04:30,584 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-c-9e3b0b7725ec2ffc/filetypes/zip already has seed_44.onnx; skipping
2026-06-06 21:04:30,584 INFO found 6 .txt files to convert
2026-06-06 21:04:30,860 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-c-9e3b0b7725ec2ffc/filetypes/c/models/seed_42.onnx
2026-06-06 21:04:30,937 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-06 21:04:31,735 INFO filetypes/c/models/seed_42.txt -> seed_42.onnx OK (delta=8.64e-08 on 200 rows, 1151 ms)
2026-06-06 21:04:31,932 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-c-9e3b0b7725ec2ffc/filetypes/c/models/seed_43.onnx
2026-06-06 21:04:31,983 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-06 21:04:32,743 INFO filetypes/c/models/seed_43.txt -> seed_43.onnx OK (delta=1.05e-07 on 200 rows, 1008 ms)
2026-06-06 21:04:32,998 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-c-9e3b0b7725ec2ffc/filetypes/c/models/seed_44.onnx
2026-06-06 21:04:33,047 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-06 21:04:33,793 INFO filetypes/c/models/seed_44.txt -> seed_44.onnx OK (delta=9.28e-08 on 200 rows, 1050 ms)
2026-06-06 21:04:33,798 INFO skipping ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-c-9e3b0b7725ec2ffc/filetypes/json/models/seed_42.onnx: model is a constant predictor (no split learned — trips the TreeEnsembleClassifier 0-split bug)
2026-06-06 21:04:33,798 INFO skipped filetypes/json/models/seed_42.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-c-9e3b0b7725ec2ffc/filetypes/json/models/seed_42.txt: constant-predictor model (1 leaf). .txt remains canonical.
2026-06-06 21:04:33,806 INFO skipping ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-c-9e3b0b7725ec2ffc/filetypes/json/models/seed_43.onnx: model is a constant predictor (no split learned — trips the TreeEnsembleClassifier 0-split bug)
2026-06-06 21:04:33,806 INFO skipped filetypes/json/models/seed_43.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-c-9e3b0b7725ec2ffc/filetypes/json/models/seed_43.txt: constant-predictor model (1 leaf). .txt remains canonical.
2026-06-06 21:04:33,816 INFO skipping ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-c-9e3b0b7725ec2ffc/filetypes/json/models/seed_44.onnx: model is a constant predictor (no split learned — trips the TreeEnsembleClassifier 0-split bug)
2026-06-06 21:04:33,816 INFO skipped filetypes/json/models/seed_44.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-c-9e3b0b7725ec2ffc/filetypes/json/models/seed_44.txt: constant-predictor model (1 leaf). .txt remains canonical.

converted 3/6 files (3 intentionally skipped, 0 failed)
skipped (3, .txt remains canonical):
  filetypes/json/models/seed_42.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-c-9e3b0b7725ec2ffc/filetypes/json/models/seed_42.txt: constant-predictor model (1 leaf). .txt remains canonical.
  filetypes/json/models/seed_43.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-c-9e3b0b7725ec2ffc/filetypes/json/models/seed_43.txt: constant-predictor model (1 leaf). .txt remains canonical.
  filetypes/json/models/seed_44.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-c-9e3b0b7725ec2ffc/filetypes/json/models/seed_44.txt: constant-predictor model (1 leaf). .txt remains canonical.
staged runtime azoth bundle: /tmp/tmp.1jH4BVWQwe
azoth bundle ok: /tmp/tmp.1jH4BVWQwe
--source-bundle out/models/azoth: 1 routes changed → 1 filetypes impacted, 77 unimpacted (drift treated as pre-existing)

11 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + csharp: L50 hostile ensemble recall +2.07pp above LWM (19.42% → 21.49%)
  + elf: L50 hostile ensemble recall +5.96pp above LWM (92.64% → 98.61%)
  + jar: L50 hostile ensemble recall +38.43pp above LWM (46.97% → 85.39%)
  + javascript: L50 hostile ensemble recall +24.16pp above LWM (37.28% → 61.44%)
  + jpeg: L50 hostile ensemble recall +1.32pp above LWM (11.92% → 13.25%)
  + msi: L50 hostile ensemble recall +19.71pp above LWM (38.34% → 58.05%)
  + pe: L50 hostile ensemble recall +15.22pp above LWM (41.69% → 56.91%)
  + perl: L50 hostile ensemble recall +13.89pp above LWM (69.44% → 83.33%)
  + png: L50 hostile ensemble recall +7.15pp above LWM (0.12% → 7.27%)
  + shell: L50 hostile ensemble recall +19.60pp above LWM (68.11% → 87.71%)
  + xml: L50 hostile ensemble recall +9.67pp above LWM (3.56% → 13.23%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - c: L50 hostile ENSEMBLE recall dropped 5.47pp BELOW LOW-WATER-MARK (13.33% → 7.86%; LWM tolerance 0.90pp)

compared 75 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: low-water-mark gate (1 filetype(s) below LWM beyond the 0.90pp tolerance vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[1]: *** [Makefile:1310: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9884)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `9e3b0b7725ec2ffc` | `39b8f3f53b882790` | `dbaaac4fa24f8645` |
| PR AUC | 0.9884 | 0.9889 | 0.9890 |
| ROC AUC | 0.9951 | 0.9951 | 0.9953 |
| F1 | 0.9446 | 0.9474 | 0.9476 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-07T01-00-42_20260607T010041-promote-9e3b0b7725ec2ffc_azoth-validate.log; tail: 2026-06-06 21:04:30,584 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-c-9e3b0b7725ec2ffc/filetypes/zip already has seed_44.onnx; skipping
2026-06-06 21:04:30,584 INFO found 6 .txt files to convert
2026-06-06 21:04:30,860 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-c-9e3b0b7725ec2ffc/filetypes/c/models/seed_42.onnx
2026-06-06 21:04:30,937 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-06 21:04:31,735 INFO filetypes/c/models/seed_42.txt -> seed_42.onnx OK (delta=8.64e-08 on 200 rows, 1151 ms)
2026-06-06 21:04:31,932 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-c-9e3b0b7725ec2ffc/filetypes/c/models/seed_43.onnx
2026-06-06 21:04:31,983 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-06 21:04:32,743 INFO filetypes/c/models/seed_43.txt -> seed_43.onnx OK (delta=1.05e-07 on 200 rows, 1008 ms)
2026-06-06 21:04:32,998 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-c-9e3b0b7725ec2ffc/filetypes/c/models/seed_44.onnx
2026-06-06 21:04:33,047 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-06 21:04:33,793 INFO filetypes/c/models/seed_44.txt -> seed_44.onnx OK (delta=9.28e-08 on 200 rows, 1050 ms)
2026-06-06 21:04:33,798 INFO skipping ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-c-9e3b0b7725ec2ffc/filetypes/json/models/seed_42.onnx: model is a constant predictor (no split learned — trips the TreeEnsembleClassifier 0-split bug)
2026-06-06 21:04:33,798 INFO skipped filetypes/json/models/seed_42.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-c-9e3b0b7725ec2ffc/filetypes/json/models/seed_42.txt: constant-predictor model (1 leaf). .txt remains canonical.
2026-06-06 21:04:33,806 INFO skipping ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-c-9e3b0b7725ec2ffc/filetypes/json/models/seed_43.onnx: model is a constant predictor (no split learned — trips the TreeEnsembleClassifier 0-split bug)
2026-06-06 21:04:33,806 INFO skipped filetypes/json/models/seed_43.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-c-9e3b0b7725ec2ffc/filetypes/json/models/seed_43.txt: constant-predictor model (1 leaf). .txt remains canonical.
2026-06-06 21:04:33,816 INFO skipping ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-c-9e3b0b7725ec2ffc/filetypes/json/models/seed_44.onnx: model is a constant predictor (no split learned — trips the TreeEnsembleClassifier 0-split bug)
2026-06-06 21:04:33,816 INFO skipped filetypes/json/models/seed_44.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-c-9e3b0b7725ec2ffc/filetypes/json/models/seed_44.txt: constant-predictor model (1 leaf). .txt remains canonical.

converted 3/6 files (3 intentionally skipped, 0 failed)
skipped (3, .txt remains canonical):
  filetypes/json/models/seed_42.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-c-9e3b0b7725ec2ffc/filetypes/json/models/seed_42.txt: constant-predictor model (1 leaf). .txt remains canonical.
  filetypes/json/models/seed_43.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-c-9e3b0b7725ec2ffc/filetypes/json/models/seed_43.txt: constant-predictor model (1 leaf). .txt remains canonical.
  filetypes/json/models/seed_44.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-c-9e3b0b7725ec2ffc/filetypes/json/models/seed_44.txt: constant-predictor model (1 leaf). .txt remains canonical.
staged runtime azoth bundle: /tmp/tmp.1jH4BVWQwe
azoth bundle ok: /tmp/tmp.1jH4BVWQwe
--source-bundle out/models/azoth: 1 routes changed → 1 filetypes impacted, 77 unimpacted (drift treated as pre-existing)

11 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + csharp: L50 hostile ensemble recall +2.07pp above LWM (19.42% → 21.49%)
  + elf: L50 hostile ensemble recall +5.96pp above LWM (92.64% → 98.61%)
  + jar: L50 hostile ensemble recall +38.43pp above LWM (46.97% → 85.39%)
  + javascript: L50 hostile ensemble recall +24.16pp above LWM (37.28% → 61.44%)
  + jpeg: L50 hostile ensemble recall +1.32pp above LWM (11.92% → 13.25%)
  + msi: L50 hostile ensemble recall +19.71pp above LWM (38.34% → 58.05%)
  + pe: L50 hostile ensemble recall +15.22pp above LWM (41.69% → 56.91%)
  + perl: L50 hostile ensemble recall +13.89pp above LWM (69.44% → 83.33%)
  + png: L50 hostile ensemble recall +7.15pp above LWM (0.12% → 7.27%)
  + shell: L50 hostile ensemble recall +19.60pp above LWM (68.11% → 87.71%)
  + xml: L50 hostile ensemble recall +9.67pp above LWM (3.56% → 13.23%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - c: L50 hostile ENSEMBLE recall dropped 5.47pp BELOW LOW-WATER-MARK (13.33% → 7.86%; LWM tolerance 0.90pp)

compared 75 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: low-water-mark gate (1 filetype(s) below LWM beyond the 0.90pp tolerance vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[1]: *** [Makefile:1310: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')
