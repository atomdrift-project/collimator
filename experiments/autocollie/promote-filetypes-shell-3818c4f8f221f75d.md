# Promote REJECTED — `3818c4f8f221f75d` on `filetypes/shell`

Generated 2026-06-14T21:44:10Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-14T21-38-23_20260614T213748-promote-3818c4f8f221f75d_azoth-validate.log; tail: 2026-06-14 17:43:58,752 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-shell-3818c4f8f221f75d/filetypes/zip already has seed_42.onnx; skipping
2026-06-14 17:43:58,752 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-shell-3818c4f8f221f75d/filetypes/zip already has seed_43.onnx; skipping
2026-06-14 17:43:58,752 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-shell-3818c4f8f221f75d/filetypes/zip already has seed_44.onnx; skipping
2026-06-14 17:43:58,752 INFO found 3 .txt files to convert
2026-06-14 17:43:59,213 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-shell-3818c4f8f221f75d/filetypes/shell/models/seed_42.onnx
2026-06-14 17:43:59,999 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-14 17:44:00,994 INFO filetypes/shell/models/seed_42.txt -> seed_42.onnx OK (delta=8.74e-08 on 200 rows, 2242 ms)
2026-06-14 17:44:01,324 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-shell-3818c4f8f221f75d/filetypes/shell/models/seed_43.onnx
2026-06-14 17:44:01,854 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-14 17:44:02,819 INFO filetypes/shell/models/seed_43.txt -> seed_43.onnx OK (delta=9.65e-08 on 200 rows, 1825 ms)
2026-06-14 17:44:03,097 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-shell-3818c4f8f221f75d/filetypes/shell/models/seed_44.onnx
2026-06-14 17:44:03,628 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-14 17:44:04,705 INFO filetypes/shell/models/seed_44.txt -> seed_44.onnx OK (delta=8.57e-08 on 200 rows, 1885 ms)

converted 3/3 files (0 intentionally skipped, 0 failed)
staged runtime azoth bundle: /tmp/tmp.tRIwMQKLlY
azoth bundle ok: /tmp/tmp.tRIwMQKLlY
--source-bundle out/models/azoth: 1 routes changed → 1 filetypes impacted, 82 unimpacted (drift treated as pre-existing)

per-route regressions (informational; does not block deploy):
  shell :: filetypes/shell recall@1FP-on-slice dropped 3.44pp (80.92% → 77.49%)

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
  - shell: L50 hostile ENSEMBLE recall dropped 3.13pp BELOW LOW-WATER-MARK (72.05% → 68.92%; LWM tolerance 0.90pp)

net-improvement-fallback DID NOT rescue: net malware-caught delta = -16 TPs across 79 compared filetypes; worst high-volume drop (>=1500 mal) = 1.23pp on 'shell' (cap = 5.00pp); worst drop overall = 1.23pp on 'shell' (small-route, not gated)
  reason: aggregate TP delta is not positive

compared 79 filetypes (mal≥1, ben≥1); 4 below threshold and skipped.

blocked by: low-water-mark gate (1 filetype(s) below LWM beyond the 0.90pp tolerance vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run, or pass --net-improvement-fallback to ship a net-positive deploy whose only regressions are on small routes (below --catastrophe-min-mal). A high-volume filetype cratering past --max-net-route-regression blocks regardless; AZOTH_ALLOW_REGRESSION is the only override for that.
make[2]: *** [Makefile:1321: azoth-validate] Error 1)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9963)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `3818c4f8f221f75d` | `661fb23a048f52c7` | `8c84829b0648f050` |
| PR AUC | 0.9963 | 0.9974 | 0.9974 |
| ROC AUC | 0.9976 | 0.9975 | 0.9974 |
| F1 | 0.9650 | 0.9718 | 0.9711 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-14T21-38-23_20260614T213748-promote-3818c4f8f221f75d_azoth-validate.log; tail: 2026-06-14 17:43:58,752 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-shell-3818c4f8f221f75d/filetypes/zip already has seed_42.onnx; skipping
2026-06-14 17:43:58,752 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-shell-3818c4f8f221f75d/filetypes/zip already has seed_43.onnx; skipping
2026-06-14 17:43:58,752 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-shell-3818c4f8f221f75d/filetypes/zip already has seed_44.onnx; skipping
2026-06-14 17:43:58,752 INFO found 3 .txt files to convert
2026-06-14 17:43:59,213 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-shell-3818c4f8f221f75d/filetypes/shell/models/seed_42.onnx
2026-06-14 17:43:59,999 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-14 17:44:00,994 INFO filetypes/shell/models/seed_42.txt -> seed_42.onnx OK (delta=8.74e-08 on 200 rows, 2242 ms)
2026-06-14 17:44:01,324 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-shell-3818c4f8f221f75d/filetypes/shell/models/seed_43.onnx
2026-06-14 17:44:01,854 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-14 17:44:02,819 INFO filetypes/shell/models/seed_43.txt -> seed_43.onnx OK (delta=9.65e-08 on 200 rows, 1825 ms)
2026-06-14 17:44:03,097 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-shell-3818c4f8f221f75d/filetypes/shell/models/seed_44.onnx
2026-06-14 17:44:03,628 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-14 17:44:04,705 INFO filetypes/shell/models/seed_44.txt -> seed_44.onnx OK (delta=8.57e-08 on 200 rows, 1885 ms)

converted 3/3 files (0 intentionally skipped, 0 failed)
staged runtime azoth bundle: /tmp/tmp.tRIwMQKLlY
azoth bundle ok: /tmp/tmp.tRIwMQKLlY
--source-bundle out/models/azoth: 1 routes changed → 1 filetypes impacted, 82 unimpacted (drift treated as pre-existing)

per-route regressions (informational; does not block deploy):
  shell :: filetypes/shell recall@1FP-on-slice dropped 3.44pp (80.92% → 77.49%)

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
  - shell: L50 hostile ENSEMBLE recall dropped 3.13pp BELOW LOW-WATER-MARK (72.05% → 68.92%; LWM tolerance 0.90pp)

net-improvement-fallback DID NOT rescue: net malware-caught delta = -16 TPs across 79 compared filetypes; worst high-volume drop (>=1500 mal) = 1.23pp on 'shell' (cap = 5.00pp); worst drop overall = 1.23pp on 'shell' (small-route, not gated)
  reason: aggregate TP delta is not positive

compared 79 filetypes (mal≥1, ben≥1); 4 below threshold and skipped.

blocked by: low-water-mark gate (1 filetype(s) below LWM beyond the 0.90pp tolerance vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run, or pass --net-improvement-fallback to ship a net-positive deploy whose only regressions are on small routes (below --catastrophe-min-mal). A high-volume filetype cratering past --max-net-route-regression blocks regardless; AZOTH_ALLOW_REGRESSION is the only override for that.
make[2]: *** [Makefile:1321: azoth-validate] Error 1)
