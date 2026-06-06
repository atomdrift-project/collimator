# Promote REJECTED — `79193f3806c344da` on `filegroups/documents`

Generated 2026-06-06T14:54:07Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-06T14-51-05_20260606T145043-promote-79193f3806c344da_azoth-validate.log; tail: 2026-06-06 10:54:05,349 INFO filegroups/documents/models/seed_44.txt -> seed_44.onnx OK (delta=1.18e-07 on 200 rows, 3039 ms)
2026-06-06 10:54:05,356 INFO skipping ONNX export for /home/t/collimator/out/models/azoth-candidate-filegroups-documents-79193f3806c344da/filetypes/json/models/seed_42.onnx: model is a constant predictor (no split learned — trips the TreeEnsembleClassifier 0-split bug)
2026-06-06 10:54:05,356 INFO skipped filetypes/json/models/seed_42.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filegroups-documents-79193f3806c344da/filetypes/json/models/seed_42.txt: constant-predictor model (1 leaf). .txt remains canonical.
2026-06-06 10:54:05,365 INFO skipping ONNX export for /home/t/collimator/out/models/azoth-candidate-filegroups-documents-79193f3806c344da/filetypes/json/models/seed_43.onnx: model is a constant predictor (no split learned — trips the TreeEnsembleClassifier 0-split bug)
2026-06-06 10:54:05,366 INFO skipped filetypes/json/models/seed_43.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filegroups-documents-79193f3806c344da/filetypes/json/models/seed_43.txt: constant-predictor model (1 leaf). .txt remains canonical.
2026-06-06 10:54:05,374 INFO skipping ONNX export for /home/t/collimator/out/models/azoth-candidate-filegroups-documents-79193f3806c344da/filetypes/json/models/seed_44.onnx: model is a constant predictor (no split learned — trips the TreeEnsembleClassifier 0-split bug)
2026-06-06 10:54:05,375 INFO skipped filetypes/json/models/seed_44.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filegroups-documents-79193f3806c344da/filetypes/json/models/seed_44.txt: constant-predictor model (1 leaf). .txt remains canonical.

converted 3/6 files (3 intentionally skipped, 0 failed)
skipped (3, .txt remains canonical):
  filetypes/json/models/seed_42.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filegroups-documents-79193f3806c344da/filetypes/json/models/seed_42.txt: constant-predictor model (1 leaf). .txt remains canonical.
  filetypes/json/models/seed_43.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filegroups-documents-79193f3806c344da/filetypes/json/models/seed_43.txt: constant-predictor model (1 leaf). .txt remains canonical.
  filetypes/json/models/seed_44.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filegroups-documents-79193f3806c344da/filetypes/json/models/seed_44.txt: constant-predictor model (1 leaf). .txt remains canonical.
staged runtime azoth bundle: /tmp/tmp.priEWxc3IV
azoth bundle ok: /tmp/tmp.priEWxc3IV
--source-bundle out/models/azoth: 1 routes changed → 9 filetypes impacted, 69 unimpacted (drift treated as pre-existing)

ensemble improvements (≥0.10pp):
  doc: L50 hostile ensemble recall +60.04pp (38.51% → 98.55%)
  xls: L50 hostile ensemble recall +0.55pp (93.19% → 93.74%)

per-route improvements (≥0.10pp, informational):
  docx :: general recall@1FP-on-slice +0.18pp (43.06% → 43.24%)
  docx :: filegroups/documents recall@1FP-on-slice +25.80pp (61.03% → 86.83%)
  pdf :: filetypes/pdf recall@1FP-on-slice +64.05pp (10.39% → 74.44%)
  xls :: filegroups/documents recall@1FP-on-slice +1.30pp (93.49% → 94.79%)
  xls :: filetypes/xls recall@1FP-on-slice +0.72pp (93.73% → 94.45%)
  xlsx :: filegroups/documents recall@1FP-on-slice +1.42pp (31.12% → 32.54%)

per-route regressions (informational; does not block deploy):
  docx :: filetypes/docx recall@1FP-on-slice dropped 9.07pp (89.15% → 80.07%)
  ole :: general recall@1FP-on-slice dropped 7.06pp (90.64% → 83.59%)
  ole :: filegroups/documents recall@1FP-on-slice dropped 4.16pp (93.68% → 89.52%)
  ole :: filetypes/ole recall@1FP-on-slice dropped 8.83pp (93.05% → 84.22%)
  pptx :: general recall@1FP-on-slice dropped 34.72pp (44.44% → 9.72%)
  pptx :: filegroups/documents recall@1FP-on-slice dropped 8.33pp (44.44% → 36.11%)
  xlsx :: general recall@1FP-on-slice dropped 14.94pp (45.91% → 30.97%)
  xlsx :: filetypes/xlsx recall@1FP-on-slice dropped 13.12pp (44.30% → 31.17%)

3 DEPLOYED-TOLERANCE regression(s) (vs currently-deployed bundle /home/t/.local/share/litmus/models/azoth) — THIS IS WHAT BLOCKS THE DEPLOY:
  - ole: L50 hostile ENSEMBLE recall dropped 3.26pp (82.17% → 78.91%; tolerance 1.70pp; deployed 95% CI lower = 79.33%)
  - pdf: L50 hostile ENSEMBLE recall dropped 2.20pp (6.50% → 4.30%; tolerance 1.70pp; deployed 95% CI lower = 6.18%)
  - xlsx: L50 hostile ENSEMBLE recall dropped 5.69pp (36.08% → 30.39%; tolerance 1.70pp; deployed 95% CI lower = 34.98%)

compared 75 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: deployed-tolerance gate (3 filetype(s) regressed vs deployed beyond the 1.70pp tolerance; see list above for the actual drops)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1297: azoth-validate] Error 1)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 1.0000)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `79193f3806c344da` | `2f679abc02b211c2` | `883e754f5379f564` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9997 | 0.9991 | 0.9992 |
| F1 | 0.9969 | 0.9975 | 0.9968 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-06T14-51-05_20260606T145043-promote-79193f3806c344da_azoth-validate.log; tail: 2026-06-06 10:54:05,349 INFO filegroups/documents/models/seed_44.txt -> seed_44.onnx OK (delta=1.18e-07 on 200 rows, 3039 ms)
2026-06-06 10:54:05,356 INFO skipping ONNX export for /home/t/collimator/out/models/azoth-candidate-filegroups-documents-79193f3806c344da/filetypes/json/models/seed_42.onnx: model is a constant predictor (no split learned — trips the TreeEnsembleClassifier 0-split bug)
2026-06-06 10:54:05,356 INFO skipped filetypes/json/models/seed_42.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filegroups-documents-79193f3806c344da/filetypes/json/models/seed_42.txt: constant-predictor model (1 leaf). .txt remains canonical.
2026-06-06 10:54:05,365 INFO skipping ONNX export for /home/t/collimator/out/models/azoth-candidate-filegroups-documents-79193f3806c344da/filetypes/json/models/seed_43.onnx: model is a constant predictor (no split learned — trips the TreeEnsembleClassifier 0-split bug)
2026-06-06 10:54:05,366 INFO skipped filetypes/json/models/seed_43.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filegroups-documents-79193f3806c344da/filetypes/json/models/seed_43.txt: constant-predictor model (1 leaf). .txt remains canonical.
2026-06-06 10:54:05,374 INFO skipping ONNX export for /home/t/collimator/out/models/azoth-candidate-filegroups-documents-79193f3806c344da/filetypes/json/models/seed_44.onnx: model is a constant predictor (no split learned — trips the TreeEnsembleClassifier 0-split bug)
2026-06-06 10:54:05,375 INFO skipped filetypes/json/models/seed_44.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filegroups-documents-79193f3806c344da/filetypes/json/models/seed_44.txt: constant-predictor model (1 leaf). .txt remains canonical.

converted 3/6 files (3 intentionally skipped, 0 failed)
skipped (3, .txt remains canonical):
  filetypes/json/models/seed_42.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filegroups-documents-79193f3806c344da/filetypes/json/models/seed_42.txt: constant-predictor model (1 leaf). .txt remains canonical.
  filetypes/json/models/seed_43.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filegroups-documents-79193f3806c344da/filetypes/json/models/seed_43.txt: constant-predictor model (1 leaf). .txt remains canonical.
  filetypes/json/models/seed_44.txt: skipped ONNX export for /home/t/collimator/out/models/azoth-candidate-filegroups-documents-79193f3806c344da/filetypes/json/models/seed_44.txt: constant-predictor model (1 leaf). .txt remains canonical.
staged runtime azoth bundle: /tmp/tmp.priEWxc3IV
azoth bundle ok: /tmp/tmp.priEWxc3IV
--source-bundle out/models/azoth: 1 routes changed → 9 filetypes impacted, 69 unimpacted (drift treated as pre-existing)

ensemble improvements (≥0.10pp):
  doc: L50 hostile ensemble recall +60.04pp (38.51% → 98.55%)
  xls: L50 hostile ensemble recall +0.55pp (93.19% → 93.74%)

per-route improvements (≥0.10pp, informational):
  docx :: general recall@1FP-on-slice +0.18pp (43.06% → 43.24%)
  docx :: filegroups/documents recall@1FP-on-slice +25.80pp (61.03% → 86.83%)
  pdf :: filetypes/pdf recall@1FP-on-slice +64.05pp (10.39% → 74.44%)
  xls :: filegroups/documents recall@1FP-on-slice +1.30pp (93.49% → 94.79%)
  xls :: filetypes/xls recall@1FP-on-slice +0.72pp (93.73% → 94.45%)
  xlsx :: filegroups/documents recall@1FP-on-slice +1.42pp (31.12% → 32.54%)

per-route regressions (informational; does not block deploy):
  docx :: filetypes/docx recall@1FP-on-slice dropped 9.07pp (89.15% → 80.07%)
  ole :: general recall@1FP-on-slice dropped 7.06pp (90.64% → 83.59%)
  ole :: filegroups/documents recall@1FP-on-slice dropped 4.16pp (93.68% → 89.52%)
  ole :: filetypes/ole recall@1FP-on-slice dropped 8.83pp (93.05% → 84.22%)
  pptx :: general recall@1FP-on-slice dropped 34.72pp (44.44% → 9.72%)
  pptx :: filegroups/documents recall@1FP-on-slice dropped 8.33pp (44.44% → 36.11%)
  xlsx :: general recall@1FP-on-slice dropped 14.94pp (45.91% → 30.97%)
  xlsx :: filetypes/xlsx recall@1FP-on-slice dropped 13.12pp (44.30% → 31.17%)

3 DEPLOYED-TOLERANCE regression(s) (vs currently-deployed bundle /home/t/.local/share/litmus/models/azoth) — THIS IS WHAT BLOCKS THE DEPLOY:
  - ole: L50 hostile ENSEMBLE recall dropped 3.26pp (82.17% → 78.91%; tolerance 1.70pp; deployed 95% CI lower = 79.33%)
  - pdf: L50 hostile ENSEMBLE recall dropped 2.20pp (6.50% → 4.30%; tolerance 1.70pp; deployed 95% CI lower = 6.18%)
  - xlsx: L50 hostile ENSEMBLE recall dropped 5.69pp (36.08% → 30.39%; tolerance 1.70pp; deployed 95% CI lower = 34.98%)

compared 75 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: deployed-tolerance gate (3 filetype(s) regressed vs deployed beyond the 1.70pp tolerance; see list above for the actual drops)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1297: azoth-validate] Error 1)
