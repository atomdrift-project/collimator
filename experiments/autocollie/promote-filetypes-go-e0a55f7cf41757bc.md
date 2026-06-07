# Promote REJECTED — `e0a55f7cf41757bc` on `filetypes/go`

Generated 2026-06-07T01:08:19Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-07T01-05-17_20260607T010502-promote-e0a55f7cf41757bc_azoth-validate.log; tail: 2026-06-06 21:08:15,074 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-go-e0a55f7cf41757bc/filetypes/zip already has seed_44.onnx; skipping
2026-06-06 21:08:15,074 INFO found 6 .txt files to convert
2026-06-06 21:08:15,246 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-go-e0a55f7cf41757bc/filetypes/go/models/seed_42.onnx
2026-06-06 21:08:15,283 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-06 21:08:15,936 INFO filetypes/go/models/seed_42.txt -> seed_42.onnx OK (delta=1.15e-07 on 200 rows, 862 ms)
2026-06-06 21:08:16,055 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-go-e0a55f7cf41757bc/filetypes/go/models/seed_43.onnx
2026-06-06 21:08:16,066 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-06 21:08:16,720 INFO filetypes/go/models/seed_43.txt -> seed_43.onnx OK (delta=1.22e-07 on 200 rows, 783 ms)
2026-06-06 21:08:16,864 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-go-e0a55f7cf41757bc/filetypes/go/models/seed_44.onnx
2026-06-06 21:08:16,878 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-06 21:08:17,646 INFO filetypes/go/models/seed_44.txt -> seed_44.onnx OK (delta=1.45e-07 on 200 rows, 926 ms)
2026-06-06 21:08:17,655 INFO skipping ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-go-e0a55f7cf41757bc/filetypes/json/models/seed_42.onnx: model is a constant predictor (no split learned — trips the TreeEnsembleClassifier 0-split bug)
2026-06-06 21:08:17,655 INFO skipped filetypes/json/models/seed_42.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-go-e0a55f7cf41757bc/filetypes/json/models/seed_42.txt: constant-predictor model (1 leaf). .txt remains canonical.
2026-06-06 21:08:17,660 INFO skipping ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-go-e0a55f7cf41757bc/filetypes/json/models/seed_43.onnx: model is a constant predictor (no split learned — trips the TreeEnsembleClassifier 0-split bug)
2026-06-06 21:08:17,660 INFO skipped filetypes/json/models/seed_43.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-go-e0a55f7cf41757bc/filetypes/json/models/seed_43.txt: constant-predictor model (1 leaf). .txt remains canonical.
2026-06-06 21:08:17,668 INFO skipping ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-go-e0a55f7cf41757bc/filetypes/json/models/seed_44.onnx: model is a constant predictor (no split learned — trips the TreeEnsembleClassifier 0-split bug)
2026-06-06 21:08:17,668 INFO skipped filetypes/json/models/seed_44.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-go-e0a55f7cf41757bc/filetypes/json/models/seed_44.txt: constant-predictor model (1 leaf). .txt remains canonical.

converted 3/6 files (3 intentionally skipped, 0 failed)
skipped (3, .txt remains canonical):
  filetypes/json/models/seed_42.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-go-e0a55f7cf41757bc/filetypes/json/models/seed_42.txt: constant-predictor model (1 leaf). .txt remains canonical.
  filetypes/json/models/seed_43.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-go-e0a55f7cf41757bc/filetypes/json/models/seed_43.txt: constant-predictor model (1 leaf). .txt remains canonical.
  filetypes/json/models/seed_44.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-go-e0a55f7cf41757bc/filetypes/json/models/seed_44.txt: constant-predictor model (1 leaf). .txt remains canonical.
staged runtime azoth bundle: /tmp/tmp.HIBpu9637l
azoth bundle ok: /tmp/tmp.HIBpu9637l
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
  - go: L50 hostile ENSEMBLE recall dropped 1.29pp BELOW LOW-WATER-MARK (7.27% → 5.98%; LWM tolerance 0.90pp)

compared 75 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: low-water-mark gate (1 filetype(s) below LWM beyond the 0.90pp tolerance vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[1]: *** [Makefile:1310: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9439)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `e0a55f7cf41757bc` | `45ef4487cf204baa` | `27b5a2c92fe79e4d` |
| PR AUC | 0.9439 | 0.9461 | 0.9451 |
| ROC AUC | 0.9862 | 0.9860 | 0.9861 |
| F1 | 0.7228 | 0.8658 | 0.8773 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-07T01-05-17_20260607T010502-promote-e0a55f7cf41757bc_azoth-validate.log; tail: 2026-06-06 21:08:15,074 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-go-e0a55f7cf41757bc/filetypes/zip already has seed_44.onnx; skipping
2026-06-06 21:08:15,074 INFO found 6 .txt files to convert
2026-06-06 21:08:15,246 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-go-e0a55f7cf41757bc/filetypes/go/models/seed_42.onnx
2026-06-06 21:08:15,283 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-06 21:08:15,936 INFO filetypes/go/models/seed_42.txt -> seed_42.onnx OK (delta=1.15e-07 on 200 rows, 862 ms)
2026-06-06 21:08:16,055 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-go-e0a55f7cf41757bc/filetypes/go/models/seed_43.onnx
2026-06-06 21:08:16,066 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-06 21:08:16,720 INFO filetypes/go/models/seed_43.txt -> seed_43.onnx OK (delta=1.22e-07 on 200 rows, 783 ms)
2026-06-06 21:08:16,864 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-go-e0a55f7cf41757bc/filetypes/go/models/seed_44.onnx
2026-06-06 21:08:16,878 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-06 21:08:17,646 INFO filetypes/go/models/seed_44.txt -> seed_44.onnx OK (delta=1.45e-07 on 200 rows, 926 ms)
2026-06-06 21:08:17,655 INFO skipping ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-go-e0a55f7cf41757bc/filetypes/json/models/seed_42.onnx: model is a constant predictor (no split learned — trips the TreeEnsembleClassifier 0-split bug)
2026-06-06 21:08:17,655 INFO skipped filetypes/json/models/seed_42.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-go-e0a55f7cf41757bc/filetypes/json/models/seed_42.txt: constant-predictor model (1 leaf). .txt remains canonical.
2026-06-06 21:08:17,660 INFO skipping ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-go-e0a55f7cf41757bc/filetypes/json/models/seed_43.onnx: model is a constant predictor (no split learned — trips the TreeEnsembleClassifier 0-split bug)
2026-06-06 21:08:17,660 INFO skipped filetypes/json/models/seed_43.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-go-e0a55f7cf41757bc/filetypes/json/models/seed_43.txt: constant-predictor model (1 leaf). .txt remains canonical.
2026-06-06 21:08:17,668 INFO skipping ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-go-e0a55f7cf41757bc/filetypes/json/models/seed_44.onnx: model is a constant predictor (no split learned — trips the TreeEnsembleClassifier 0-split bug)
2026-06-06 21:08:17,668 INFO skipped filetypes/json/models/seed_44.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-go-e0a55f7cf41757bc/filetypes/json/models/seed_44.txt: constant-predictor model (1 leaf). .txt remains canonical.

converted 3/6 files (3 intentionally skipped, 0 failed)
skipped (3, .txt remains canonical):
  filetypes/json/models/seed_42.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-go-e0a55f7cf41757bc/filetypes/json/models/seed_42.txt: constant-predictor model (1 leaf). .txt remains canonical.
  filetypes/json/models/seed_43.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-go-e0a55f7cf41757bc/filetypes/json/models/seed_43.txt: constant-predictor model (1 leaf). .txt remains canonical.
  filetypes/json/models/seed_44.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-go-e0a55f7cf41757bc/filetypes/json/models/seed_44.txt: constant-predictor model (1 leaf). .txt remains canonical.
staged runtime azoth bundle: /tmp/tmp.HIBpu9637l
azoth bundle ok: /tmp/tmp.HIBpu9637l
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
  - go: L50 hostile ENSEMBLE recall dropped 1.29pp BELOW LOW-WATER-MARK (7.27% → 5.98%; LWM tolerance 0.90pp)

compared 75 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: low-water-mark gate (1 filetype(s) below LWM beyond the 0.90pp tolerance vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[1]: *** [Makefile:1310: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')
