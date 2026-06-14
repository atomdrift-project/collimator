# Promote REJECTED — `884424e2ef5ff47d` on `filetypes/shell`

Generated 2026-06-13T02:08:19Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-13T02-04-38_20260613T020409-promote-884424e2ef5ff47d_azoth-validate.log; tail: 2026-06-12 22:08:12,019 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-shell-884424e2ef5ff47d/filetypes/shell/models/seed_42.onnx
2026-06-12 22:08:12,471 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-12 22:08:13,242 INFO filetypes/shell/models/seed_42.txt -> seed_42.onnx OK (delta=1.33e-07 on 200 rows, 1553 ms)
2026-06-12 22:08:13,489 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-shell-884424e2ef5ff47d/filetypes/shell/models/seed_43.onnx
2026-06-12 22:08:13,938 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-12 22:08:14,665 INFO filetypes/shell/models/seed_43.txt -> seed_43.onnx OK (delta=8.62e-08 on 200 rows, 1423 ms)
2026-06-12 22:08:14,921 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-shell-884424e2ef5ff47d/filetypes/shell/models/seed_44.onnx
2026-06-12 22:08:15,356 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-12 22:08:16,074 INFO filetypes/shell/models/seed_44.txt -> seed_44.onnx OK (delta=8.21e-08 on 200 rows, 1409 ms)

converted 3/3 files (0 intentionally skipped, 0 failed)
staged runtime azoth bundle: /tmp/tmp.VC35d7KKmf
azoth bundle ok: /tmp/tmp.VC35d7KKmf
--source-bundle out/models/azoth: 1 routes changed → 1 filetypes impacted, 82 unimpacted (drift treated as pre-existing)

per-route regressions (informational; does not block deploy):
  shell :: filetypes/shell recall@1FP-on-slice dropped 2.82pp (75.28% → 72.46%)

13 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + applescript: L50 hostile ensemble recall +23.08pp above LWM (0.00% → 23.08%)
  + dockerfile: L50 hostile ensemble recall +5.56pp above LWM (0.00% → 5.56%)
  + jar: L50 hostile ensemble recall +3.10pp above LWM (55.51% → 58.61%)
  + jpeg: L50 hostile ensemble recall +6.38pp above LWM (3.85% → 10.23%)
  + objc: L50 hostile ensemble recall +20.00pp above LWM (0.00% → 20.00%)
  + package.json: L50 hostile ensemble recall +3.39pp above LWM (85.89% → 89.28%)
  + pdf: L50 hostile ensemble recall +3.39pp above LWM (4.48% → 7.87%)
  + perl: L50 hostile ensemble recall +4.82pp above LWM (51.28% → 56.10%)
  + php: L50 hostile ensemble recall +6.29pp above LWM (43.22% → 49.51%)
  + pkg-info: L50 hostile ensemble recall +0.94pp above LWM (94.75% → 95.69%)
  + ruby: L50 hostile ensemble recall +1.68pp above LWM (41.18% → 42.86%)
  + whl: L50 hostile ensemble recall +37.50pp above LWM (0.00% → 37.50%)
  + xml: L50 hostile ensemble recall +6.95pp above LWM (2.52% → 9.47%)

1 DEPLOYED-TOLERANCE regression(s) (vs currently-deployed bundle /home/t/.local/share/litmus/models/azoth) — THIS IS WHAT BLOCKS THE DEPLOY:
  - shell: L50 hostile ENSEMBLE recall dropped 15.54pp (73.23% → 57.69%; tolerance 1.70pp; deployed 95% CI lower = 71.21%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - shell: L50 hostile ENSEMBLE recall dropped 14.36pp BELOW LOW-WATER-MARK (72.05% → 57.69%; LWM tolerance 0.90pp)

net-improvement-fallback DID NOT rescue: net malware-caught delta = -242 TPs across 78 compared filetypes; worst high-volume drop (>=1500 mal) = 15.54pp on 'shell' (cap = 5.00pp); worst drop overall = 15.54pp on 'shell' (small-route, not gated)
  reason: aggregate TP delta is not positive
  reason: a high-volume filetype cratered (15.54pp on 'shell', >=1500 malware) exceeds catastrophe cap (5.00pp)

compared 78 filetypes (mal≥1, ben≥1); 5 below threshold and skipped.

blocked by: deployed-tolerance gate (1 filetype(s) regressed vs deployed beyond the 1.70pp tolerance; see list above for the actual drops), low-water-mark gate (1 filetype(s) below LWM beyond the 0.90pp tolerance vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run, or pass --net-improvement-fallback to ship a net-positive deploy whose only regressions are on small routes (below --catastrophe-min-mal). A high-volume filetype cratering past --max-net-route-regression blocks regardless; AZOTH_ALLOW_REGRESSION is the only override for that.
make[1]: *** [Makefile:1317: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9974)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `884424e2ef5ff47d` | `c4fa834aef6770a0` | `56b637fb8561a5e9` |
| PR AUC | 0.9974 | 0.9975 | 0.9976 |
| ROC AUC | 0.9975 | 0.9977 | 0.9978 |
| F1 | 0.9759 | 0.9764 | 0.9769 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-13T02-04-38_20260613T020409-promote-884424e2ef5ff47d_azoth-validate.log; tail: 2026-06-12 22:08:12,019 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-shell-884424e2ef5ff47d/filetypes/shell/models/seed_42.onnx
2026-06-12 22:08:12,471 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-12 22:08:13,242 INFO filetypes/shell/models/seed_42.txt -> seed_42.onnx OK (delta=1.33e-07 on 200 rows, 1553 ms)
2026-06-12 22:08:13,489 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-shell-884424e2ef5ff47d/filetypes/shell/models/seed_43.onnx
2026-06-12 22:08:13,938 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-12 22:08:14,665 INFO filetypes/shell/models/seed_43.txt -> seed_43.onnx OK (delta=8.62e-08 on 200 rows, 1423 ms)
2026-06-12 22:08:14,921 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-shell-884424e2ef5ff47d/filetypes/shell/models/seed_44.onnx
2026-06-12 22:08:15,356 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-12 22:08:16,074 INFO filetypes/shell/models/seed_44.txt -> seed_44.onnx OK (delta=8.21e-08 on 200 rows, 1409 ms)

converted 3/3 files (0 intentionally skipped, 0 failed)
staged runtime azoth bundle: /tmp/tmp.VC35d7KKmf
azoth bundle ok: /tmp/tmp.VC35d7KKmf
--source-bundle out/models/azoth: 1 routes changed → 1 filetypes impacted, 82 unimpacted (drift treated as pre-existing)

per-route regressions (informational; does not block deploy):
  shell :: filetypes/shell recall@1FP-on-slice dropped 2.82pp (75.28% → 72.46%)

13 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + applescript: L50 hostile ensemble recall +23.08pp above LWM (0.00% → 23.08%)
  + dockerfile: L50 hostile ensemble recall +5.56pp above LWM (0.00% → 5.56%)
  + jar: L50 hostile ensemble recall +3.10pp above LWM (55.51% → 58.61%)
  + jpeg: L50 hostile ensemble recall +6.38pp above LWM (3.85% → 10.23%)
  + objc: L50 hostile ensemble recall +20.00pp above LWM (0.00% → 20.00%)
  + package.json: L50 hostile ensemble recall +3.39pp above LWM (85.89% → 89.28%)
  + pdf: L50 hostile ensemble recall +3.39pp above LWM (4.48% → 7.87%)
  + perl: L50 hostile ensemble recall +4.82pp above LWM (51.28% → 56.10%)
  + php: L50 hostile ensemble recall +6.29pp above LWM (43.22% → 49.51%)
  + pkg-info: L50 hostile ensemble recall +0.94pp above LWM (94.75% → 95.69%)
  + ruby: L50 hostile ensemble recall +1.68pp above LWM (41.18% → 42.86%)
  + whl: L50 hostile ensemble recall +37.50pp above LWM (0.00% → 37.50%)
  + xml: L50 hostile ensemble recall +6.95pp above LWM (2.52% → 9.47%)

1 DEPLOYED-TOLERANCE regression(s) (vs currently-deployed bundle /home/t/.local/share/litmus/models/azoth) — THIS IS WHAT BLOCKS THE DEPLOY:
  - shell: L50 hostile ENSEMBLE recall dropped 15.54pp (73.23% → 57.69%; tolerance 1.70pp; deployed 95% CI lower = 71.21%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - shell: L50 hostile ENSEMBLE recall dropped 14.36pp BELOW LOW-WATER-MARK (72.05% → 57.69%; LWM tolerance 0.90pp)

net-improvement-fallback DID NOT rescue: net malware-caught delta = -242 TPs across 78 compared filetypes; worst high-volume drop (>=1500 mal) = 15.54pp on 'shell' (cap = 5.00pp); worst drop overall = 15.54pp on 'shell' (small-route, not gated)
  reason: aggregate TP delta is not positive
  reason: a high-volume filetype cratered (15.54pp on 'shell', >=1500 malware) exceeds catastrophe cap (5.00pp)

compared 78 filetypes (mal≥1, ben≥1); 5 below threshold and skipped.

blocked by: deployed-tolerance gate (1 filetype(s) regressed vs deployed beyond the 1.70pp tolerance; see list above for the actual drops), low-water-mark gate (1 filetype(s) below LWM beyond the 0.90pp tolerance vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run, or pass --net-improvement-fallback to ship a net-positive deploy whose only regressions are on small routes (below --catastrophe-min-mal). A high-volume filetype cratering past --max-net-route-regression blocks regardless; AZOTH_ALLOW_REGRESSION is the only override for that.
make[1]: *** [Makefile:1317: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')
