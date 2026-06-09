# Promote REJECTED — `f97a49a39578f34a` on `filetypes/csharp`

Generated 2026-06-09T13:46:25Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-09T13-42-39_20260609T134227-promote-f97a49a39578f34a_azoth-validate.log; tail: 2026-06-09 09:46:15,920 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-csharp-f97a49a39578f34a/filetypes/xls already has seed_43.onnx; skipping
2026-06-09 09:46:15,920 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-csharp-f97a49a39578f34a/filetypes/xls already has seed_44.onnx; skipping
2026-06-09 09:46:15,920 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-csharp-f97a49a39578f34a/filetypes/xlsx already has model.onnx; skipping
2026-06-09 09:46:15,920 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-csharp-f97a49a39578f34a/filetypes/xml already has model.onnx; skipping
2026-06-09 09:46:15,920 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-csharp-f97a49a39578f34a/filetypes/zip already has seed_42.onnx; skipping
2026-06-09 09:46:15,920 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-csharp-f97a49a39578f34a/filetypes/zip already has seed_43.onnx; skipping
2026-06-09 09:46:15,920 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-csharp-f97a49a39578f34a/filetypes/zip already has seed_44.onnx; skipping
2026-06-09 09:46:15,920 INFO found 3 .txt files to convert
2026-06-09 09:46:16,030 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-csharp-f97a49a39578f34a/filetypes/csharp/models/seed_42.onnx
2026-06-09 09:46:17,664 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-09 09:46:18,460 INFO filetypes/csharp/models/seed_42.txt -> seed_42.onnx OK (delta=6.20e-08 on 200 rows, 2540 ms)
2026-06-09 09:46:18,497 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-csharp-f97a49a39578f34a/filetypes/csharp/models/seed_43.onnx
2026-06-09 09:46:19,337 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-09 09:46:20,066 INFO filetypes/csharp/models/seed_43.txt -> seed_43.onnx OK (delta=7.10e-08 on 200 rows, 1606 ms)
2026-06-09 09:46:20,148 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-csharp-f97a49a39578f34a/filetypes/csharp/models/seed_44.onnx
2026-06-09 09:46:20,950 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-09 09:46:21,762 INFO filetypes/csharp/models/seed_44.txt -> seed_44.onnx OK (delta=5.81e-08 on 200 rows, 1697 ms)

converted 3/3 files (0 intentionally skipped, 0 failed)
staged runtime azoth bundle: /tmp/tmp.QhstR0Rkha
azoth bundle ok: /tmp/tmp.QhstR0Rkha
--source-bundle out/models/azoth: 1 routes changed → 1 filetypes impacted, 78 unimpacted (drift treated as pre-existing)

12 low-water-mark improvement(s) (>0.90pp above LWM, informational):
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
  + xml: L50 hostile ensemble recall +11.13pp above LWM (2.52% → 13.65%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - csharp: L50 hostile ENSEMBLE recall dropped 3.06pp BELOW LOW-WATER-MARK (17.09% → 14.03%; LWM tolerance 0.90pp)

net-improvement-fallback DID NOT rescue: net malware-caught delta = -2 TPs across 76 compared filetypes; worst high-volume drop (>=1500 mal) = 0.00pp on 'none' (cap = 5.00pp); worst drop overall = 0.51pp on 'csharp' (small-route, not gated)
  reason: aggregate TP delta is not positive

compared 76 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: low-water-mark gate (1 filetype(s) below LWM beyond the 0.90pp tolerance vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run, or pass --net-improvement-fallback to ship a net-positive deploy whose only regressions are on small routes (below --catastrophe-min-mal). A high-volume filetype cratering past --max-net-route-regression blocks regardless; AZOTH_ALLOW_REGRESSION is the only override for that.
make[1]: *** [Makefile:1317: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.4899)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `f97a49a39578f34a` | `916a89c0cec1b69c` | `bab9b5e2892b5460` |
| PR AUC | 0.4899 | 0.5311 | 0.5353 |
| ROC AUC | 0.9276 | 0.9377 | 0.9373 |
| F1 | 0.3636 | 0.4454 | 0.4557 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-09T13-42-39_20260609T134227-promote-f97a49a39578f34a_azoth-validate.log; tail: 2026-06-09 09:46:15,920 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-csharp-f97a49a39578f34a/filetypes/xls already has seed_43.onnx; skipping
2026-06-09 09:46:15,920 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-csharp-f97a49a39578f34a/filetypes/xls already has seed_44.onnx; skipping
2026-06-09 09:46:15,920 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-csharp-f97a49a39578f34a/filetypes/xlsx already has model.onnx; skipping
2026-06-09 09:46:15,920 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-csharp-f97a49a39578f34a/filetypes/xml already has model.onnx; skipping
2026-06-09 09:46:15,920 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-csharp-f97a49a39578f34a/filetypes/zip already has seed_42.onnx; skipping
2026-06-09 09:46:15,920 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-csharp-f97a49a39578f34a/filetypes/zip already has seed_43.onnx; skipping
2026-06-09 09:46:15,920 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-csharp-f97a49a39578f34a/filetypes/zip already has seed_44.onnx; skipping
2026-06-09 09:46:15,920 INFO found 3 .txt files to convert
2026-06-09 09:46:16,030 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-csharp-f97a49a39578f34a/filetypes/csharp/models/seed_42.onnx
2026-06-09 09:46:17,664 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-09 09:46:18,460 INFO filetypes/csharp/models/seed_42.txt -> seed_42.onnx OK (delta=6.20e-08 on 200 rows, 2540 ms)
2026-06-09 09:46:18,497 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-csharp-f97a49a39578f34a/filetypes/csharp/models/seed_43.onnx
2026-06-09 09:46:19,337 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-09 09:46:20,066 INFO filetypes/csharp/models/seed_43.txt -> seed_43.onnx OK (delta=7.10e-08 on 200 rows, 1606 ms)
2026-06-09 09:46:20,148 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-csharp-f97a49a39578f34a/filetypes/csharp/models/seed_44.onnx
2026-06-09 09:46:20,950 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-09 09:46:21,762 INFO filetypes/csharp/models/seed_44.txt -> seed_44.onnx OK (delta=5.81e-08 on 200 rows, 1697 ms)

converted 3/3 files (0 intentionally skipped, 0 failed)
staged runtime azoth bundle: /tmp/tmp.QhstR0Rkha
azoth bundle ok: /tmp/tmp.QhstR0Rkha
--source-bundle out/models/azoth: 1 routes changed → 1 filetypes impacted, 78 unimpacted (drift treated as pre-existing)

12 low-water-mark improvement(s) (>0.90pp above LWM, informational):
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
  + xml: L50 hostile ensemble recall +11.13pp above LWM (2.52% → 13.65%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - csharp: L50 hostile ENSEMBLE recall dropped 3.06pp BELOW LOW-WATER-MARK (17.09% → 14.03%; LWM tolerance 0.90pp)

net-improvement-fallback DID NOT rescue: net malware-caught delta = -2 TPs across 76 compared filetypes; worst high-volume drop (>=1500 mal) = 0.00pp on 'none' (cap = 5.00pp); worst drop overall = 0.51pp on 'csharp' (small-route, not gated)
  reason: aggregate TP delta is not positive

compared 76 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: low-water-mark gate (1 filetype(s) below LWM beyond the 0.90pp tolerance vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run, or pass --net-improvement-fallback to ship a net-positive deploy whose only regressions are on small routes (below --catastrophe-min-mal). A high-volume filetype cratering past --max-net-route-regression blocks regardless; AZOTH_ALLOW_REGRESSION is the only override for that.
make[1]: *** [Makefile:1317: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')
