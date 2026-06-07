# Promote REJECTED — `d1cb1aa0c51d40bf` on `filetypes/elf`

Generated 2026-06-07T02:56:18Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-07T02-52-06_20260607T024542-promote-d1cb1aa0c51d40bf_azoth-validate.log; tail: 2026-06-06 22:56:08,788 INFO found 6 .txt files to convert
2026-06-06 22:56:09,391 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-elf-d1cb1aa0c51d40bf/filetypes/elf/models/seed_42.onnx
2026-06-06 22:56:10,388 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-06 22:56:11,199 INFO filetypes/elf/models/seed_42.txt -> seed_42.onnx OK (delta=1.36e-07 on 200 rows, 2411 ms)
2026-06-06 22:56:11,761 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-elf-d1cb1aa0c51d40bf/filetypes/elf/models/seed_43.onnx
2026-06-06 22:56:12,738 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-06 22:56:13,880 INFO filetypes/elf/models/seed_43.txt -> seed_43.onnx OK (delta=1.33e-07 on 200 rows, 2681 ms)
2026-06-06 22:56:14,639 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-elf-d1cb1aa0c51d40bf/filetypes/elf/models/seed_44.onnx
2026-06-06 22:56:15,668 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-06 22:56:16,483 INFO filetypes/elf/models/seed_44.txt -> seed_44.onnx OK (delta=1.64e-07 on 200 rows, 2602 ms)
2026-06-06 22:56:16,492 INFO skipping ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-elf-d1cb1aa0c51d40bf/filetypes/json/models/seed_42.onnx: model is a constant predictor (no split learned — trips the TreeEnsembleClassifier 0-split bug)
2026-06-06 22:56:16,493 INFO skipped filetypes/json/models/seed_42.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-elf-d1cb1aa0c51d40bf/filetypes/json/models/seed_42.txt: constant-predictor model (1 leaf). .txt remains canonical.
2026-06-06 22:56:16,499 INFO skipping ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-elf-d1cb1aa0c51d40bf/filetypes/json/models/seed_43.onnx: model is a constant predictor (no split learned — trips the TreeEnsembleClassifier 0-split bug)
2026-06-06 22:56:16,499 INFO skipped filetypes/json/models/seed_43.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-elf-d1cb1aa0c51d40bf/filetypes/json/models/seed_43.txt: constant-predictor model (1 leaf). .txt remains canonical.
2026-06-06 22:56:16,504 INFO skipping ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-elf-d1cb1aa0c51d40bf/filetypes/json/models/seed_44.onnx: model is a constant predictor (no split learned — trips the TreeEnsembleClassifier 0-split bug)
2026-06-06 22:56:16,504 INFO skipped filetypes/json/models/seed_44.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-elf-d1cb1aa0c51d40bf/filetypes/json/models/seed_44.txt: constant-predictor model (1 leaf). .txt remains canonical.

converted 3/6 files (3 intentionally skipped, 0 failed)
skipped (3, .txt remains canonical):
  filetypes/json/models/seed_42.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-elf-d1cb1aa0c51d40bf/filetypes/json/models/seed_42.txt: constant-predictor model (1 leaf). .txt remains canonical.
  filetypes/json/models/seed_43.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-elf-d1cb1aa0c51d40bf/filetypes/json/models/seed_43.txt: constant-predictor model (1 leaf). .txt remains canonical.
  filetypes/json/models/seed_44.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-elf-d1cb1aa0c51d40bf/filetypes/json/models/seed_44.txt: constant-predictor model (1 leaf). .txt remains canonical.
staged runtime azoth bundle: /tmp/tmp.ynTXfEuzhb
azoth bundle ok: /tmp/tmp.ynTXfEuzhb
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
  - elf: L50 hostile ENSEMBLE recall dropped 7.61pp (98.61% → 91.00%; tolerance 1.70pp; deployed 95% CI lower = 98.45%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - elf: L50 hostile ENSEMBLE recall dropped 1.65pp BELOW LOW-WATER-MARK (92.64% → 91.00%; LWM tolerance 0.90pp)

compared 75 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: deployed-tolerance gate (1 filetype(s) regressed vs deployed beyond the 1.70pp tolerance; see list above for the actual drops), low-water-mark gate (1 filetype(s) below LWM beyond the 0.90pp tolerance vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1310: azoth-validate] Error 1)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 1.0000)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `d1cb1aa0c51d40bf` | `fcac0203cff3feb9` | `4b7d39300abbf57e` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 1.0000 | 1.0000 | 1.0000 |
| F1 | 0.9973 | 0.9990 | 0.9991 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-07T02-52-06_20260607T024542-promote-d1cb1aa0c51d40bf_azoth-validate.log; tail: 2026-06-06 22:56:08,788 INFO found 6 .txt files to convert
2026-06-06 22:56:09,391 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-elf-d1cb1aa0c51d40bf/filetypes/elf/models/seed_42.onnx
2026-06-06 22:56:10,388 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-06 22:56:11,199 INFO filetypes/elf/models/seed_42.txt -> seed_42.onnx OK (delta=1.36e-07 on 200 rows, 2411 ms)
2026-06-06 22:56:11,761 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-elf-d1cb1aa0c51d40bf/filetypes/elf/models/seed_43.onnx
2026-06-06 22:56:12,738 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-06 22:56:13,880 INFO filetypes/elf/models/seed_43.txt -> seed_43.onnx OK (delta=1.33e-07 on 200 rows, 2681 ms)
2026-06-06 22:56:14,639 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-elf-d1cb1aa0c51d40bf/filetypes/elf/models/seed_44.onnx
2026-06-06 22:56:15,668 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-06 22:56:16,483 INFO filetypes/elf/models/seed_44.txt -> seed_44.onnx OK (delta=1.64e-07 on 200 rows, 2602 ms)
2026-06-06 22:56:16,492 INFO skipping ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-elf-d1cb1aa0c51d40bf/filetypes/json/models/seed_42.onnx: model is a constant predictor (no split learned — trips the TreeEnsembleClassifier 0-split bug)
2026-06-06 22:56:16,493 INFO skipped filetypes/json/models/seed_42.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-elf-d1cb1aa0c51d40bf/filetypes/json/models/seed_42.txt: constant-predictor model (1 leaf). .txt remains canonical.
2026-06-06 22:56:16,499 INFO skipping ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-elf-d1cb1aa0c51d40bf/filetypes/json/models/seed_43.onnx: model is a constant predictor (no split learned — trips the TreeEnsembleClassifier 0-split bug)
2026-06-06 22:56:16,499 INFO skipped filetypes/json/models/seed_43.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-elf-d1cb1aa0c51d40bf/filetypes/json/models/seed_43.txt: constant-predictor model (1 leaf). .txt remains canonical.
2026-06-06 22:56:16,504 INFO skipping ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-elf-d1cb1aa0c51d40bf/filetypes/json/models/seed_44.onnx: model is a constant predictor (no split learned — trips the TreeEnsembleClassifier 0-split bug)
2026-06-06 22:56:16,504 INFO skipped filetypes/json/models/seed_44.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-elf-d1cb1aa0c51d40bf/filetypes/json/models/seed_44.txt: constant-predictor model (1 leaf). .txt remains canonical.

converted 3/6 files (3 intentionally skipped, 0 failed)
skipped (3, .txt remains canonical):
  filetypes/json/models/seed_42.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-elf-d1cb1aa0c51d40bf/filetypes/json/models/seed_42.txt: constant-predictor model (1 leaf). .txt remains canonical.
  filetypes/json/models/seed_43.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-elf-d1cb1aa0c51d40bf/filetypes/json/models/seed_43.txt: constant-predictor model (1 leaf). .txt remains canonical.
  filetypes/json/models/seed_44.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-elf-d1cb1aa0c51d40bf/filetypes/json/models/seed_44.txt: constant-predictor model (1 leaf). .txt remains canonical.
staged runtime azoth bundle: /tmp/tmp.ynTXfEuzhb
azoth bundle ok: /tmp/tmp.ynTXfEuzhb
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
  - elf: L50 hostile ENSEMBLE recall dropped 7.61pp (98.61% → 91.00%; tolerance 1.70pp; deployed 95% CI lower = 98.45%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - elf: L50 hostile ENSEMBLE recall dropped 1.65pp BELOW LOW-WATER-MARK (92.64% → 91.00%; LWM tolerance 0.90pp)

compared 75 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: deployed-tolerance gate (1 filetype(s) regressed vs deployed beyond the 1.70pp tolerance; see list above for the actual drops), low-water-mark gate (1 filetype(s) below LWM beyond the 0.90pp tolerance vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1310: azoth-validate] Error 1)
