# Promote REJECTED — `f9655c5de6f52572` on `filegroups/documents`

Generated 2026-06-01T14:23:58Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-01T14-19-52_20260601T141949-promote-f9655c5de6f52572_azoth-validate.log; tail: 2026-06-01 10:23:45,211 INFO found 3 .txt files to convert
2026-06-01 10:23:45,274 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filegroups-documents-f9655c5de6f52572/filegroups/documents/models/seed_42.onnx
2026-06-01 10:23:47,382 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-01 10:23:48,042 INFO filegroups/documents/models/seed_42.txt -> seed_42.onnx OK (delta=9.69e-08 on 200 rows, 2831 ms)
2026-06-01 10:23:48,159 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filegroups-documents-f9655c5de6f52572/filegroups/documents/models/seed_43.onnx
2026-06-01 10:23:50,168 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-01 10:23:50,853 INFO filegroups/documents/models/seed_43.txt -> seed_43.onnx OK (delta=1.08e-07 on 200 rows, 2810 ms)
2026-06-01 10:23:50,926 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filegroups-documents-f9655c5de6f52572/filegroups/documents/models/seed_44.onnx
2026-06-01 10:23:53,000 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-01 10:23:53,639 INFO filegroups/documents/models/seed_44.txt -> seed_44.onnx OK (delta=1.15e-07 on 200 rows, 2786 ms)

converted 3/3 files (0 intentionally skipped, 0 failed)
staged runtime azoth bundle: /tmp/tmp.SfbiWf9Xfx
azoth bundle ok: /tmp/tmp.SfbiWf9Xfx
--source-bundle out/models/azoth: 1 routes changed → 9 filetypes impacted, 70 unimpacted (drift treated as pre-existing)

ensemble improvements (≥0.10pp):
  c: L50 hostile ensemble recall +1.40pp (4.38% → 5.79%)
  kotlin: L50 hostile ensemble recall +2.01pp (46.97% → 48.97%)
  ole: L50 hostile ensemble recall +65.82pp (17.37% → 83.19%)
  pptx: L50 hostile ensemble recall +6.15pp (38.46% → 44.62%)
  shell: L50 hostile ensemble recall +10.01pp (75.12% → 85.14%)
  xlsx: L50 hostile ensemble recall +0.28pp (44.58% → 44.85%)

per-route improvements (≥0.10pp, informational):
  docx :: filegroups/documents recall@1FP-on-slice +8.38pp (80.64% → 89.02%)
  go :: filegroups/source recall@1FP-on-slice +0.17pp (2.37% → 2.54%)
  kotlin :: filegroups/source recall@1FP-on-slice +15.80pp (35.00% → 50.81%)
  rust :: filegroups/source recall@1FP-on-slice +0.60pp (2.41% → 3.01%)
  shell :: filetypes/shell recall@1FP-on-slice +13.81pp (74.75% → 88.56%)

per-route regressions (informational; does not block deploy):
  c :: filegroups/source recall@1FP-on-slice dropped 2.02pp (10.96% → 8.93%)
  csharp :: filegroups/source recall@1FP-on-slice dropped 5.39pp (31.54% → 26.14%)
  html :: filegroups/documents recall@1FP-on-slice dropped 12.00pp (68.00% → 56.00%)
  java :: filegroups/source recall@1FP-on-slice dropped 20.00pp (60.00% → 40.00%)
  ole :: filegroups/documents recall@1FP-on-slice dropped 2.68pp (94.77% → 92.09%)
  pdf :: filegroups/documents recall@1FP-on-slice dropped 3.52pp (10.95% → 7.43%)
  pptx :: filegroups/documents recall@1FP-on-slice dropped 12.31pp (46.15% → 33.85%)
  xlsx :: filegroups/documents recall@1FP-on-slice dropped 23.64pp (55.21% → 31.57%)

1 DEPLOYED-TOLERANCE regression(s) (vs currently-deployed bundle /home/t/.local/share/litmus/models/azoth) — THIS IS WHAT BLOCKS THE DEPLOY:
  - doc: L50 hostile ENSEMBLE recall dropped 4.09pp (99.04% → 94.96%; tolerance 1.70pp; deployed 95% CI lower = 98.66%)

compared 77 filetypes (mal≥1, ben≥1); 2 below threshold and skipped.

blocked by: deployed-tolerance gate (1 filetype(s) regressed vs deployed beyond the 1.70pp tolerance; see list above for the actual drops)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1152: azoth-validate] Error 1)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 1.0000)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `f9655c5de6f52572` | `804b22b3ca24414d` | `e1186e2ace6fcc6a` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9998 | 0.9991 | 0.9989 |
| F1 | 0.9966 | 0.9973 | 0.9973 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-01T14-19-52_20260601T141949-promote-f9655c5de6f52572_azoth-validate.log; tail: 2026-06-01 10:23:45,211 INFO found 3 .txt files to convert
2026-06-01 10:23:45,274 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filegroups-documents-f9655c5de6f52572/filegroups/documents/models/seed_42.onnx
2026-06-01 10:23:47,382 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-01 10:23:48,042 INFO filegroups/documents/models/seed_42.txt -> seed_42.onnx OK (delta=9.69e-08 on 200 rows, 2831 ms)
2026-06-01 10:23:48,159 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filegroups-documents-f9655c5de6f52572/filegroups/documents/models/seed_43.onnx
2026-06-01 10:23:50,168 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-01 10:23:50,853 INFO filegroups/documents/models/seed_43.txt -> seed_43.onnx OK (delta=1.08e-07 on 200 rows, 2810 ms)
2026-06-01 10:23:50,926 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filegroups-documents-f9655c5de6f52572/filegroups/documents/models/seed_44.onnx
2026-06-01 10:23:53,000 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-01 10:23:53,639 INFO filegroups/documents/models/seed_44.txt -> seed_44.onnx OK (delta=1.15e-07 on 200 rows, 2786 ms)

converted 3/3 files (0 intentionally skipped, 0 failed)
staged runtime azoth bundle: /tmp/tmp.SfbiWf9Xfx
azoth bundle ok: /tmp/tmp.SfbiWf9Xfx
--source-bundle out/models/azoth: 1 routes changed → 9 filetypes impacted, 70 unimpacted (drift treated as pre-existing)

ensemble improvements (≥0.10pp):
  c: L50 hostile ensemble recall +1.40pp (4.38% → 5.79%)
  kotlin: L50 hostile ensemble recall +2.01pp (46.97% → 48.97%)
  ole: L50 hostile ensemble recall +65.82pp (17.37% → 83.19%)
  pptx: L50 hostile ensemble recall +6.15pp (38.46% → 44.62%)
  shell: L50 hostile ensemble recall +10.01pp (75.12% → 85.14%)
  xlsx: L50 hostile ensemble recall +0.28pp (44.58% → 44.85%)

per-route improvements (≥0.10pp, informational):
  docx :: filegroups/documents recall@1FP-on-slice +8.38pp (80.64% → 89.02%)
  go :: filegroups/source recall@1FP-on-slice +0.17pp (2.37% → 2.54%)
  kotlin :: filegroups/source recall@1FP-on-slice +15.80pp (35.00% → 50.81%)
  rust :: filegroups/source recall@1FP-on-slice +0.60pp (2.41% → 3.01%)
  shell :: filetypes/shell recall@1FP-on-slice +13.81pp (74.75% → 88.56%)

per-route regressions (informational; does not block deploy):
  c :: filegroups/source recall@1FP-on-slice dropped 2.02pp (10.96% → 8.93%)
  csharp :: filegroups/source recall@1FP-on-slice dropped 5.39pp (31.54% → 26.14%)
  html :: filegroups/documents recall@1FP-on-slice dropped 12.00pp (68.00% → 56.00%)
  java :: filegroups/source recall@1FP-on-slice dropped 20.00pp (60.00% → 40.00%)
  ole :: filegroups/documents recall@1FP-on-slice dropped 2.68pp (94.77% → 92.09%)
  pdf :: filegroups/documents recall@1FP-on-slice dropped 3.52pp (10.95% → 7.43%)
  pptx :: filegroups/documents recall@1FP-on-slice dropped 12.31pp (46.15% → 33.85%)
  xlsx :: filegroups/documents recall@1FP-on-slice dropped 23.64pp (55.21% → 31.57%)

1 DEPLOYED-TOLERANCE regression(s) (vs currently-deployed bundle /home/t/.local/share/litmus/models/azoth) — THIS IS WHAT BLOCKS THE DEPLOY:
  - doc: L50 hostile ENSEMBLE recall dropped 4.09pp (99.04% → 94.96%; tolerance 1.70pp; deployed 95% CI lower = 98.66%)

compared 77 filetypes (mal≥1, ben≥1); 2 below threshold and skipped.

blocked by: deployed-tolerance gate (1 filetype(s) regressed vs deployed beyond the 1.70pp tolerance; see list above for the actual drops)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1152: azoth-validate] Error 1)
