# Promote REJECTED — `fa684a1ee61f2dbe` on `filetypes/macho`

Generated 2026-06-14T23:44:31Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-14T23-40-36_20260614T234010-promote-fa684a1ee61f2dbe_azoth-validate.log; tail: 2026-06-14 19:44:25,017 INFO found 3 .txt files to convert
2026-06-14 19:44:25,197 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-macho-fa684a1ee61f2dbe/filetypes/macho/models/seed_42.onnx
2026-06-14 19:44:25,347 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-14 19:44:26,130 INFO filetypes/macho/models/seed_42.txt -> seed_42.onnx OK (delta=8.67e-08 on 200 rows, 1112 ms)
2026-06-14 19:44:26,279 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-macho-fa684a1ee61f2dbe/filetypes/macho/models/seed_43.onnx
2026-06-14 19:44:26,404 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-14 19:44:27,179 INFO filetypes/macho/models/seed_43.txt -> seed_43.onnx OK (delta=8.33e-08 on 200 rows, 1049 ms)
2026-06-14 19:44:27,354 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-macho-fa684a1ee61f2dbe/filetypes/macho/models/seed_44.onnx
2026-06-14 19:44:27,476 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-14 19:44:28,224 INFO filetypes/macho/models/seed_44.txt -> seed_44.onnx OK (delta=8.02e-08 on 200 rows, 1045 ms)

converted 3/3 files (0 intentionally skipped, 0 failed)
staged runtime azoth bundle: /tmp/tmp.MskKgD5dpj
azoth bundle ok: /tmp/tmp.MskKgD5dpj
--source-bundle out/models/azoth: 1 routes changed → 1 filetypes impacted, 82 unimpacted (drift treated as pre-existing)

per-route improvements (≥0.10pp, informational):
  macho :: filetypes/macho recall@1FP-on-slice +2.35pp (86.22% → 88.56%)

14 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + applescript: L50 hostile ensemble recall +23.08pp above LWM (0.00% → 23.08%)
  + dockerfile: L50 hostile ensemble recall +5.56pp above LWM (0.00% → 5.56%)
  + jar: L50 hostile ensemble recall +8.98pp above LWM (55.51% → 64.49%)
  + jpeg: L50 hostile ensemble recall +6.38pp above LWM (3.85% → 10.23%)
  + objc: L50 hostile ensemble recall +20.00pp above LWM (0.00% → 20.00%)
  + package.json: L50 hostile ensemble recall +3.39pp above LWM (85.89% → 89.28%)
  + pdf: L50 hostile ensemble recall +1.12pp above LWM (4.48% → 5.60%)
  + perl: L50 hostile ensemble recall +4.82pp above LWM (51.28% → 56.10%)
  + php: L50 hostile ensemble recall +3.91pp above LWM (43.22% → 47.12%)
  + pkg-info: L50 hostile ensemble recall +0.94pp above LWM (94.75% → 95.69%)
  + ruby: L50 hostile ensemble recall +1.68pp above LWM (41.18% → 42.86%)
  + vbs: L50 hostile ensemble recall +6.18pp above LWM (56.69% → 62.87%)
  + whl: L50 hostile ensemble recall +33.33pp above LWM (0.00% → 33.33%)
  + xml: L50 hostile ensemble recall +6.95pp above LWM (2.52% → 9.47%)

1 DEPLOYED-TOLERANCE regression(s) (vs currently-deployed bundle /home/t/.local/share/atomdrift/scan/models/azoth) — THIS IS WHAT BLOCKS THE DEPLOY:
  - macho: L50 hostile ENSEMBLE recall dropped 8.80pp (75.66% → 66.86%; tolerance 1.70pp; deployed 95% CI lower = 70.75%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - macho: L50 hostile ENSEMBLE recall dropped 11.05pp BELOW LOW-WATER-MARK (77.91% → 66.86%; LWM tolerance 0.90pp)

net-improvement-fallback DID NOT rescue: net malware-caught delta = -28 TPs across 79 compared filetypes; worst high-volume drop (>=1500 mal) = 0.00pp on 'none' (cap = 5.00pp); worst drop overall = 8.80pp on 'macho' (small-route, not gated)
  reason: aggregate TP delta is not positive

compared 79 filetypes (mal≥1, ben≥1); 4 below threshold and skipped.

blocked by: deployed-tolerance gate (1 filetype(s) regressed vs deployed beyond the 1.70pp tolerance; see list above for the actual drops), low-water-mark gate (1 filetype(s) below LWM beyond the 0.90pp tolerance vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run, or pass --net-improvement-fallback to ship a net-positive deploy whose only regressions are on small routes (below --catastrophe-min-mal). A high-volume filetype cratering past --max-net-route-regression blocks regardless; AZOTH_ALLOW_REGRESSION is the only override for that.
make[2]: *** [Makefile:1321: azoth-validate] Error 1)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9970)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `fa684a1ee61f2dbe` | `a7e007c50873c773` | `da23d38a8582e133` |
| PR AUC | 0.9970 | 0.9971 | 0.9973 |
| ROC AUC | 0.9994 | 0.9994 | 0.9994 |
| F1 | 0.9700 | 0.9754 | 0.9811 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-14T23-40-36_20260614T234010-promote-fa684a1ee61f2dbe_azoth-validate.log; tail: 2026-06-14 19:44:25,017 INFO found 3 .txt files to convert
2026-06-14 19:44:25,197 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-macho-fa684a1ee61f2dbe/filetypes/macho/models/seed_42.onnx
2026-06-14 19:44:25,347 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-14 19:44:26,130 INFO filetypes/macho/models/seed_42.txt -> seed_42.onnx OK (delta=8.67e-08 on 200 rows, 1112 ms)
2026-06-14 19:44:26,279 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-macho-fa684a1ee61f2dbe/filetypes/macho/models/seed_43.onnx
2026-06-14 19:44:26,404 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-14 19:44:27,179 INFO filetypes/macho/models/seed_43.txt -> seed_43.onnx OK (delta=8.33e-08 on 200 rows, 1049 ms)
2026-06-14 19:44:27,354 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-macho-fa684a1ee61f2dbe/filetypes/macho/models/seed_44.onnx
2026-06-14 19:44:27,476 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-14 19:44:28,224 INFO filetypes/macho/models/seed_44.txt -> seed_44.onnx OK (delta=8.02e-08 on 200 rows, 1045 ms)

converted 3/3 files (0 intentionally skipped, 0 failed)
staged runtime azoth bundle: /tmp/tmp.MskKgD5dpj
azoth bundle ok: /tmp/tmp.MskKgD5dpj
--source-bundle out/models/azoth: 1 routes changed → 1 filetypes impacted, 82 unimpacted (drift treated as pre-existing)

per-route improvements (≥0.10pp, informational):
  macho :: filetypes/macho recall@1FP-on-slice +2.35pp (86.22% → 88.56%)

14 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + applescript: L50 hostile ensemble recall +23.08pp above LWM (0.00% → 23.08%)
  + dockerfile: L50 hostile ensemble recall +5.56pp above LWM (0.00% → 5.56%)
  + jar: L50 hostile ensemble recall +8.98pp above LWM (55.51% → 64.49%)
  + jpeg: L50 hostile ensemble recall +6.38pp above LWM (3.85% → 10.23%)
  + objc: L50 hostile ensemble recall +20.00pp above LWM (0.00% → 20.00%)
  + package.json: L50 hostile ensemble recall +3.39pp above LWM (85.89% → 89.28%)
  + pdf: L50 hostile ensemble recall +1.12pp above LWM (4.48% → 5.60%)
  + perl: L50 hostile ensemble recall +4.82pp above LWM (51.28% → 56.10%)
  + php: L50 hostile ensemble recall +3.91pp above LWM (43.22% → 47.12%)
  + pkg-info: L50 hostile ensemble recall +0.94pp above LWM (94.75% → 95.69%)
  + ruby: L50 hostile ensemble recall +1.68pp above LWM (41.18% → 42.86%)
  + vbs: L50 hostile ensemble recall +6.18pp above LWM (56.69% → 62.87%)
  + whl: L50 hostile ensemble recall +33.33pp above LWM (0.00% → 33.33%)
  + xml: L50 hostile ensemble recall +6.95pp above LWM (2.52% → 9.47%)

1 DEPLOYED-TOLERANCE regression(s) (vs currently-deployed bundle /home/t/.local/share/atomdrift/scan/models/azoth) — THIS IS WHAT BLOCKS THE DEPLOY:
  - macho: L50 hostile ENSEMBLE recall dropped 8.80pp (75.66% → 66.86%; tolerance 1.70pp; deployed 95% CI lower = 70.75%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - macho: L50 hostile ENSEMBLE recall dropped 11.05pp BELOW LOW-WATER-MARK (77.91% → 66.86%; LWM tolerance 0.90pp)

net-improvement-fallback DID NOT rescue: net malware-caught delta = -28 TPs across 79 compared filetypes; worst high-volume drop (>=1500 mal) = 0.00pp on 'none' (cap = 5.00pp); worst drop overall = 8.80pp on 'macho' (small-route, not gated)
  reason: aggregate TP delta is not positive

compared 79 filetypes (mal≥1, ben≥1); 4 below threshold and skipped.

blocked by: deployed-tolerance gate (1 filetype(s) regressed vs deployed beyond the 1.70pp tolerance; see list above for the actual drops), low-water-mark gate (1 filetype(s) below LWM beyond the 0.90pp tolerance vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run, or pass --net-improvement-fallback to ship a net-positive deploy whose only regressions are on small routes (below --catastrophe-min-mal). A high-volume filetype cratering past --max-net-route-regression blocks regardless; AZOTH_ALLOW_REGRESSION is the only override for that.
make[2]: *** [Makefile:1321: azoth-validate] Error 1)
