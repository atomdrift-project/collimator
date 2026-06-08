# Promote REJECTED — `2888ba6b4ab9e5e8` on `filetypes/tar`

Generated 2026-06-08T16:16:49Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-08T16-13-00_20260608T161259-promote-2888ba6b4ab9e5e8_azoth-validate.log; tail: 2026-06-08 12:16:40,856 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-tar-2888ba6b4ab9e5e8/filetypes/vbs already has model.onnx; skipping
2026-06-08 12:16:40,856 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-tar-2888ba6b4ab9e5e8/filetypes/xls already has seed_42.onnx; skipping
2026-06-08 12:16:40,856 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-tar-2888ba6b4ab9e5e8/filetypes/xls already has seed_43.onnx; skipping
2026-06-08 12:16:40,856 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-tar-2888ba6b4ab9e5e8/filetypes/xls already has seed_44.onnx; skipping
2026-06-08 12:16:40,856 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-tar-2888ba6b4ab9e5e8/filetypes/xlsx already has model.onnx; skipping
2026-06-08 12:16:40,856 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-tar-2888ba6b4ab9e5e8/filetypes/xml already has seed_42.onnx; skipping
2026-06-08 12:16:40,856 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-tar-2888ba6b4ab9e5e8/filetypes/xml already has seed_43.onnx; skipping
2026-06-08 12:16:40,856 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-tar-2888ba6b4ab9e5e8/filetypes/xml already has seed_44.onnx; skipping
2026-06-08 12:16:40,856 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-tar-2888ba6b4ab9e5e8/filetypes/zip already has seed_42.onnx; skipping
2026-06-08 12:16:40,856 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-tar-2888ba6b4ab9e5e8/filetypes/zip already has seed_43.onnx; skipping
2026-06-08 12:16:40,856 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-tar-2888ba6b4ab9e5e8/filetypes/zip already has seed_44.onnx; skipping
2026-06-08 12:16:40,856 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-tar-2888ba6b4ab9e5e8/filetypes/zst already has seed_42.onnx; skipping
2026-06-08 12:16:40,856 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-tar-2888ba6b4ab9e5e8/filetypes/zst already has seed_43.onnx; skipping
2026-06-08 12:16:40,856 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-tar-2888ba6b4ab9e5e8/filetypes/zst already has seed_44.onnx; skipping
2026-06-08 12:16:40,856 INFO found 3 .txt files to convert
2026-06-08 12:16:40,942 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-tar-2888ba6b4ab9e5e8/filetypes/tar/models/seed_42.onnx
2026-06-08 12:16:41,085 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-08 12:16:42,470 INFO filetypes/tar/models/seed_42.txt -> seed_42.onnx OK (delta=1.43e-07 on 200 rows, 1613 ms)
2026-06-08 12:16:42,502 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-tar-2888ba6b4ab9e5e8/filetypes/tar/models/seed_43.onnx
2026-06-08 12:16:42,549 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-08 12:16:43,941 INFO filetypes/tar/models/seed_43.txt -> seed_43.onnx OK (delta=9.53e-08 on 200 rows, 1471 ms)
2026-06-08 12:16:43,960 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-tar-2888ba6b4ab9e5e8/filetypes/tar/models/seed_44.onnx
2026-06-08 12:16:44,010 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-08 12:16:45,340 INFO filetypes/tar/models/seed_44.txt -> seed_44.onnx OK (delta=1.18e-07 on 200 rows, 1398 ms)

converted 3/3 files (0 intentionally skipped, 0 failed)
staged runtime azoth bundle: /tmp/tmp.1kJ69Ojnib
azoth bundle ok: /tmp/tmp.1kJ69Ojnib
--source-bundle out/models/azoth: 1 routes changed → 1 filetypes impacted, 77 unimpacted (drift treated as pre-existing)

per-route regressions (informational; does not block deploy):
  tar :: filetypes/tar recall@1FP-on-slice dropped 40.56pp (88.43% → 47.87%)

1 DEPLOYED-TOLERANCE regression(s) (vs currently-deployed bundle /home/t/.local/share/litmus/models/azoth) — THIS IS WHAT BLOCKS THE DEPLOY:
  - tar: L50 hostile ENSEMBLE recall dropped 14.60pp (86.30% → 71.70%; tolerance 1.70pp; deployed 95% CI lower = 84.97%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - tar: L50 hostile ENSEMBLE recall dropped 14.60pp BELOW LOW-WATER-MARK (86.30% → 71.70%; LWM tolerance 0.90pp)

net-improvement-fallback DID NOT rescue: net malware-caught delta = -405 TPs across 75 compared filetypes; worst high-volume drop (>=1500 mal) = 14.60pp on 'tar' (cap = 5.00pp); worst drop overall = 14.60pp on 'tar' (small-route, not gated)
  reason: aggregate TP delta is not positive
  reason: a high-volume filetype cratered (14.60pp on 'tar', >=1500 malware) exceeds catastrophe cap (5.00pp)

compared 75 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: deployed-tolerance gate (1 filetype(s) regressed vs deployed beyond the 1.70pp tolerance; see list above for the actual drops), low-water-mark gate (1 filetype(s) below LWM beyond the 0.90pp tolerance vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run, or pass --net-improvement-fallback to ship a net-positive deploy whose only regressions are on small routes (below --catastrophe-min-mal). A high-volume filetype cratering past --max-net-route-regression blocks regardless; AZOTH_ALLOW_REGRESSION is the only override for that.
make[1]: *** [Makefile:1317: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9968)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `2888ba6b4ab9e5e8` | `9deb7a8e9d342a6c` | `f772ca0e315325ab` |
| PR AUC | 0.9968 | 0.9967 | 0.9973 |
| ROC AUC | 0.9894 | 0.9890 | 0.9910 |
| F1 | 0.9356 | 0.9426 | 0.9521 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-08T16-13-00_20260608T161259-promote-2888ba6b4ab9e5e8_azoth-validate.log; tail: 2026-06-08 12:16:40,856 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-tar-2888ba6b4ab9e5e8/filetypes/vbs already has model.onnx; skipping
2026-06-08 12:16:40,856 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-tar-2888ba6b4ab9e5e8/filetypes/xls already has seed_42.onnx; skipping
2026-06-08 12:16:40,856 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-tar-2888ba6b4ab9e5e8/filetypes/xls already has seed_43.onnx; skipping
2026-06-08 12:16:40,856 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-tar-2888ba6b4ab9e5e8/filetypes/xls already has seed_44.onnx; skipping
2026-06-08 12:16:40,856 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-tar-2888ba6b4ab9e5e8/filetypes/xlsx already has model.onnx; skipping
2026-06-08 12:16:40,856 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-tar-2888ba6b4ab9e5e8/filetypes/xml already has seed_42.onnx; skipping
2026-06-08 12:16:40,856 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-tar-2888ba6b4ab9e5e8/filetypes/xml already has seed_43.onnx; skipping
2026-06-08 12:16:40,856 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-tar-2888ba6b4ab9e5e8/filetypes/xml already has seed_44.onnx; skipping
2026-06-08 12:16:40,856 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-tar-2888ba6b4ab9e5e8/filetypes/zip already has seed_42.onnx; skipping
2026-06-08 12:16:40,856 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-tar-2888ba6b4ab9e5e8/filetypes/zip already has seed_43.onnx; skipping
2026-06-08 12:16:40,856 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-tar-2888ba6b4ab9e5e8/filetypes/zip already has seed_44.onnx; skipping
2026-06-08 12:16:40,856 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-tar-2888ba6b4ab9e5e8/filetypes/zst already has seed_42.onnx; skipping
2026-06-08 12:16:40,856 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-tar-2888ba6b4ab9e5e8/filetypes/zst already has seed_43.onnx; skipping
2026-06-08 12:16:40,856 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-tar-2888ba6b4ab9e5e8/filetypes/zst already has seed_44.onnx; skipping
2026-06-08 12:16:40,856 INFO found 3 .txt files to convert
2026-06-08 12:16:40,942 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-tar-2888ba6b4ab9e5e8/filetypes/tar/models/seed_42.onnx
2026-06-08 12:16:41,085 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-08 12:16:42,470 INFO filetypes/tar/models/seed_42.txt -> seed_42.onnx OK (delta=1.43e-07 on 200 rows, 1613 ms)
2026-06-08 12:16:42,502 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-tar-2888ba6b4ab9e5e8/filetypes/tar/models/seed_43.onnx
2026-06-08 12:16:42,549 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-08 12:16:43,941 INFO filetypes/tar/models/seed_43.txt -> seed_43.onnx OK (delta=9.53e-08 on 200 rows, 1471 ms)
2026-06-08 12:16:43,960 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-tar-2888ba6b4ab9e5e8/filetypes/tar/models/seed_44.onnx
2026-06-08 12:16:44,010 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-08 12:16:45,340 INFO filetypes/tar/models/seed_44.txt -> seed_44.onnx OK (delta=1.18e-07 on 200 rows, 1398 ms)

converted 3/3 files (0 intentionally skipped, 0 failed)
staged runtime azoth bundle: /tmp/tmp.1kJ69Ojnib
azoth bundle ok: /tmp/tmp.1kJ69Ojnib
--source-bundle out/models/azoth: 1 routes changed → 1 filetypes impacted, 77 unimpacted (drift treated as pre-existing)

per-route regressions (informational; does not block deploy):
  tar :: filetypes/tar recall@1FP-on-slice dropped 40.56pp (88.43% → 47.87%)

1 DEPLOYED-TOLERANCE regression(s) (vs currently-deployed bundle /home/t/.local/share/litmus/models/azoth) — THIS IS WHAT BLOCKS THE DEPLOY:
  - tar: L50 hostile ENSEMBLE recall dropped 14.60pp (86.30% → 71.70%; tolerance 1.70pp; deployed 95% CI lower = 84.97%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - tar: L50 hostile ENSEMBLE recall dropped 14.60pp BELOW LOW-WATER-MARK (86.30% → 71.70%; LWM tolerance 0.90pp)

net-improvement-fallback DID NOT rescue: net malware-caught delta = -405 TPs across 75 compared filetypes; worst high-volume drop (>=1500 mal) = 14.60pp on 'tar' (cap = 5.00pp); worst drop overall = 14.60pp on 'tar' (small-route, not gated)
  reason: aggregate TP delta is not positive
  reason: a high-volume filetype cratered (14.60pp on 'tar', >=1500 malware) exceeds catastrophe cap (5.00pp)

compared 75 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: deployed-tolerance gate (1 filetype(s) regressed vs deployed beyond the 1.70pp tolerance; see list above for the actual drops), low-water-mark gate (1 filetype(s) below LWM beyond the 0.90pp tolerance vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run, or pass --net-improvement-fallback to ship a net-positive deploy whose only regressions are on small routes (below --catastrophe-min-mal). A high-volume filetype cratering past --max-net-route-regression blocks regardless; AZOTH_ALLOW_REGRESSION is the only override for that.
make[1]: *** [Makefile:1317: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')
