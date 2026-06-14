# Promote REJECTED — `e37f927afbd32e67` on `filegroups/scripts`

Generated 2026-06-14T22:04:34Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-14T21-53-26_20260614T214853-promote-e37f927afbd32e67_azoth-validate.log; tail:   powershell: L50 hostile ensemble recall +1.62pp (50.81% → 52.44%)

per-route improvements (≥0.10pp, informational):
  batch :: filegroups/scripts recall@1FP-on-slice +0.46pp (1.76% → 2.21%)
  powershell :: filegroups/scripts recall@1FP-on-slice +5.17pp (54.51% → 59.68%)
  powershell :: filetypes/powershell recall@1FP-on-slice +12.85pp (44.31% → 57.16%)
  python :: filegroups/scripts recall@1FP-on-slice +2.50pp (52.76% → 55.26%)
  ruby :: filegroups/scripts recall@1FP-on-slice +19.05pp (19.05% → 38.10%)

per-route regressions (informational; does not block deploy):
  javascript :: filegroups/scripts recall@1FP-on-slice dropped 3.03pp (65.46% → 62.44%)
  perl :: filegroups/scripts recall@1FP-on-slice dropped 2.44pp (63.41% → 60.98%)
  php :: filegroups/scripts recall@1FP-on-slice dropped 5.05pp (55.54% → 50.49%)
  shell :: filegroups/scripts recall@1FP-on-slice dropped 7.54pp (72.46% → 64.92%)

14 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + applescript: L50 hostile ensemble recall +23.08pp above LWM (0.00% → 23.08%)
  + batch: L50 hostile ensemble recall +1.17pp above LWM (0.96% → 2.13%)
  + dockerfile: L50 hostile ensemble recall +5.56pp above LWM (0.00% → 5.56%)
  + jar: L50 hostile ensemble recall +8.98pp above LWM (55.51% → 64.49%)
  + jpeg: L50 hostile ensemble recall +6.38pp above LWM (3.85% → 10.23%)
  + objc: L50 hostile ensemble recall +20.00pp above LWM (0.00% → 20.00%)
  + package.json: L50 hostile ensemble recall +3.39pp above LWM (85.89% → 89.28%)
  + pdf: L50 hostile ensemble recall +1.12pp above LWM (4.48% → 5.60%)
  + php: L50 hostile ensemble recall +3.34pp above LWM (43.22% → 46.56%)
  + pkg-info: L50 hostile ensemble recall +0.94pp above LWM (94.75% → 95.69%)
  + ruby: L50 hostile ensemble recall +1.68pp above LWM (41.18% → 42.86%)
  + vbs: L50 hostile ensemble recall +6.18pp above LWM (56.69% → 62.87%)
  + whl: L50 hostile ensemble recall +33.33pp above LWM (0.00% → 33.33%)
  + xml: L50 hostile ensemble recall +6.95pp above LWM (2.52% → 9.47%)

2 DEPLOYED-TOLERANCE regression(s) (vs currently-deployed bundle /home/t/.local/share/atomdrift/scan/models/azoth) — THIS IS WHAT BLOCKS THE DEPLOY:
  - python: L50 hostile ENSEMBLE recall dropped 4.92pp (48.37% → 43.45%; tolerance 1.70pp; deployed 95% CI lower = 46.51%)
  - shell: L50 hostile ENSEMBLE recall dropped 2.87pp (70.15% → 67.28%; tolerance 1.70pp; deployed 95% CI lower = 68.07%)

4 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - javascript: L50 hostile ENSEMBLE recall dropped 3.26pp BELOW LOW-WATER-MARK (63.33% → 60.07%; LWM tolerance 0.90pp)
  - lua: L50 hostile ENSEMBLE recall dropped 23.08pp BELOW LOW-WATER-MARK (69.23% → 46.15%; LWM tolerance 0.90pp)
  - python: L50 hostile ENSEMBLE recall dropped 5.01pp BELOW LOW-WATER-MARK (48.46% → 43.45%; LWM tolerance 0.90pp)
  - shell: L50 hostile ENSEMBLE recall dropped 4.77pp BELOW LOW-WATER-MARK (72.05% → 67.28%; LWM tolerance 0.90pp)

net-improvement-fallback DID NOT rescue: net malware-caught delta = -131 TPs across 79 compared filetypes; worst high-volume drop (>=1500 mal) = 4.92pp on 'python' (cap = 5.00pp); worst drop overall = 4.92pp on 'python' (small-route, not gated)
  reason: aggregate TP delta is not positive

compared 79 filetypes (mal≥1, ben≥1); 4 below threshold and skipped.

blocked by: deployed-tolerance gate (2 filetype(s) regressed vs deployed beyond the 1.70pp tolerance; see list above for the actual drops), low-water-mark gate (4 filetype(s) below LWM beyond the 0.90pp tolerance vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run, or pass --net-improvement-fallback to ship a net-positive deploy whose only regressions are on small routes (below --catastrophe-min-mal). A high-volume filetype cratering past --max-net-route-regression blocks regardless; AZOTH_ALLOW_REGRESSION is the only override for that.
make[2]: *** [Makefile:1321: azoth-validate] Error 1)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9970)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `e37f927afbd32e67` | `670eda909ab4340b` | `a0abad5f5c238143` |
| PR AUC | 0.9970 | 0.9982 | 0.9982 |
| ROC AUC | 0.9964 | 0.9979 | 0.9979 |
| F1 | 0.9723 | 0.9806 | 0.9800 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-14T21-53-26_20260614T214853-promote-e37f927afbd32e67_azoth-validate.log; tail:   powershell: L50 hostile ensemble recall +1.62pp (50.81% → 52.44%)

per-route improvements (≥0.10pp, informational):
  batch :: filegroups/scripts recall@1FP-on-slice +0.46pp (1.76% → 2.21%)
  powershell :: filegroups/scripts recall@1FP-on-slice +5.17pp (54.51% → 59.68%)
  powershell :: filetypes/powershell recall@1FP-on-slice +12.85pp (44.31% → 57.16%)
  python :: filegroups/scripts recall@1FP-on-slice +2.50pp (52.76% → 55.26%)
  ruby :: filegroups/scripts recall@1FP-on-slice +19.05pp (19.05% → 38.10%)

per-route regressions (informational; does not block deploy):
  javascript :: filegroups/scripts recall@1FP-on-slice dropped 3.03pp (65.46% → 62.44%)
  perl :: filegroups/scripts recall@1FP-on-slice dropped 2.44pp (63.41% → 60.98%)
  php :: filegroups/scripts recall@1FP-on-slice dropped 5.05pp (55.54% → 50.49%)
  shell :: filegroups/scripts recall@1FP-on-slice dropped 7.54pp (72.46% → 64.92%)

14 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + applescript: L50 hostile ensemble recall +23.08pp above LWM (0.00% → 23.08%)
  + batch: L50 hostile ensemble recall +1.17pp above LWM (0.96% → 2.13%)
  + dockerfile: L50 hostile ensemble recall +5.56pp above LWM (0.00% → 5.56%)
  + jar: L50 hostile ensemble recall +8.98pp above LWM (55.51% → 64.49%)
  + jpeg: L50 hostile ensemble recall +6.38pp above LWM (3.85% → 10.23%)
  + objc: L50 hostile ensemble recall +20.00pp above LWM (0.00% → 20.00%)
  + package.json: L50 hostile ensemble recall +3.39pp above LWM (85.89% → 89.28%)
  + pdf: L50 hostile ensemble recall +1.12pp above LWM (4.48% → 5.60%)
  + php: L50 hostile ensemble recall +3.34pp above LWM (43.22% → 46.56%)
  + pkg-info: L50 hostile ensemble recall +0.94pp above LWM (94.75% → 95.69%)
  + ruby: L50 hostile ensemble recall +1.68pp above LWM (41.18% → 42.86%)
  + vbs: L50 hostile ensemble recall +6.18pp above LWM (56.69% → 62.87%)
  + whl: L50 hostile ensemble recall +33.33pp above LWM (0.00% → 33.33%)
  + xml: L50 hostile ensemble recall +6.95pp above LWM (2.52% → 9.47%)

2 DEPLOYED-TOLERANCE regression(s) (vs currently-deployed bundle /home/t/.local/share/atomdrift/scan/models/azoth) — THIS IS WHAT BLOCKS THE DEPLOY:
  - python: L50 hostile ENSEMBLE recall dropped 4.92pp (48.37% → 43.45%; tolerance 1.70pp; deployed 95% CI lower = 46.51%)
  - shell: L50 hostile ENSEMBLE recall dropped 2.87pp (70.15% → 67.28%; tolerance 1.70pp; deployed 95% CI lower = 68.07%)

4 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - javascript: L50 hostile ENSEMBLE recall dropped 3.26pp BELOW LOW-WATER-MARK (63.33% → 60.07%; LWM tolerance 0.90pp)
  - lua: L50 hostile ENSEMBLE recall dropped 23.08pp BELOW LOW-WATER-MARK (69.23% → 46.15%; LWM tolerance 0.90pp)
  - python: L50 hostile ENSEMBLE recall dropped 5.01pp BELOW LOW-WATER-MARK (48.46% → 43.45%; LWM tolerance 0.90pp)
  - shell: L50 hostile ENSEMBLE recall dropped 4.77pp BELOW LOW-WATER-MARK (72.05% → 67.28%; LWM tolerance 0.90pp)

net-improvement-fallback DID NOT rescue: net malware-caught delta = -131 TPs across 79 compared filetypes; worst high-volume drop (>=1500 mal) = 4.92pp on 'python' (cap = 5.00pp); worst drop overall = 4.92pp on 'python' (small-route, not gated)
  reason: aggregate TP delta is not positive

compared 79 filetypes (mal≥1, ben≥1); 4 below threshold and skipped.

blocked by: deployed-tolerance gate (2 filetype(s) regressed vs deployed beyond the 1.70pp tolerance; see list above for the actual drops), low-water-mark gate (4 filetype(s) below LWM beyond the 0.90pp tolerance vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run, or pass --net-improvement-fallback to ship a net-positive deploy whose only regressions are on small routes (below --catastrophe-min-mal). A high-volume filetype cratering past --max-net-route-regression blocks regardless; AZOTH_ALLOW_REGRESSION is the only override for that.
make[2]: *** [Makefile:1321: azoth-validate] Error 1)
