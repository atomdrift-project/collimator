# Promote REJECTED — `956e522f2c6a5ae2` on `filegroups/scripts`

Generated 2026-06-14T23:02:36Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-14T22-51-22_20260614T224643-promote-956e522f2c6a5ae2_azoth-validate.log; tail: 
per-route improvements (≥0.10pp, informational):
  batch :: filegroups/scripts recall@1FP-on-slice +0.54pp (1.76% → 2.29%)
  php :: filetypes/php recall@1FP-on-slice +3.23pp (44.46% → 47.69%)
  powershell :: filegroups/scripts recall@1FP-on-slice +8.86pp (54.51% → 63.37%)
  powershell :: filetypes/powershell recall@1FP-on-slice +12.85pp (44.31% → 57.16%)
  python :: filegroups/scripts recall@1FP-on-slice +2.25pp (52.76% → 55.01%)
  ruby :: filegroups/scripts recall@1FP-on-slice +19.05pp (19.05% → 38.10%)

per-route regressions (informational; does not block deploy):
  javascript :: filegroups/scripts recall@1FP-on-slice dropped 7.62pp (65.46% → 57.84%)
  perl :: filegroups/scripts recall@1FP-on-slice dropped 2.44pp (63.41% → 60.98%)
  php :: filegroups/scripts recall@1FP-on-slice dropped 9.40pp (55.54% → 46.14%)
  shell :: filegroups/scripts recall@1FP-on-slice dropped 3.59pp (72.46% → 68.87%)

14 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + applescript: L50 hostile ensemble recall +23.08pp above LWM (0.00% → 23.08%)
  + dockerfile: L50 hostile ensemble recall +5.56pp above LWM (0.00% → 5.56%)
  + jar: L50 hostile ensemble recall +8.98pp above LWM (55.51% → 64.49%)
  + jpeg: L50 hostile ensemble recall +6.38pp above LWM (3.85% → 10.23%)
  + objc: L50 hostile ensemble recall +20.00pp above LWM (0.00% → 20.00%)
  + package.json: L50 hostile ensemble recall +3.39pp above LWM (85.89% → 89.28%)
  + pdf: L50 hostile ensemble recall +1.12pp above LWM (4.48% → 5.60%)
  + perl: L50 hostile ensemble recall +2.38pp above LWM (51.28% → 53.66%)
  + php: L50 hostile ensemble recall +0.96pp above LWM (43.22% → 44.18%)
  + pkg-info: L50 hostile ensemble recall +0.94pp above LWM (94.75% → 95.69%)
  + ruby: L50 hostile ensemble recall +1.68pp above LWM (41.18% → 42.86%)
  + vbs: L50 hostile ensemble recall +6.18pp above LWM (56.69% → 62.87%)
  + whl: L50 hostile ensemble recall +33.33pp above LWM (0.00% → 33.33%)
  + xml: L50 hostile ensemble recall +6.95pp above LWM (2.52% → 9.47%)

1 DEPLOYED-TOLERANCE regression(s) (vs currently-deployed bundle /home/t/.local/share/atomdrift/scan/models/azoth) — THIS IS WHAT BLOCKS THE DEPLOY:
  - python: L50 hostile ENSEMBLE recall dropped 4.75pp (48.37% → 43.63%; tolerance 1.70pp; deployed 95% CI lower = 46.51%)

5 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - javascript: L50 hostile ENSEMBLE recall dropped 3.32pp BELOW LOW-WATER-MARK (63.33% → 60.01%; LWM tolerance 0.90pp)
  - lua: L50 hostile ENSEMBLE recall dropped 15.38pp BELOW LOW-WATER-MARK (69.23% → 53.85%; LWM tolerance 0.90pp)
  - powershell: L50 hostile ENSEMBLE recall dropped 3.89pp BELOW LOW-WATER-MARK (53.08% → 49.19%; LWM tolerance 0.90pp)
  - python: L50 hostile ENSEMBLE recall dropped 4.83pp BELOW LOW-WATER-MARK (48.46% → 43.63%; LWM tolerance 0.90pp)
  - shell: L50 hostile ENSEMBLE recall dropped 2.72pp BELOW LOW-WATER-MARK (72.05% → 69.33%; LWM tolerance 0.90pp)

net-improvement-fallback DID NOT rescue: net malware-caught delta = -259 TPs across 79 compared filetypes; worst high-volume drop (>=1500 mal) = 4.75pp on 'python' (cap = 5.00pp); worst drop overall = 4.75pp on 'python' (small-route, not gated)
  reason: aggregate TP delta is not positive

compared 79 filetypes (mal≥1, ben≥1); 4 below threshold and skipped.

blocked by: deployed-tolerance gate (1 filetype(s) regressed vs deployed beyond the 1.70pp tolerance; see list above for the actual drops), low-water-mark gate (5 filetype(s) below LWM beyond the 0.90pp tolerance vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run, or pass --net-improvement-fallback to ship a net-positive deploy whose only regressions are on small routes (below --catastrophe-min-mal). A high-volume filetype cratering past --max-net-route-regression blocks regardless; AZOTH_ALLOW_REGRESSION is the only override for that.
make[2]: *** [Makefile:1321: azoth-validate] Error 1)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9981)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `956e522f2c6a5ae2` | `ed13ea1228e99b96` | `74b2f79612e3d1b0` |
| PR AUC | 0.9981 | 0.9977 | 0.9980 |
| ROC AUC | 0.9979 | 0.9973 | 0.9977 |
| F1 | 0.9787 | 0.9727 | 0.9729 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-14T22-51-22_20260614T224643-promote-956e522f2c6a5ae2_azoth-validate.log; tail: 
per-route improvements (≥0.10pp, informational):
  batch :: filegroups/scripts recall@1FP-on-slice +0.54pp (1.76% → 2.29%)
  php :: filetypes/php recall@1FP-on-slice +3.23pp (44.46% → 47.69%)
  powershell :: filegroups/scripts recall@1FP-on-slice +8.86pp (54.51% → 63.37%)
  powershell :: filetypes/powershell recall@1FP-on-slice +12.85pp (44.31% → 57.16%)
  python :: filegroups/scripts recall@1FP-on-slice +2.25pp (52.76% → 55.01%)
  ruby :: filegroups/scripts recall@1FP-on-slice +19.05pp (19.05% → 38.10%)

per-route regressions (informational; does not block deploy):
  javascript :: filegroups/scripts recall@1FP-on-slice dropped 7.62pp (65.46% → 57.84%)
  perl :: filegroups/scripts recall@1FP-on-slice dropped 2.44pp (63.41% → 60.98%)
  php :: filegroups/scripts recall@1FP-on-slice dropped 9.40pp (55.54% → 46.14%)
  shell :: filegroups/scripts recall@1FP-on-slice dropped 3.59pp (72.46% → 68.87%)

14 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + applescript: L50 hostile ensemble recall +23.08pp above LWM (0.00% → 23.08%)
  + dockerfile: L50 hostile ensemble recall +5.56pp above LWM (0.00% → 5.56%)
  + jar: L50 hostile ensemble recall +8.98pp above LWM (55.51% → 64.49%)
  + jpeg: L50 hostile ensemble recall +6.38pp above LWM (3.85% → 10.23%)
  + objc: L50 hostile ensemble recall +20.00pp above LWM (0.00% → 20.00%)
  + package.json: L50 hostile ensemble recall +3.39pp above LWM (85.89% → 89.28%)
  + pdf: L50 hostile ensemble recall +1.12pp above LWM (4.48% → 5.60%)
  + perl: L50 hostile ensemble recall +2.38pp above LWM (51.28% → 53.66%)
  + php: L50 hostile ensemble recall +0.96pp above LWM (43.22% → 44.18%)
  + pkg-info: L50 hostile ensemble recall +0.94pp above LWM (94.75% → 95.69%)
  + ruby: L50 hostile ensemble recall +1.68pp above LWM (41.18% → 42.86%)
  + vbs: L50 hostile ensemble recall +6.18pp above LWM (56.69% → 62.87%)
  + whl: L50 hostile ensemble recall +33.33pp above LWM (0.00% → 33.33%)
  + xml: L50 hostile ensemble recall +6.95pp above LWM (2.52% → 9.47%)

1 DEPLOYED-TOLERANCE regression(s) (vs currently-deployed bundle /home/t/.local/share/atomdrift/scan/models/azoth) — THIS IS WHAT BLOCKS THE DEPLOY:
  - python: L50 hostile ENSEMBLE recall dropped 4.75pp (48.37% → 43.63%; tolerance 1.70pp; deployed 95% CI lower = 46.51%)

5 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - javascript: L50 hostile ENSEMBLE recall dropped 3.32pp BELOW LOW-WATER-MARK (63.33% → 60.01%; LWM tolerance 0.90pp)
  - lua: L50 hostile ENSEMBLE recall dropped 15.38pp BELOW LOW-WATER-MARK (69.23% → 53.85%; LWM tolerance 0.90pp)
  - powershell: L50 hostile ENSEMBLE recall dropped 3.89pp BELOW LOW-WATER-MARK (53.08% → 49.19%; LWM tolerance 0.90pp)
  - python: L50 hostile ENSEMBLE recall dropped 4.83pp BELOW LOW-WATER-MARK (48.46% → 43.63%; LWM tolerance 0.90pp)
  - shell: L50 hostile ENSEMBLE recall dropped 2.72pp BELOW LOW-WATER-MARK (72.05% → 69.33%; LWM tolerance 0.90pp)

net-improvement-fallback DID NOT rescue: net malware-caught delta = -259 TPs across 79 compared filetypes; worst high-volume drop (>=1500 mal) = 4.75pp on 'python' (cap = 5.00pp); worst drop overall = 4.75pp on 'python' (small-route, not gated)
  reason: aggregate TP delta is not positive

compared 79 filetypes (mal≥1, ben≥1); 4 below threshold and skipped.

blocked by: deployed-tolerance gate (1 filetype(s) regressed vs deployed beyond the 1.70pp tolerance; see list above for the actual drops), low-water-mark gate (5 filetype(s) below LWM beyond the 0.90pp tolerance vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run, or pass --net-improvement-fallback to ship a net-positive deploy whose only regressions are on small routes (below --catastrophe-min-mal). A high-volume filetype cratering past --max-net-route-regression blocks regardless; AZOTH_ALLOW_REGRESSION is the only override for that.
make[2]: *** [Makefile:1321: azoth-validate] Error 1)
