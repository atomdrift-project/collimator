# Promote REJECTED — `9445b9b1b5c81388` on `filetypes/c`

Generated 2026-06-14T21:05:42Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-14T20-57-17_20260614T205631-promote-9445b9b1b5c81388_azoth-validate.log; tail: 2026-06-14 17:05:32,135 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-c-9445b9b1b5c81388/filetypes/zip already has seed_42.onnx; skipping
2026-06-14 17:05:32,135 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-c-9445b9b1b5c81388/filetypes/zip already has seed_43.onnx; skipping
2026-06-14 17:05:32,135 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-c-9445b9b1b5c81388/filetypes/zip already has seed_44.onnx; skipping
2026-06-14 17:05:32,135 INFO found 3 .txt files to convert
2026-06-14 17:05:32,487 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-c-9445b9b1b5c81388/filetypes/c/models/seed_42.onnx
2026-06-14 17:05:32,583 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-14 17:05:33,373 INFO filetypes/c/models/seed_42.txt -> seed_42.onnx OK (delta=1.97e-07 on 200 rows, 1237 ms)
2026-06-14 17:05:33,699 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-c-9445b9b1b5c81388/filetypes/c/models/seed_43.onnx
2026-06-14 17:05:33,747 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-14 17:05:34,511 INFO filetypes/c/models/seed_43.txt -> seed_43.onnx OK (delta=1.32e-07 on 200 rows, 1139 ms)
2026-06-14 17:05:34,843 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-c-9445b9b1b5c81388/filetypes/c/models/seed_44.onnx
2026-06-14 17:05:34,889 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-14 17:05:35,726 INFO filetypes/c/models/seed_44.txt -> seed_44.onnx OK (delta=8.85e-08 on 200 rows, 1215 ms)

converted 3/3 files (0 intentionally skipped, 0 failed)
staged runtime azoth bundle: /tmp/tmp.5PyKzewut5
azoth bundle ok: /tmp/tmp.5PyKzewut5
--source-bundle out/models/azoth: 1 routes changed → 1 filetypes impacted, 82 unimpacted (drift treated as pre-existing)

per-route improvements (≥0.10pp, informational):
  c :: filetypes/c recall@1FP-on-slice +0.55pp (11.15% → 11.70%)

14 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + applescript: L50 hostile ensemble recall +23.08pp above LWM (0.00% → 23.08%)
  + dockerfile: L50 hostile ensemble recall +5.56pp above LWM (0.00% → 5.56%)
  + jar: L50 hostile ensemble recall +8.98pp above LWM (55.51% → 64.49%)
  + jpeg: L50 hostile ensemble recall +6.38pp above LWM (3.85% → 10.23%)
  + objc: L50 hostile ensemble recall +20.00pp above LWM (0.00% → 20.00%)
  + package.json: L50 hostile ensemble recall +3.39pp above LWM (85.89% → 89.28%)
  + pdf: L50 hostile ensemble recall +1.12pp above LWM (4.48% → 5.60%)
  + perl: L50 hostile ensemble recall +4.82pp above LWM (51.28% → 56.10%)
  + php: L50 hostile ensemble recall +4.47pp above LWM (43.22% → 47.69%)
  + pkg-info: L50 hostile ensemble recall +0.94pp above LWM (94.75% → 95.69%)
  + ruby: L50 hostile ensemble recall +1.68pp above LWM (41.18% → 42.86%)
  + vbs: L50 hostile ensemble recall +6.18pp above LWM (56.69% → 62.87%)
  + whl: L50 hostile ensemble recall +33.33pp above LWM (0.00% → 33.33%)
  + xml: L50 hostile ensemble recall +6.95pp above LWM (2.52% → 9.47%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - c: L50 hostile ENSEMBLE recall dropped 1.25pp BELOW LOW-WATER-MARK (9.98% → 8.73%; LWM tolerance 0.90pp)

net-improvement-fallback DID NOT rescue: net malware-caught delta = -2 TPs across 79 compared filetypes; worst high-volume drop (>=1500 mal) = 0.56pp on 'c' (cap = 5.00pp); worst drop overall = 0.56pp on 'c' (small-route, not gated)
  reason: aggregate TP delta is not positive

compared 79 filetypes (mal≥1, ben≥1); 4 below threshold and skipped.

blocked by: low-water-mark gate (1 filetype(s) below LWM beyond the 0.90pp tolerance vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run, or pass --net-improvement-fallback to ship a net-positive deploy whose only regressions are on small routes (below --catastrophe-min-mal). A high-volume filetype cratering past --max-net-route-regression blocks regardless; AZOTH_ALLOW_REGRESSION is the only override for that.
make[2]: *** [Makefile:1321: azoth-validate] Error 1)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9848)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `9445b9b1b5c81388` | `bde7e6275c406640` | `55a9fdfc50ea32aa` |
| PR AUC | 0.9848 | 0.9844 | 0.9842 |
| ROC AUC | 0.9928 | 0.9931 | 0.9931 |
| F1 | 0.9340 | 0.9413 | 0.9446 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-14T20-57-17_20260614T205631-promote-9445b9b1b5c81388_azoth-validate.log; tail: 2026-06-14 17:05:32,135 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-c-9445b9b1b5c81388/filetypes/zip already has seed_42.onnx; skipping
2026-06-14 17:05:32,135 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-c-9445b9b1b5c81388/filetypes/zip already has seed_43.onnx; skipping
2026-06-14 17:05:32,135 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-c-9445b9b1b5c81388/filetypes/zip already has seed_44.onnx; skipping
2026-06-14 17:05:32,135 INFO found 3 .txt files to convert
2026-06-14 17:05:32,487 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-c-9445b9b1b5c81388/filetypes/c/models/seed_42.onnx
2026-06-14 17:05:32,583 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-14 17:05:33,373 INFO filetypes/c/models/seed_42.txt -> seed_42.onnx OK (delta=1.97e-07 on 200 rows, 1237 ms)
2026-06-14 17:05:33,699 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-c-9445b9b1b5c81388/filetypes/c/models/seed_43.onnx
2026-06-14 17:05:33,747 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-14 17:05:34,511 INFO filetypes/c/models/seed_43.txt -> seed_43.onnx OK (delta=1.32e-07 on 200 rows, 1139 ms)
2026-06-14 17:05:34,843 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-c-9445b9b1b5c81388/filetypes/c/models/seed_44.onnx
2026-06-14 17:05:34,889 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-14 17:05:35,726 INFO filetypes/c/models/seed_44.txt -> seed_44.onnx OK (delta=8.85e-08 on 200 rows, 1215 ms)

converted 3/3 files (0 intentionally skipped, 0 failed)
staged runtime azoth bundle: /tmp/tmp.5PyKzewut5
azoth bundle ok: /tmp/tmp.5PyKzewut5
--source-bundle out/models/azoth: 1 routes changed → 1 filetypes impacted, 82 unimpacted (drift treated as pre-existing)

per-route improvements (≥0.10pp, informational):
  c :: filetypes/c recall@1FP-on-slice +0.55pp (11.15% → 11.70%)

14 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + applescript: L50 hostile ensemble recall +23.08pp above LWM (0.00% → 23.08%)
  + dockerfile: L50 hostile ensemble recall +5.56pp above LWM (0.00% → 5.56%)
  + jar: L50 hostile ensemble recall +8.98pp above LWM (55.51% → 64.49%)
  + jpeg: L50 hostile ensemble recall +6.38pp above LWM (3.85% → 10.23%)
  + objc: L50 hostile ensemble recall +20.00pp above LWM (0.00% → 20.00%)
  + package.json: L50 hostile ensemble recall +3.39pp above LWM (85.89% → 89.28%)
  + pdf: L50 hostile ensemble recall +1.12pp above LWM (4.48% → 5.60%)
  + perl: L50 hostile ensemble recall +4.82pp above LWM (51.28% → 56.10%)
  + php: L50 hostile ensemble recall +4.47pp above LWM (43.22% → 47.69%)
  + pkg-info: L50 hostile ensemble recall +0.94pp above LWM (94.75% → 95.69%)
  + ruby: L50 hostile ensemble recall +1.68pp above LWM (41.18% → 42.86%)
  + vbs: L50 hostile ensemble recall +6.18pp above LWM (56.69% → 62.87%)
  + whl: L50 hostile ensemble recall +33.33pp above LWM (0.00% → 33.33%)
  + xml: L50 hostile ensemble recall +6.95pp above LWM (2.52% → 9.47%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - c: L50 hostile ENSEMBLE recall dropped 1.25pp BELOW LOW-WATER-MARK (9.98% → 8.73%; LWM tolerance 0.90pp)

net-improvement-fallback DID NOT rescue: net malware-caught delta = -2 TPs across 79 compared filetypes; worst high-volume drop (>=1500 mal) = 0.56pp on 'c' (cap = 5.00pp); worst drop overall = 0.56pp on 'c' (small-route, not gated)
  reason: aggregate TP delta is not positive

compared 79 filetypes (mal≥1, ben≥1); 4 below threshold and skipped.

blocked by: low-water-mark gate (1 filetype(s) below LWM beyond the 0.90pp tolerance vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run, or pass --net-improvement-fallback to ship a net-positive deploy whose only regressions are on small routes (below --catastrophe-min-mal). A high-volume filetype cratering past --max-net-route-regression blocks regardless; AZOTH_ALLOW_REGRESSION is the only override for that.
make[2]: *** [Makefile:1321: azoth-validate] Error 1)
