# Promote REJECTED — `cad3a137090e6b9f` on `filetypes/shell`

Generated 2026-06-06T15:08:34Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-06T15-05-29_20260606T150510-promote-cad3a137090e6b9f_azoth-validate.log; tail: 2026-06-06 11:08:28,010 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-shell-cad3a137090e6b9f/filetypes/rust already has model.onnx; skipping
2026-06-06 11:08:28,010 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-shell-cad3a137090e6b9f/filetypes/tar already has model.onnx; skipping
2026-06-06 11:08:28,010 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-shell-cad3a137090e6b9f/filetypes/text already has model.onnx; skipping
2026-06-06 11:08:28,010 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-shell-cad3a137090e6b9f/filetypes/vbs already has seed_42.onnx; skipping
2026-06-06 11:08:28,010 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-shell-cad3a137090e6b9f/filetypes/vbs already has seed_43.onnx; skipping
2026-06-06 11:08:28,010 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-shell-cad3a137090e6b9f/filetypes/vbs already has seed_44.onnx; skipping
2026-06-06 11:08:28,010 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-shell-cad3a137090e6b9f/filetypes/xls already has model.onnx; skipping
2026-06-06 11:08:28,010 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-shell-cad3a137090e6b9f/filetypes/xlsx already has model.onnx; skipping
2026-06-06 11:08:28,010 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-shell-cad3a137090e6b9f/filetypes/xml already has model.onnx; skipping
2026-06-06 11:08:28,010 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-shell-cad3a137090e6b9f/filetypes/zip already has seed_42.onnx; skipping
2026-06-06 11:08:28,010 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-shell-cad3a137090e6b9f/filetypes/zip already has seed_43.onnx; skipping
2026-06-06 11:08:28,010 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-shell-cad3a137090e6b9f/filetypes/zip already has seed_44.onnx; skipping
2026-06-06 11:08:28,010 INFO found 6 .txt files to convert
2026-06-06 11:08:28,045 INFO skipping ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-shell-cad3a137090e6b9f/filetypes/json/models/seed_42.onnx: model is a constant predictor (no split learned — trips the TreeEnsembleClassifier 0-split bug)
2026-06-06 11:08:28,045 INFO skipped filetypes/json/models/seed_42.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-shell-cad3a137090e6b9f/filetypes/json/models/seed_42.txt: constant-predictor model (1 leaf). .txt remains canonical.
2026-06-06 11:08:28,048 INFO skipping ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-shell-cad3a137090e6b9f/filetypes/json/models/seed_43.onnx: model is a constant predictor (no split learned — trips the TreeEnsembleClassifier 0-split bug)
2026-06-06 11:08:28,048 INFO skipped filetypes/json/models/seed_43.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-shell-cad3a137090e6b9f/filetypes/json/models/seed_43.txt: constant-predictor model (1 leaf). .txt remains canonical.
2026-06-06 11:08:28,053 INFO skipping ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-shell-cad3a137090e6b9f/filetypes/json/models/seed_44.onnx: model is a constant predictor (no split learned — trips the TreeEnsembleClassifier 0-split bug)
2026-06-06 11:08:28,053 INFO skipped filetypes/json/models/seed_44.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-shell-cad3a137090e6b9f/filetypes/json/models/seed_44.txt: constant-predictor model (1 leaf). .txt remains canonical.
2026-06-06 11:08:28,281 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-shell-cad3a137090e6b9f/filetypes/shell/models/seed_42.onnx
2026-06-06 11:08:28,726 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-06 11:08:29,487 INFO filetypes/shell/models/seed_42.txt -> seed_42.onnx OK (delta=1.29e-07 on 200 rows, 1434 ms)
2026-06-06 11:08:29,673 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-shell-cad3a137090e6b9f/filetypes/shell/models/seed_43.onnx
2026-06-06 11:08:30,095 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-06 11:08:30,827 INFO filetypes/shell/models/seed_43.txt -> seed_43.onnx OK (delta=9.21e-08 on 200 rows, 1340 ms)
2026-06-06 11:08:31,105 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-shell-cad3a137090e6b9f/filetypes/shell/models/seed_44.onnx
2026-06-06 11:08:31,473 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-06 11:08:32,228 INFO filetypes/shell/models/seed_44.txt -> seed_44.onnx OK (delta=8.63e-08 on 200 rows, 1401 ms)

converted 3/6 files (3 intentionally skipped, 0 failed)
skipped (3, .txt remains canonical):
  filetypes/json/models/seed_42.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-shell-cad3a137090e6b9f/filetypes/json/models/seed_42.txt: constant-predictor model (1 leaf). .txt remains canonical.
  filetypes/json/models/seed_43.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-shell-cad3a137090e6b9f/filetypes/json/models/seed_43.txt: constant-predictor model (1 leaf). .txt remains canonical.
  filetypes/json/models/seed_44.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-shell-cad3a137090e6b9f/filetypes/json/models/seed_44.txt: constant-predictor model (1 leaf). .txt remains canonical.
staged runtime azoth bundle: /tmp/tmp.FQiF74NSZb
azoth bundle ok: /tmp/tmp.FQiF74NSZb
--source-bundle out/models/azoth: 1 routes changed → 1 filetypes impacted, 77 unimpacted (drift treated as pre-existing)

per-route regressions (informational; does not block deploy):
  shell :: general recall@1FP-on-slice dropped 28.10pp (74.79% → 46.69%)

1 DEPLOYED-TOLERANCE regression(s) (vs currently-deployed bundle /home/t/.local/share/litmus/models/azoth) — THIS IS WHAT BLOCKS THE DEPLOY:
  - shell: L50 hostile ENSEMBLE recall dropped 2.20pp (81.64% → 79.43%; tolerance 1.70pp; deployed 95% CI lower = 79.81%)

compared 75 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: deployed-tolerance gate (1 filetype(s) regressed vs deployed beyond the 1.70pp tolerance; see list above for the actual drops)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1297: azoth-validate] Error 1)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9960)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `cad3a137090e6b9f` | `774524474e433510` | `4da5e03749c12503` |
| PR AUC | 0.9960 | 0.9987 | 0.9986 |
| ROC AUC | 0.9974 | 0.9987 | 0.9987 |
| F1 | 0.9656 | 0.9741 | 0.9786 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-06T15-05-29_20260606T150510-promote-cad3a137090e6b9f_azoth-validate.log; tail: 2026-06-06 11:08:28,010 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-shell-cad3a137090e6b9f/filetypes/rust already has model.onnx; skipping
2026-06-06 11:08:28,010 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-shell-cad3a137090e6b9f/filetypes/tar already has model.onnx; skipping
2026-06-06 11:08:28,010 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-shell-cad3a137090e6b9f/filetypes/text already has model.onnx; skipping
2026-06-06 11:08:28,010 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-shell-cad3a137090e6b9f/filetypes/vbs already has seed_42.onnx; skipping
2026-06-06 11:08:28,010 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-shell-cad3a137090e6b9f/filetypes/vbs already has seed_43.onnx; skipping
2026-06-06 11:08:28,010 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-shell-cad3a137090e6b9f/filetypes/vbs already has seed_44.onnx; skipping
2026-06-06 11:08:28,010 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-shell-cad3a137090e6b9f/filetypes/xls already has model.onnx; skipping
2026-06-06 11:08:28,010 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-shell-cad3a137090e6b9f/filetypes/xlsx already has model.onnx; skipping
2026-06-06 11:08:28,010 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-shell-cad3a137090e6b9f/filetypes/xml already has model.onnx; skipping
2026-06-06 11:08:28,010 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-shell-cad3a137090e6b9f/filetypes/zip already has seed_42.onnx; skipping
2026-06-06 11:08:28,010 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-shell-cad3a137090e6b9f/filetypes/zip already has seed_43.onnx; skipping
2026-06-06 11:08:28,010 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-shell-cad3a137090e6b9f/filetypes/zip already has seed_44.onnx; skipping
2026-06-06 11:08:28,010 INFO found 6 .txt files to convert
2026-06-06 11:08:28,045 INFO skipping ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-shell-cad3a137090e6b9f/filetypes/json/models/seed_42.onnx: model is a constant predictor (no split learned — trips the TreeEnsembleClassifier 0-split bug)
2026-06-06 11:08:28,045 INFO skipped filetypes/json/models/seed_42.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-shell-cad3a137090e6b9f/filetypes/json/models/seed_42.txt: constant-predictor model (1 leaf). .txt remains canonical.
2026-06-06 11:08:28,048 INFO skipping ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-shell-cad3a137090e6b9f/filetypes/json/models/seed_43.onnx: model is a constant predictor (no split learned — trips the TreeEnsembleClassifier 0-split bug)
2026-06-06 11:08:28,048 INFO skipped filetypes/json/models/seed_43.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-shell-cad3a137090e6b9f/filetypes/json/models/seed_43.txt: constant-predictor model (1 leaf). .txt remains canonical.
2026-06-06 11:08:28,053 INFO skipping ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-shell-cad3a137090e6b9f/filetypes/json/models/seed_44.onnx: model is a constant predictor (no split learned — trips the TreeEnsembleClassifier 0-split bug)
2026-06-06 11:08:28,053 INFO skipped filetypes/json/models/seed_44.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-shell-cad3a137090e6b9f/filetypes/json/models/seed_44.txt: constant-predictor model (1 leaf). .txt remains canonical.
2026-06-06 11:08:28,281 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-shell-cad3a137090e6b9f/filetypes/shell/models/seed_42.onnx
2026-06-06 11:08:28,726 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-06 11:08:29,487 INFO filetypes/shell/models/seed_42.txt -> seed_42.onnx OK (delta=1.29e-07 on 200 rows, 1434 ms)
2026-06-06 11:08:29,673 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-shell-cad3a137090e6b9f/filetypes/shell/models/seed_43.onnx
2026-06-06 11:08:30,095 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-06 11:08:30,827 INFO filetypes/shell/models/seed_43.txt -> seed_43.onnx OK (delta=9.21e-08 on 200 rows, 1340 ms)
2026-06-06 11:08:31,105 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-shell-cad3a137090e6b9f/filetypes/shell/models/seed_44.onnx
2026-06-06 11:08:31,473 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-06 11:08:32,228 INFO filetypes/shell/models/seed_44.txt -> seed_44.onnx OK (delta=8.63e-08 on 200 rows, 1401 ms)

converted 3/6 files (3 intentionally skipped, 0 failed)
skipped (3, .txt remains canonical):
  filetypes/json/models/seed_42.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-shell-cad3a137090e6b9f/filetypes/json/models/seed_42.txt: constant-predictor model (1 leaf). .txt remains canonical.
  filetypes/json/models/seed_43.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-shell-cad3a137090e6b9f/filetypes/json/models/seed_43.txt: constant-predictor model (1 leaf). .txt remains canonical.
  filetypes/json/models/seed_44.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filetypes-shell-cad3a137090e6b9f/filetypes/json/models/seed_44.txt: constant-predictor model (1 leaf). .txt remains canonical.
staged runtime azoth bundle: /tmp/tmp.FQiF74NSZb
azoth bundle ok: /tmp/tmp.FQiF74NSZb
--source-bundle out/models/azoth: 1 routes changed → 1 filetypes impacted, 77 unimpacted (drift treated as pre-existing)

per-route regressions (informational; does not block deploy):
  shell :: general recall@1FP-on-slice dropped 28.10pp (74.79% → 46.69%)

1 DEPLOYED-TOLERANCE regression(s) (vs currently-deployed bundle /home/t/.local/share/litmus/models/azoth) — THIS IS WHAT BLOCKS THE DEPLOY:
  - shell: L50 hostile ENSEMBLE recall dropped 2.20pp (81.64% → 79.43%; tolerance 1.70pp; deployed 95% CI lower = 79.81%)

compared 75 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: deployed-tolerance gate (1 filetype(s) regressed vs deployed beyond the 1.70pp tolerance; see list above for the actual drops)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1297: azoth-validate] Error 1)
