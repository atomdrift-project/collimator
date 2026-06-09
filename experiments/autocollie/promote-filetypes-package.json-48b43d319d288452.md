# Promote REJECTED — `48b43d319d288452` on `filetypes/package.json`

Generated 2026-06-09T10:11:43Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-09T10-08-14_20260609T100813-promote-48b43d319d288452_azoth-validate.log; tail: 2026-06-09 06:11:29,226 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-package.json-48b43d319d288452/filetypes/zip already has seed_44.onnx; skipping
2026-06-09 06:11:29,226 INFO found 3 .txt files to convert
2026-06-09 06:11:30,650 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-package.json-48b43d319d288452/filetypes/package.json/models/seed_42.onnx
2026-06-09 06:11:31,796 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-09 06:11:32,865 INFO filetypes/package.json/models/seed_42.txt -> seed_42.onnx OK (delta=8.34e-08 on 200 rows, 3639 ms)
2026-06-09 06:11:32,989 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-package.json-48b43d319d288452/filetypes/package.json/models/seed_43.onnx
2026-06-09 06:11:33,928 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-09 06:11:34,720 INFO filetypes/package.json/models/seed_43.txt -> seed_43.onnx OK (delta=1.33e-07 on 200 rows, 1855 ms)
2026-06-09 06:11:34,818 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-package.json-48b43d319d288452/filetypes/package.json/models/seed_44.onnx
2026-06-09 06:11:35,746 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-09 06:11:37,674 INFO filetypes/package.json/models/seed_44.txt -> seed_44.onnx OK (delta=8.71e-08 on 200 rows, 2953 ms)

converted 3/3 files (0 intentionally skipped, 0 failed)
staged runtime azoth bundle: /tmp/tmp.dBgoFWYYOM
azoth bundle ok: /tmp/tmp.dBgoFWYYOM
--source-bundle out/models/azoth: 1 routes changed → 1 filetypes impacted, 78 unimpacted (drift treated as pre-existing)

per-route regressions (informational; does not block deploy):
  package.json :: filetypes/package.json recall@1FP-on-slice dropped 4.99pp (93.64% → 88.65%)

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

1 DEPLOYED-TOLERANCE regression(s) (vs currently-deployed bundle /home/t/.local/share/litmus/models/azoth) — THIS IS WHAT BLOCKS THE DEPLOY:
  - package.json: L50 hostile ENSEMBLE recall dropped 12.41pp (87.24% → 74.83%; tolerance 1.70pp; deployed 95% CI lower = 85.80%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - package.json: L50 hostile ENSEMBLE recall dropped 11.05pp BELOW LOW-WATER-MARK (85.89% → 74.83%; LWM tolerance 0.90pp)

net-improvement-fallback DID NOT rescue: net malware-caught delta = +6,522 TPs across 76 compared filetypes; worst high-volume drop (>=1500 mal) = 12.41pp on 'package.json' (cap = 5.00pp); worst drop overall = 12.41pp on 'package.json' (small-route, not gated)
  reason: a high-volume filetype cratered (12.41pp on 'package.json', >=1500 malware) exceeds catastrophe cap (5.00pp)

compared 76 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: deployed-tolerance gate (1 filetype(s) regressed vs deployed beyond the 1.70pp tolerance; see list above for the actual drops), low-water-mark gate (1 filetype(s) below LWM beyond the 0.90pp tolerance vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run, or pass --net-improvement-fallback to ship a net-positive deploy whose only regressions are on small routes (below --catastrophe-min-mal). A high-volume filetype cratering past --max-net-route-regression blocks regardless; AZOTH_ALLOW_REGRESSION is the only override for that.
make[1]: *** [Makefile:1317: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9988)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `48b43d319d288452` | `06f365ed02b06e4b` | `08ac769bd7fd6df1` |
| PR AUC | 0.9988 | 0.9989 | 0.9989 |
| ROC AUC | 0.9981 | 0.9984 | 0.9984 |
| F1 | 0.9878 | 0.9945 | 0.9945 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-09T10-08-14_20260609T100813-promote-48b43d319d288452_azoth-validate.log; tail: 2026-06-09 06:11:29,226 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-package.json-48b43d319d288452/filetypes/zip already has seed_44.onnx; skipping
2026-06-09 06:11:29,226 INFO found 3 .txt files to convert
2026-06-09 06:11:30,650 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-package.json-48b43d319d288452/filetypes/package.json/models/seed_42.onnx
2026-06-09 06:11:31,796 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-09 06:11:32,865 INFO filetypes/package.json/models/seed_42.txt -> seed_42.onnx OK (delta=8.34e-08 on 200 rows, 3639 ms)
2026-06-09 06:11:32,989 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-package.json-48b43d319d288452/filetypes/package.json/models/seed_43.onnx
2026-06-09 06:11:33,928 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-09 06:11:34,720 INFO filetypes/package.json/models/seed_43.txt -> seed_43.onnx OK (delta=1.33e-07 on 200 rows, 1855 ms)
2026-06-09 06:11:34,818 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-package.json-48b43d319d288452/filetypes/package.json/models/seed_44.onnx
2026-06-09 06:11:35,746 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-09 06:11:37,674 INFO filetypes/package.json/models/seed_44.txt -> seed_44.onnx OK (delta=8.71e-08 on 200 rows, 2953 ms)

converted 3/3 files (0 intentionally skipped, 0 failed)
staged runtime azoth bundle: /tmp/tmp.dBgoFWYYOM
azoth bundle ok: /tmp/tmp.dBgoFWYYOM
--source-bundle out/models/azoth: 1 routes changed → 1 filetypes impacted, 78 unimpacted (drift treated as pre-existing)

per-route regressions (informational; does not block deploy):
  package.json :: filetypes/package.json recall@1FP-on-slice dropped 4.99pp (93.64% → 88.65%)

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

1 DEPLOYED-TOLERANCE regression(s) (vs currently-deployed bundle /home/t/.local/share/litmus/models/azoth) — THIS IS WHAT BLOCKS THE DEPLOY:
  - package.json: L50 hostile ENSEMBLE recall dropped 12.41pp (87.24% → 74.83%; tolerance 1.70pp; deployed 95% CI lower = 85.80%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - package.json: L50 hostile ENSEMBLE recall dropped 11.05pp BELOW LOW-WATER-MARK (85.89% → 74.83%; LWM tolerance 0.90pp)

net-improvement-fallback DID NOT rescue: net malware-caught delta = +6,522 TPs across 76 compared filetypes; worst high-volume drop (>=1500 mal) = 12.41pp on 'package.json' (cap = 5.00pp); worst drop overall = 12.41pp on 'package.json' (small-route, not gated)
  reason: a high-volume filetype cratered (12.41pp on 'package.json', >=1500 malware) exceeds catastrophe cap (5.00pp)

compared 76 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: deployed-tolerance gate (1 filetype(s) regressed vs deployed beyond the 1.70pp tolerance; see list above for the actual drops), low-water-mark gate (1 filetype(s) below LWM beyond the 0.90pp tolerance vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run, or pass --net-improvement-fallback to ship a net-positive deploy whose only regressions are on small routes (below --catastrophe-min-mal). A high-volume filetype cratering past --max-net-route-regression blocks regardless; AZOTH_ALLOW_REGRESSION is the only override for that.
make[1]: *** [Makefile:1317: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')
