# Promote REJECTED — `2bb4b063701f7ea6` on `filetypes/shell`

Generated 2026-06-06T15:12:22Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-06T15-09-18_20260606T150857-promote-2bb4b063701f7ea6_azoth-validate.log; tail: 2026-06-06 11:12:16,265 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-shell-2bb4b063701f7ea6/filetypes/rust already has model.onnx; skipping
2026-06-06 11:12:16,265 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-shell-2bb4b063701f7ea6/filetypes/tar already has model.onnx; skipping
2026-06-06 11:12:16,265 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-shell-2bb4b063701f7ea6/filetypes/text already has model.onnx; skipping
2026-06-06 11:12:16,265 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-shell-2bb4b063701f7ea6/filetypes/vbs already has seed_42.onnx; skipping
2026-06-06 11:12:16,265 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-shell-2bb4b063701f7ea6/filetypes/vbs already has seed_43.onnx; skipping
2026-06-06 11:12:16,265 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-shell-2bb4b063701f7ea6/filetypes/vbs already has seed_44.onnx; skipping
2026-06-06 11:12:16,265 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-shell-2bb4b063701f7ea6/filetypes/xls already has model.onnx; skipping
2026-06-06 11:12:16,265 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-shell-2bb4b063701f7ea6/filetypes/xlsx already has model.onnx; skipping
2026-06-06 11:12:16,265 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-shell-2bb4b063701f7ea6/filetypes/xml already has model.onnx; skipping
2026-06-06 11:12:16,265 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-shell-2bb4b063701f7ea6/filetypes/zip already has seed_42.onnx; skipping
2026-06-06 11:12:16,265 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-shell-2bb4b063701f7ea6/filetypes/zip already has seed_43.onnx; skipping
2026-06-06 11:12:16,265 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-shell-2bb4b063701f7ea6/filetypes/zip already has seed_44.onnx; skipping
2026-06-06 11:12:16,265 INFO found 6 .txt files to convert
2026-06-06 11:12:16,299 INFO skipping ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-shell-2bb4b063701f7ea6/filetypes/json/models/seed_42.onnx: model is a constant predictor (no split learned — trips the TreeEnsembleClassifier 0-split bug)
2026-06-06 11:12:16,300 INFO skipped filetypes/json/models/seed_42.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-shell-2bb4b063701f7ea6/filetypes/json/models/seed_42.txt: constant-predictor model (1 leaf). .txt remains canonical.
2026-06-06 11:12:16,304 INFO skipping ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-shell-2bb4b063701f7ea6/filetypes/json/models/seed_43.onnx: model is a constant predictor (no split learned — trips the TreeEnsembleClassifier 0-split bug)
2026-06-06 11:12:16,304 INFO skipped filetypes/json/models/seed_43.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-shell-2bb4b063701f7ea6/filetypes/json/models/seed_43.txt: constant-predictor model (1 leaf). .txt remains canonical.
2026-06-06 11:12:16,312 INFO skipping ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-shell-2bb4b063701f7ea6/filetypes/json/models/seed_44.onnx: model is a constant predictor (no split learned — trips the TreeEnsembleClassifier 0-split bug)
2026-06-06 11:12:16,312 INFO skipped filetypes/json/models/seed_44.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-shell-2bb4b063701f7ea6/filetypes/json/models/seed_44.txt: constant-predictor model (1 leaf). .txt remains canonical.
2026-06-06 11:12:16,547 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-shell-2bb4b063701f7ea6/filetypes/shell/models/seed_42.onnx
2026-06-06 11:12:16,981 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-06 11:12:17,760 INFO filetypes/shell/models/seed_42.txt -> seed_42.onnx OK (delta=8.76e-08 on 200 rows, 1448 ms)
2026-06-06 11:12:17,967 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-shell-2bb4b063701f7ea6/filetypes/shell/models/seed_43.onnx
2026-06-06 11:12:18,372 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-06 11:12:19,100 INFO filetypes/shell/models/seed_43.txt -> seed_43.onnx OK (delta=8.41e-08 on 200 rows, 1340 ms)
2026-06-06 11:12:19,401 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-shell-2bb4b063701f7ea6/filetypes/shell/models/seed_44.onnx
2026-06-06 11:12:19,819 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-06 11:12:20,563 INFO filetypes/shell/models/seed_44.txt -> seed_44.onnx OK (delta=8.41e-08 on 200 rows, 1463 ms)

converted 3/6 files (3 intentionally skipped, 0 failed)
skipped (3, .txt remains canonical):
  filetypes/json/models/seed_42.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-shell-2bb4b063701f7ea6/filetypes/json/models/seed_42.txt: constant-predictor model (1 leaf). .txt remains canonical.
  filetypes/json/models/seed_43.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-shell-2bb4b063701f7ea6/filetypes/json/models/seed_43.txt: constant-predictor model (1 leaf). .txt remains canonical.
  filetypes/json/models/seed_44.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-shell-2bb4b063701f7ea6/filetypes/json/models/seed_44.txt: constant-predictor model (1 leaf). .txt remains canonical.
staged runtime azoth bundle: /tmp/tmp.02zaIurBhj
azoth bundle ok: /tmp/tmp.02zaIurBhj
--source-bundle out/models/azoth: 1 routes changed → 1 filetypes impacted, 77 unimpacted (drift treated as pre-existing)

per-route regressions (informational; does not block deploy):
  shell :: general recall@1FP-on-slice dropped 28.10pp (74.79% → 46.69%)

1 DEPLOYED-TOLERANCE regression(s) (vs currently-deployed bundle /home/t/.local/share/litmus/models/azoth) — THIS IS WHAT BLOCKS THE DEPLOY:
  - shell: L50 hostile ENSEMBLE recall dropped 3.54pp (81.64% → 78.10%; tolerance 1.70pp; deployed 95% CI lower = 79.81%)

compared 75 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: deployed-tolerance gate (1 filetype(s) regressed vs deployed beyond the 1.70pp tolerance; see list above for the actual drops)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1297: azoth-validate] Error 1)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9968)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `2bb4b063701f7ea6` | `912e7dbcbcd0171e` | `d5a5af85b97d98ad` |
| PR AUC | 0.9968 | 0.9987 | 0.9988 |
| ROC AUC | 0.9980 | 0.9988 | 0.9988 |
| F1 | 0.9621 | 0.9769 | 0.9752 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-06T15-09-18_20260606T150857-promote-2bb4b063701f7ea6_azoth-validate.log; tail: 2026-06-06 11:12:16,265 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-shell-2bb4b063701f7ea6/filetypes/rust already has model.onnx; skipping
2026-06-06 11:12:16,265 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-shell-2bb4b063701f7ea6/filetypes/tar already has model.onnx; skipping
2026-06-06 11:12:16,265 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-shell-2bb4b063701f7ea6/filetypes/text already has model.onnx; skipping
2026-06-06 11:12:16,265 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-shell-2bb4b063701f7ea6/filetypes/vbs already has seed_42.onnx; skipping
2026-06-06 11:12:16,265 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-shell-2bb4b063701f7ea6/filetypes/vbs already has seed_43.onnx; skipping
2026-06-06 11:12:16,265 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-shell-2bb4b063701f7ea6/filetypes/vbs already has seed_44.onnx; skipping
2026-06-06 11:12:16,265 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-shell-2bb4b063701f7ea6/filetypes/xls already has model.onnx; skipping
2026-06-06 11:12:16,265 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-shell-2bb4b063701f7ea6/filetypes/xlsx already has model.onnx; skipping
2026-06-06 11:12:16,265 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-shell-2bb4b063701f7ea6/filetypes/xml already has model.onnx; skipping
2026-06-06 11:12:16,265 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-shell-2bb4b063701f7ea6/filetypes/zip already has seed_42.onnx; skipping
2026-06-06 11:12:16,265 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-shell-2bb4b063701f7ea6/filetypes/zip already has seed_43.onnx; skipping
2026-06-06 11:12:16,265 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-shell-2bb4b063701f7ea6/filetypes/zip already has seed_44.onnx; skipping
2026-06-06 11:12:16,265 INFO found 6 .txt files to convert
2026-06-06 11:12:16,299 INFO skipping ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-shell-2bb4b063701f7ea6/filetypes/json/models/seed_42.onnx: model is a constant predictor (no split learned — trips the TreeEnsembleClassifier 0-split bug)
2026-06-06 11:12:16,300 INFO skipped filetypes/json/models/seed_42.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-shell-2bb4b063701f7ea6/filetypes/json/models/seed_42.txt: constant-predictor model (1 leaf). .txt remains canonical.
2026-06-06 11:12:16,304 INFO skipping ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-shell-2bb4b063701f7ea6/filetypes/json/models/seed_43.onnx: model is a constant predictor (no split learned — trips the TreeEnsembleClassifier 0-split bug)
2026-06-06 11:12:16,304 INFO skipped filetypes/json/models/seed_43.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-shell-2bb4b063701f7ea6/filetypes/json/models/seed_43.txt: constant-predictor model (1 leaf). .txt remains canonical.
2026-06-06 11:12:16,312 INFO skipping ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-shell-2bb4b063701f7ea6/filetypes/json/models/seed_44.onnx: model is a constant predictor (no split learned — trips the TreeEnsembleClassifier 0-split bug)
2026-06-06 11:12:16,312 INFO skipped filetypes/json/models/seed_44.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-shell-2bb4b063701f7ea6/filetypes/json/models/seed_44.txt: constant-predictor model (1 leaf). .txt remains canonical.
2026-06-06 11:12:16,547 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-shell-2bb4b063701f7ea6/filetypes/shell/models/seed_42.onnx
2026-06-06 11:12:16,981 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-06 11:12:17,760 INFO filetypes/shell/models/seed_42.txt -> seed_42.onnx OK (delta=8.76e-08 on 200 rows, 1448 ms)
2026-06-06 11:12:17,967 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-shell-2bb4b063701f7ea6/filetypes/shell/models/seed_43.onnx
2026-06-06 11:12:18,372 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-06 11:12:19,100 INFO filetypes/shell/models/seed_43.txt -> seed_43.onnx OK (delta=8.41e-08 on 200 rows, 1340 ms)
2026-06-06 11:12:19,401 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-shell-2bb4b063701f7ea6/filetypes/shell/models/seed_44.onnx
2026-06-06 11:12:19,819 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-06 11:12:20,563 INFO filetypes/shell/models/seed_44.txt -> seed_44.onnx OK (delta=8.41e-08 on 200 rows, 1463 ms)

converted 3/6 files (3 intentionally skipped, 0 failed)
skipped (3, .txt remains canonical):
  filetypes/json/models/seed_42.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-shell-2bb4b063701f7ea6/filetypes/json/models/seed_42.txt: constant-predictor model (1 leaf). .txt remains canonical.
  filetypes/json/models/seed_43.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-shell-2bb4b063701f7ea6/filetypes/json/models/seed_43.txt: constant-predictor model (1 leaf). .txt remains canonical.
  filetypes/json/models/seed_44.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-shell-2bb4b063701f7ea6/filetypes/json/models/seed_44.txt: constant-predictor model (1 leaf). .txt remains canonical.
staged runtime azoth bundle: /tmp/tmp.02zaIurBhj
azoth bundle ok: /tmp/tmp.02zaIurBhj
--source-bundle out/models/azoth: 1 routes changed → 1 filetypes impacted, 77 unimpacted (drift treated as pre-existing)

per-route regressions (informational; does not block deploy):
  shell :: general recall@1FP-on-slice dropped 28.10pp (74.79% → 46.69%)

1 DEPLOYED-TOLERANCE regression(s) (vs currently-deployed bundle /home/t/.local/share/litmus/models/azoth) — THIS IS WHAT BLOCKS THE DEPLOY:
  - shell: L50 hostile ENSEMBLE recall dropped 3.54pp (81.64% → 78.10%; tolerance 1.70pp; deployed 95% CI lower = 79.81%)

compared 75 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: deployed-tolerance gate (1 filetype(s) regressed vs deployed beyond the 1.70pp tolerance; see list above for the actual drops)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1297: azoth-validate] Error 1)
