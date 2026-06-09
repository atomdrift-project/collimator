# Promote REJECTED — `9d5103e79a1c1ca1` on `filetypes/python`

Generated 2026-06-09T16:02:56Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-09T15-59-18_20260609T155917-promote-9d5103e79a1c1ca1_azoth-validate.log; tail: 2026-06-09 12:02:49,071 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-python-9d5103e79a1c1ca1/filetypes/xls already has seed_44.onnx; skipping
2026-06-09 12:02:49,071 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-python-9d5103e79a1c1ca1/filetypes/xlsx already has model.onnx; skipping
2026-06-09 12:02:49,071 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-python-9d5103e79a1c1ca1/filetypes/xml already has model.onnx; skipping
2026-06-09 12:02:49,071 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-python-9d5103e79a1c1ca1/filetypes/zip already has seed_42.onnx; skipping
2026-06-09 12:02:49,071 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-python-9d5103e79a1c1ca1/filetypes/zip already has seed_43.onnx; skipping
2026-06-09 12:02:49,071 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-python-9d5103e79a1c1ca1/filetypes/zip already has seed_44.onnx; skipping
2026-06-09 12:02:49,071 INFO found 3 .txt files to convert
2026-06-09 12:02:49,552 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-python-9d5103e79a1c1ca1/filetypes/python/models/seed_42.onnx
2026-06-09 12:02:49,602 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-09 12:02:50,373 INFO filetypes/python/models/seed_42.txt -> seed_42.onnx OK (delta=8.51e-08 on 200 rows, 1302 ms)
2026-06-09 12:02:50,841 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-python-9d5103e79a1c1ca1/filetypes/python/models/seed_43.onnx
2026-06-09 12:02:50,864 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-09 12:02:51,559 INFO filetypes/python/models/seed_43.txt -> seed_43.onnx OK (delta=8.36e-08 on 200 rows, 1185 ms)
2026-06-09 12:02:52,161 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-python-9d5103e79a1c1ca1/filetypes/python/models/seed_44.onnx
2026-06-09 12:02:52,186 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-09 12:02:52,855 INFO filetypes/python/models/seed_44.txt -> seed_44.onnx OK (delta=7.89e-08 on 200 rows, 1296 ms)

converted 3/3 files (0 intentionally skipped, 0 failed)
staged runtime azoth bundle: /tmp/tmp.hPkQifE0N4
azoth bundle ok: /tmp/tmp.hPkQifE0N4
--source-bundle out/models/azoth: 1 routes changed → 1 filetypes impacted, 79 unimpacted (drift treated as pre-existing)

13 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + applescript: L50 hostile ensemble recall +19.23pp above LWM (0.00% → 19.23%)
  + batch: L50 hostile ensemble recall +1.25pp above LWM (0.96% → 2.22%)
  + crx: L50 hostile ensemble recall +14.94pp above LWM (68.49% → 83.44%)
  + dockerfile: L50 hostile ensemble recall +6.25pp above LWM (0.00% → 6.25%)
  + jpeg: L50 hostile ensemble recall +5.08pp above LWM (3.85% → 8.93%)
  + objc: L50 hostile ensemble recall +20.00pp above LWM (0.00% → 20.00%)
  + ole: L50 hostile ensemble recall +1.18pp above LWM (80.90% → 82.08%)
  + pe: L50 hostile ensemble recall +7.61pp above LWM (56.49% → 64.10%)
  + php: L50 hostile ensemble recall +3.67pp above LWM (43.22% → 46.89%)
  + pkg-info: L50 hostile ensemble recall +1.10pp above LWM (94.75% → 95.85%)
  + rust: L50 hostile ensemble recall +2.16pp above LWM (1.60% → 3.76%)
  + whl: L50 hostile ensemble recall +40.00pp above LWM (0.00% → 40.00%)
  + xml: L50 hostile ensemble recall +11.13pp above LWM (2.52% → 13.65%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - python: L50 hostile ENSEMBLE recall dropped 3.64pp BELOW LOW-WATER-MARK (48.46% → 44.82%; LWM tolerance 0.90pp)

net-improvement-fallback DID NOT rescue: net malware-caught delta = -18 TPs across 76 compared filetypes; worst high-volume drop (>=1500 mal) = 0.00pp on 'none' (cap = 5.00pp); worst drop overall = 0.00pp on '' (small-route, not gated)
  reason: aggregate TP delta is not positive

compared 76 filetypes (mal≥1, ben≥1); 4 below threshold and skipped.

blocked by: low-water-mark gate (1 filetype(s) below LWM beyond the 0.90pp tolerance vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run, or pass --net-improvement-fallback to ship a net-positive deploy whose only regressions are on small routes (below --catastrophe-min-mal). A high-volume filetype cratering past --max-net-route-regression blocks regardless; AZOTH_ALLOW_REGRESSION is the only override for that.
make[1]: *** [Makefile:1317: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9927)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `9d5103e79a1c1ca1` | `e54e06327c9dc8a8` | `d7cc133c3f659c09` |
| PR AUC | 0.9927 | 0.9938 | 0.9938 |
| ROC AUC | 0.9945 | 0.9953 | 0.9953 |
| F1 | 0.9570 | 0.9624 | 0.9609 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-09T15-59-18_20260609T155917-promote-9d5103e79a1c1ca1_azoth-validate.log; tail: 2026-06-09 12:02:49,071 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-python-9d5103e79a1c1ca1/filetypes/xls already has seed_44.onnx; skipping
2026-06-09 12:02:49,071 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-python-9d5103e79a1c1ca1/filetypes/xlsx already has model.onnx; skipping
2026-06-09 12:02:49,071 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-python-9d5103e79a1c1ca1/filetypes/xml already has model.onnx; skipping
2026-06-09 12:02:49,071 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-python-9d5103e79a1c1ca1/filetypes/zip already has seed_42.onnx; skipping
2026-06-09 12:02:49,071 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-python-9d5103e79a1c1ca1/filetypes/zip already has seed_43.onnx; skipping
2026-06-09 12:02:49,071 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-python-9d5103e79a1c1ca1/filetypes/zip already has seed_44.onnx; skipping
2026-06-09 12:02:49,071 INFO found 3 .txt files to convert
2026-06-09 12:02:49,552 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-python-9d5103e79a1c1ca1/filetypes/python/models/seed_42.onnx
2026-06-09 12:02:49,602 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-09 12:02:50,373 INFO filetypes/python/models/seed_42.txt -> seed_42.onnx OK (delta=8.51e-08 on 200 rows, 1302 ms)
2026-06-09 12:02:50,841 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-python-9d5103e79a1c1ca1/filetypes/python/models/seed_43.onnx
2026-06-09 12:02:50,864 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-09 12:02:51,559 INFO filetypes/python/models/seed_43.txt -> seed_43.onnx OK (delta=8.36e-08 on 200 rows, 1185 ms)
2026-06-09 12:02:52,161 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-python-9d5103e79a1c1ca1/filetypes/python/models/seed_44.onnx
2026-06-09 12:02:52,186 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-09 12:02:52,855 INFO filetypes/python/models/seed_44.txt -> seed_44.onnx OK (delta=7.89e-08 on 200 rows, 1296 ms)

converted 3/3 files (0 intentionally skipped, 0 failed)
staged runtime azoth bundle: /tmp/tmp.hPkQifE0N4
azoth bundle ok: /tmp/tmp.hPkQifE0N4
--source-bundle out/models/azoth: 1 routes changed → 1 filetypes impacted, 79 unimpacted (drift treated as pre-existing)

13 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + applescript: L50 hostile ensemble recall +19.23pp above LWM (0.00% → 19.23%)
  + batch: L50 hostile ensemble recall +1.25pp above LWM (0.96% → 2.22%)
  + crx: L50 hostile ensemble recall +14.94pp above LWM (68.49% → 83.44%)
  + dockerfile: L50 hostile ensemble recall +6.25pp above LWM (0.00% → 6.25%)
  + jpeg: L50 hostile ensemble recall +5.08pp above LWM (3.85% → 8.93%)
  + objc: L50 hostile ensemble recall +20.00pp above LWM (0.00% → 20.00%)
  + ole: L50 hostile ensemble recall +1.18pp above LWM (80.90% → 82.08%)
  + pe: L50 hostile ensemble recall +7.61pp above LWM (56.49% → 64.10%)
  + php: L50 hostile ensemble recall +3.67pp above LWM (43.22% → 46.89%)
  + pkg-info: L50 hostile ensemble recall +1.10pp above LWM (94.75% → 95.85%)
  + rust: L50 hostile ensemble recall +2.16pp above LWM (1.60% → 3.76%)
  + whl: L50 hostile ensemble recall +40.00pp above LWM (0.00% → 40.00%)
  + xml: L50 hostile ensemble recall +11.13pp above LWM (2.52% → 13.65%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - python: L50 hostile ENSEMBLE recall dropped 3.64pp BELOW LOW-WATER-MARK (48.46% → 44.82%; LWM tolerance 0.90pp)

net-improvement-fallback DID NOT rescue: net malware-caught delta = -18 TPs across 76 compared filetypes; worst high-volume drop (>=1500 mal) = 0.00pp on 'none' (cap = 5.00pp); worst drop overall = 0.00pp on '' (small-route, not gated)
  reason: aggregate TP delta is not positive

compared 76 filetypes (mal≥1, ben≥1); 4 below threshold and skipped.

blocked by: low-water-mark gate (1 filetype(s) below LWM beyond the 0.90pp tolerance vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run, or pass --net-improvement-fallback to ship a net-positive deploy whose only regressions are on small routes (below --catastrophe-min-mal). A high-volume filetype cratering past --max-net-route-regression blocks regardless; AZOTH_ALLOW_REGRESSION is the only override for that.
make[1]: *** [Makefile:1317: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')
