# Promote REJECTED — `a6ab814618a4279e` on `filegroups/native`

Generated 2026-06-09T10:50:36Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-09T10-43-51_20260609T104350-promote-a6ab814618a4279e_azoth-validate.log; tail: 2026-06-09 06:50:29,197 INFO filegroups/native/models/seed_43.txt -> seed_43.onnx OK (delta=9.12e-08 on 200 rows, 3633 ms)
2026-06-09 06:50:30,173 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filegroups-native-a6ab814618a4279e/filegroups/native/models/seed_44.onnx
2026-06-09 06:50:30,296 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-09 06:50:32,882 INFO filegroups/native/models/seed_44.txt -> seed_44.onnx OK (delta=8.43e-08 on 200 rows, 3685 ms)

converted 3/3 files (0 intentionally skipped, 0 failed)
staged runtime azoth bundle: /tmp/tmp.dCq08AUzXK
azoth bundle ok: /tmp/tmp.dCq08AUzXK
--source-bundle out/models/azoth: 1 routes changed → 3 filetypes impacted, 76 unimpacted (drift treated as pre-existing)

per-route improvements (≥0.10pp, informational):
  elf :: filegroups/native recall@1FP-on-slice +1.18pp (92.66% → 93.84%)
  elf :: filetypes/elf recall@1FP-on-slice +0.85pp (96.28% → 97.13%)
  pe :: filetypes/pe recall@1FP-on-slice +14.09pp (50.31% → 64.40%)

per-route regressions (informational; does not block deploy):
  macho :: filegroups/native recall@1FP-on-slice dropped 7.08pp (68.14% → 61.06%)
  pe :: filegroups/native recall@1FP-on-slice dropped 1.90pp (59.89% → 57.98%)

12 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + applescript: L50 hostile ensemble recall +19.23pp above LWM (0.00% → 19.23%)
  + batch: L50 hostile ensemble recall +1.25pp above LWM (0.96% → 2.22%)
  + crx: L50 hostile ensemble recall +14.94pp above LWM (68.49% → 83.44%)
  + dockerfile: L50 hostile ensemble recall +6.25pp above LWM (0.00% → 6.25%)
  + jpeg: L50 hostile ensemble recall +5.08pp above LWM (3.85% → 8.93%)
  + objc: L50 hostile ensemble recall +20.00pp above LWM (0.00% → 20.00%)
  + ole: L50 hostile ensemble recall +1.18pp above LWM (80.90% → 82.08%)
  + pe: L50 hostile ensemble recall +2.42pp above LWM (56.49% → 58.91%)
  + php: L50 hostile ensemble recall +3.67pp above LWM (43.22% → 46.89%)
  + pkg-info: L50 hostile ensemble recall +1.10pp above LWM (94.75% → 95.85%)
  + rust: L50 hostile ensemble recall +2.16pp above LWM (1.60% → 3.76%)
  + xml: L50 hostile ensemble recall +11.13pp above LWM (2.52% → 13.65%)

1 DEPLOYED-TOLERANCE regression(s) (vs currently-deployed bundle /home/t/.local/share/litmus/models/azoth) — THIS IS WHAT BLOCKS THE DEPLOY:
  - elf: L50 hostile ENSEMBLE recall dropped 2.27pp (94.46% → 92.19%; tolerance 1.70pp; deployed 95% CI lower = 94.15%)

2 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - elf: L50 hostile ENSEMBLE recall dropped 1.79pp BELOW LOW-WATER-MARK (93.97% → 92.19%; LWM tolerance 0.90pp)
  - macho: L50 hostile ENSEMBLE recall dropped 5.64pp BELOW LOW-WATER-MARK (77.91% → 72.27%; LWM tolerance 0.90pp)

net-improvement-fallback DID NOT rescue: net malware-caught delta = -1,770 TPs across 76 compared filetypes; worst high-volume drop (>=1500 mal) = 2.27pp on 'elf' (cap = 5.00pp); worst drop overall = 2.65pp on 'macho' (small-route, not gated)
  reason: aggregate TP delta is not positive

compared 76 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: deployed-tolerance gate (1 filetype(s) regressed vs deployed beyond the 1.70pp tolerance; see list above for the actual drops), low-water-mark gate (2 filetype(s) below LWM beyond the 0.90pp tolerance vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run, or pass --net-improvement-fallback to ship a net-positive deploy whose only regressions are on small routes (below --catastrophe-min-mal). A high-volume filetype cratering past --max-net-route-regression blocks regardless; AZOTH_ALLOW_REGRESSION is the only override for that.
make[1]: *** [Makefile:1317: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9993)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `a6ab814618a4279e` | `16e84f161b64801c` | `235560bd36a38bd6` |
| PR AUC | 0.9993 | 1.0000 | 0.9999 |
| ROC AUC | 0.9993 | 0.9999 | 0.9999 |
| F1 | 0.9900 | 0.9985 | 0.9959 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-09T10-43-51_20260609T104350-promote-a6ab814618a4279e_azoth-validate.log; tail: 2026-06-09 06:50:29,197 INFO filegroups/native/models/seed_43.txt -> seed_43.onnx OK (delta=9.12e-08 on 200 rows, 3633 ms)
2026-06-09 06:50:30,173 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filegroups-native-a6ab814618a4279e/filegroups/native/models/seed_44.onnx
2026-06-09 06:50:30,296 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-09 06:50:32,882 INFO filegroups/native/models/seed_44.txt -> seed_44.onnx OK (delta=8.43e-08 on 200 rows, 3685 ms)

converted 3/3 files (0 intentionally skipped, 0 failed)
staged runtime azoth bundle: /tmp/tmp.dCq08AUzXK
azoth bundle ok: /tmp/tmp.dCq08AUzXK
--source-bundle out/models/azoth: 1 routes changed → 3 filetypes impacted, 76 unimpacted (drift treated as pre-existing)

per-route improvements (≥0.10pp, informational):
  elf :: filegroups/native recall@1FP-on-slice +1.18pp (92.66% → 93.84%)
  elf :: filetypes/elf recall@1FP-on-slice +0.85pp (96.28% → 97.13%)
  pe :: filetypes/pe recall@1FP-on-slice +14.09pp (50.31% → 64.40%)

per-route regressions (informational; does not block deploy):
  macho :: filegroups/native recall@1FP-on-slice dropped 7.08pp (68.14% → 61.06%)
  pe :: filegroups/native recall@1FP-on-slice dropped 1.90pp (59.89% → 57.98%)

12 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + applescript: L50 hostile ensemble recall +19.23pp above LWM (0.00% → 19.23%)
  + batch: L50 hostile ensemble recall +1.25pp above LWM (0.96% → 2.22%)
  + crx: L50 hostile ensemble recall +14.94pp above LWM (68.49% → 83.44%)
  + dockerfile: L50 hostile ensemble recall +6.25pp above LWM (0.00% → 6.25%)
  + jpeg: L50 hostile ensemble recall +5.08pp above LWM (3.85% → 8.93%)
  + objc: L50 hostile ensemble recall +20.00pp above LWM (0.00% → 20.00%)
  + ole: L50 hostile ensemble recall +1.18pp above LWM (80.90% → 82.08%)
  + pe: L50 hostile ensemble recall +2.42pp above LWM (56.49% → 58.91%)
  + php: L50 hostile ensemble recall +3.67pp above LWM (43.22% → 46.89%)
  + pkg-info: L50 hostile ensemble recall +1.10pp above LWM (94.75% → 95.85%)
  + rust: L50 hostile ensemble recall +2.16pp above LWM (1.60% → 3.76%)
  + xml: L50 hostile ensemble recall +11.13pp above LWM (2.52% → 13.65%)

1 DEPLOYED-TOLERANCE regression(s) (vs currently-deployed bundle /home/t/.local/share/litmus/models/azoth) — THIS IS WHAT BLOCKS THE DEPLOY:
  - elf: L50 hostile ENSEMBLE recall dropped 2.27pp (94.46% → 92.19%; tolerance 1.70pp; deployed 95% CI lower = 94.15%)

2 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - elf: L50 hostile ENSEMBLE recall dropped 1.79pp BELOW LOW-WATER-MARK (93.97% → 92.19%; LWM tolerance 0.90pp)
  - macho: L50 hostile ENSEMBLE recall dropped 5.64pp BELOW LOW-WATER-MARK (77.91% → 72.27%; LWM tolerance 0.90pp)

net-improvement-fallback DID NOT rescue: net malware-caught delta = -1,770 TPs across 76 compared filetypes; worst high-volume drop (>=1500 mal) = 2.27pp on 'elf' (cap = 5.00pp); worst drop overall = 2.65pp on 'macho' (small-route, not gated)
  reason: aggregate TP delta is not positive

compared 76 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: deployed-tolerance gate (1 filetype(s) regressed vs deployed beyond the 1.70pp tolerance; see list above for the actual drops), low-water-mark gate (2 filetype(s) below LWM beyond the 0.90pp tolerance vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run, or pass --net-improvement-fallback to ship a net-positive deploy whose only regressions are on small routes (below --catastrophe-min-mal). A high-volume filetype cratering past --max-net-route-regression blocks regardless; AZOTH_ALLOW_REGRESSION is the only override for that.
make[1]: *** [Makefile:1317: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')
