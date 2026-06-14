# Promote REJECTED — `19f0b2dd70564c54` on `filetypes/zip`

Generated 2026-06-14T21:19:18Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-14T21-12-20_20260614T211218-promote-19f0b2dd70564c54_azoth-validate.log; tail: 2026-06-14 17:19:05,306 INFO found 3 .txt files to convert
2026-06-14 17:19:06,091 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-zip-19f0b2dd70564c54/filetypes/zip/models/seed_42.onnx
2026-06-14 17:19:06,802 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-14 17:19:08,652 INFO filetypes/zip/models/seed_42.txt -> seed_42.onnx OK (delta=8.93e-08 on 200 rows, 3346 ms)
2026-06-14 17:19:09,222 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-zip-19f0b2dd70564c54/filetypes/zip/models/seed_43.onnx
2026-06-14 17:19:09,834 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-14 17:19:11,533 INFO filetypes/zip/models/seed_43.txt -> seed_43.onnx OK (delta=1.04e-07 on 200 rows, 2881 ms)
2026-06-14 17:19:12,042 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-zip-19f0b2dd70564c54/filetypes/zip/models/seed_44.onnx
2026-06-14 17:19:12,597 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-14 17:19:14,074 INFO filetypes/zip/models/seed_44.txt -> seed_44.onnx OK (delta=9.01e-08 on 200 rows, 2540 ms)

converted 3/3 files (0 intentionally skipped, 0 failed)
staged runtime azoth bundle: /tmp/tmp.3CWYxGmMD0
azoth bundle ok: /tmp/tmp.3CWYxGmMD0
--source-bundle out/models/azoth: 1 routes changed → 1 filetypes impacted, 82 unimpacted (drift treated as pre-existing)

per-route improvements (≥0.10pp, informational):
  zip :: filetypes/zip recall@1FP-on-slice +7.02pp (41.16% → 48.18%)

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

1 DEPLOYED-TOLERANCE regression(s) (vs currently-deployed bundle /home/t/.local/share/atomdrift/scan/models/azoth) — THIS IS WHAT BLOCKS THE DEPLOY:
  - zip: L50 hostile ENSEMBLE recall dropped 3.80pp (31.84% → 28.04%; tolerance 1.70pp; deployed 95% CI lower = 31.03%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - zip: L50 hostile ENSEMBLE recall dropped 6.06pp BELOW LOW-WATER-MARK (34.10% → 28.04%; LWM tolerance 0.90pp)

net-improvement-fallback DID NOT rescue: net malware-caught delta = -481 TPs across 79 compared filetypes; worst high-volume drop (>=1500 mal) = 3.80pp on 'zip' (cap = 5.00pp); worst drop overall = 3.80pp on 'zip' (small-route, not gated)
  reason: aggregate TP delta is not positive

compared 79 filetypes (mal≥1, ben≥1); 4 below threshold and skipped.

blocked by: deployed-tolerance gate (1 filetype(s) regressed vs deployed beyond the 1.70pp tolerance; see list above for the actual drops), low-water-mark gate (1 filetype(s) below LWM beyond the 0.90pp tolerance vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run, or pass --net-improvement-fallback to ship a net-positive deploy whose only regressions are on small routes (below --catastrophe-min-mal). A high-volume filetype cratering past --max-net-route-regression blocks regardless; AZOTH_ALLOW_REGRESSION is the only override for that.
make[2]: *** [Makefile:1321: azoth-validate] Error 1)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9996)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `19f0b2dd70564c54` | `8eee07be53f24512` | `c9499a5c3c65a6b2` |
| PR AUC | 0.9996 | 0.9996 | 0.9997 |
| ROC AUC | 0.9973 | 0.9977 | 0.9978 |
| F1 | 0.9813 | 0.9955 | 0.9956 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-14T21-12-20_20260614T211218-promote-19f0b2dd70564c54_azoth-validate.log; tail: 2026-06-14 17:19:05,306 INFO found 3 .txt files to convert
2026-06-14 17:19:06,091 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-zip-19f0b2dd70564c54/filetypes/zip/models/seed_42.onnx
2026-06-14 17:19:06,802 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-14 17:19:08,652 INFO filetypes/zip/models/seed_42.txt -> seed_42.onnx OK (delta=8.93e-08 on 200 rows, 3346 ms)
2026-06-14 17:19:09,222 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-zip-19f0b2dd70564c54/filetypes/zip/models/seed_43.onnx
2026-06-14 17:19:09,834 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-14 17:19:11,533 INFO filetypes/zip/models/seed_43.txt -> seed_43.onnx OK (delta=1.04e-07 on 200 rows, 2881 ms)
2026-06-14 17:19:12,042 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-zip-19f0b2dd70564c54/filetypes/zip/models/seed_44.onnx
2026-06-14 17:19:12,597 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-14 17:19:14,074 INFO filetypes/zip/models/seed_44.txt -> seed_44.onnx OK (delta=9.01e-08 on 200 rows, 2540 ms)

converted 3/3 files (0 intentionally skipped, 0 failed)
staged runtime azoth bundle: /tmp/tmp.3CWYxGmMD0
azoth bundle ok: /tmp/tmp.3CWYxGmMD0
--source-bundle out/models/azoth: 1 routes changed → 1 filetypes impacted, 82 unimpacted (drift treated as pre-existing)

per-route improvements (≥0.10pp, informational):
  zip :: filetypes/zip recall@1FP-on-slice +7.02pp (41.16% → 48.18%)

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

1 DEPLOYED-TOLERANCE regression(s) (vs currently-deployed bundle /home/t/.local/share/atomdrift/scan/models/azoth) — THIS IS WHAT BLOCKS THE DEPLOY:
  - zip: L50 hostile ENSEMBLE recall dropped 3.80pp (31.84% → 28.04%; tolerance 1.70pp; deployed 95% CI lower = 31.03%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - zip: L50 hostile ENSEMBLE recall dropped 6.06pp BELOW LOW-WATER-MARK (34.10% → 28.04%; LWM tolerance 0.90pp)

net-improvement-fallback DID NOT rescue: net malware-caught delta = -481 TPs across 79 compared filetypes; worst high-volume drop (>=1500 mal) = 3.80pp on 'zip' (cap = 5.00pp); worst drop overall = 3.80pp on 'zip' (small-route, not gated)
  reason: aggregate TP delta is not positive

compared 79 filetypes (mal≥1, ben≥1); 4 below threshold and skipped.

blocked by: deployed-tolerance gate (1 filetype(s) regressed vs deployed beyond the 1.70pp tolerance; see list above for the actual drops), low-water-mark gate (1 filetype(s) below LWM beyond the 0.90pp tolerance vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run, or pass --net-improvement-fallback to ship a net-positive deploy whose only regressions are on small routes (below --catastrophe-min-mal). A high-volume filetype cratering past --max-net-route-regression blocks regardless; AZOTH_ALLOW_REGRESSION is the only override for that.
make[2]: *** [Makefile:1321: azoth-validate] Error 1)
