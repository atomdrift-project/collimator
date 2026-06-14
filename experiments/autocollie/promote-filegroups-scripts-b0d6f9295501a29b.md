# Promote REJECTED — `b0d6f9295501a29b` on `filegroups/scripts`

Generated 2026-06-13T20:05:08Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-13T19-54-42_20260613T195036-promote-b0d6f9295501a29b_azoth-validate.log; tail:   php: L50 hostile ensemble recall +0.98pp (48.25% → 49.23%)
  shell: L50 hostile ensemble recall +1.08pp (73.23% → 74.31%)

per-route improvements (≥0.10pp, informational):
  batch :: filegroups/scripts recall@1FP-on-slice +0.40pp (1.76% → 2.16%)
  javascript :: filegroups/scripts recall@1FP-on-slice +0.66pp (65.46% → 66.12%)
  javascript :: filetypes/javascript recall@1FP-on-slice +4.07pp (62.90% → 66.97%)
  php :: filetypes/php recall@1FP-on-slice +6.87pp (44.74% → 51.61%)
  powershell :: filegroups/scripts recall@1FP-on-slice +2.22pp (54.51% → 56.72%)
  python :: filegroups/scripts recall@1FP-on-slice +2.02pp (52.76% → 54.78%)
  ruby :: filegroups/scripts recall@1FP-on-slice +19.05pp (19.05% → 38.10%)
  shell :: filegroups/scripts recall@1FP-on-slice +1.23pp (72.46% → 73.69%)

per-route regressions (informational; does not block deploy):
  php :: filegroups/scripts recall@1FP-on-slice dropped 5.19pp (55.54% → 50.35%)
  powershell :: filetypes/powershell recall@1FP-on-slice dropped 11.08pp (55.39% → 44.31%)

13 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + applescript: L50 hostile ensemble recall +23.08pp above LWM (0.00% → 23.08%)
  + dockerfile: L50 hostile ensemble recall +5.56pp above LWM (0.00% → 5.56%)
  + jar: L50 hostile ensemble recall +8.98pp above LWM (55.51% → 64.49%)
  + jpeg: L50 hostile ensemble recall +6.38pp above LWM (3.85% → 10.23%)
  + objc: L50 hostile ensemble recall +20.00pp above LWM (0.00% → 20.00%)
  + package.json: L50 hostile ensemble recall +3.39pp above LWM (85.89% → 89.28%)
  + pdf: L50 hostile ensemble recall +1.02pp above LWM (4.48% → 5.50%)
  + php: L50 hostile ensemble recall +6.01pp above LWM (43.22% → 49.23%)
  + pkg-info: L50 hostile ensemble recall +0.94pp above LWM (94.75% → 95.69%)
  + ruby: L50 hostile ensemble recall +1.68pp above LWM (41.18% → 42.86%)
  + shell: L50 hostile ensemble recall +2.25pp above LWM (72.05% → 74.31%)
  + whl: L50 hostile ensemble recall +37.50pp above LWM (0.00% → 37.50%)
  + xml: L50 hostile ensemble recall +6.95pp above LWM (2.52% → 9.47%)

1 DEPLOYED-TOLERANCE regression(s) (vs currently-deployed bundle /home/t/.local/share/litmus/models/azoth) — THIS IS WHAT BLOCKS THE DEPLOY:
  - python: L50 hostile ENSEMBLE recall dropped 3.90pp (48.94% → 45.04%; tolerance 1.70pp; deployed 95% CI lower = 47.08%)

4 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - javascript: L50 hostile ENSEMBLE recall dropped 8.32pp BELOW LOW-WATER-MARK (63.33% → 55.01%; LWM tolerance 0.90pp)
  - lua: L50 hostile ENSEMBLE recall dropped 30.77pp BELOW LOW-WATER-MARK (69.23% → 38.46%; LWM tolerance 0.90pp)
  - powershell: L50 hostile ENSEMBLE recall dropped 2.26pp BELOW LOW-WATER-MARK (53.08% → 50.81%; LWM tolerance 0.90pp)
  - python: L50 hostile ENSEMBLE recall dropped 3.42pp BELOW LOW-WATER-MARK (48.46% → 45.04%; LWM tolerance 0.90pp)

net-improvement-fallback DID NOT rescue: net malware-caught delta = -56 TPs across 78 compared filetypes; worst high-volume drop (>=1500 mal) = 3.90pp on 'python' (cap = 5.00pp); worst drop overall = 4.88pp on 'perl' (small-route, not gated)
  reason: aggregate TP delta is not positive

compared 78 filetypes (mal≥1, ben≥1); 5 below threshold and skipped.

blocked by: deployed-tolerance gate (1 filetype(s) regressed vs deployed beyond the 1.70pp tolerance; see list above for the actual drops), low-water-mark gate (4 filetype(s) below LWM beyond the 0.90pp tolerance vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run, or pass --net-improvement-fallback to ship a net-positive deploy whose only regressions are on small routes (below --catastrophe-min-mal). A high-volume filetype cratering past --max-net-route-regression blocks regardless; AZOTH_ALLOW_REGRESSION is the only override for that.
make[2]: *** [Makefile:1317: azoth-validate] Error 1)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9978)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `b0d6f9295501a29b` | `29e227387d821e48` | `6cd73e4a7286b3ec` |
| PR AUC | 0.9978 | 0.9972 | 0.9975 |
| ROC AUC | 0.9976 | 0.9968 | 0.9971 |
| F1 | 0.9693 | 0.9632 | 0.9646 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-13T19-54-42_20260613T195036-promote-b0d6f9295501a29b_azoth-validate.log; tail:   php: L50 hostile ensemble recall +0.98pp (48.25% → 49.23%)
  shell: L50 hostile ensemble recall +1.08pp (73.23% → 74.31%)

per-route improvements (≥0.10pp, informational):
  batch :: filegroups/scripts recall@1FP-on-slice +0.40pp (1.76% → 2.16%)
  javascript :: filegroups/scripts recall@1FP-on-slice +0.66pp (65.46% → 66.12%)
  javascript :: filetypes/javascript recall@1FP-on-slice +4.07pp (62.90% → 66.97%)
  php :: filetypes/php recall@1FP-on-slice +6.87pp (44.74% → 51.61%)
  powershell :: filegroups/scripts recall@1FP-on-slice +2.22pp (54.51% → 56.72%)
  python :: filegroups/scripts recall@1FP-on-slice +2.02pp (52.76% → 54.78%)
  ruby :: filegroups/scripts recall@1FP-on-slice +19.05pp (19.05% → 38.10%)
  shell :: filegroups/scripts recall@1FP-on-slice +1.23pp (72.46% → 73.69%)

per-route regressions (informational; does not block deploy):
  php :: filegroups/scripts recall@1FP-on-slice dropped 5.19pp (55.54% → 50.35%)
  powershell :: filetypes/powershell recall@1FP-on-slice dropped 11.08pp (55.39% → 44.31%)

13 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + applescript: L50 hostile ensemble recall +23.08pp above LWM (0.00% → 23.08%)
  + dockerfile: L50 hostile ensemble recall +5.56pp above LWM (0.00% → 5.56%)
  + jar: L50 hostile ensemble recall +8.98pp above LWM (55.51% → 64.49%)
  + jpeg: L50 hostile ensemble recall +6.38pp above LWM (3.85% → 10.23%)
  + objc: L50 hostile ensemble recall +20.00pp above LWM (0.00% → 20.00%)
  + package.json: L50 hostile ensemble recall +3.39pp above LWM (85.89% → 89.28%)
  + pdf: L50 hostile ensemble recall +1.02pp above LWM (4.48% → 5.50%)
  + php: L50 hostile ensemble recall +6.01pp above LWM (43.22% → 49.23%)
  + pkg-info: L50 hostile ensemble recall +0.94pp above LWM (94.75% → 95.69%)
  + ruby: L50 hostile ensemble recall +1.68pp above LWM (41.18% → 42.86%)
  + shell: L50 hostile ensemble recall +2.25pp above LWM (72.05% → 74.31%)
  + whl: L50 hostile ensemble recall +37.50pp above LWM (0.00% → 37.50%)
  + xml: L50 hostile ensemble recall +6.95pp above LWM (2.52% → 9.47%)

1 DEPLOYED-TOLERANCE regression(s) (vs currently-deployed bundle /home/t/.local/share/litmus/models/azoth) — THIS IS WHAT BLOCKS THE DEPLOY:
  - python: L50 hostile ENSEMBLE recall dropped 3.90pp (48.94% → 45.04%; tolerance 1.70pp; deployed 95% CI lower = 47.08%)

4 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - javascript: L50 hostile ENSEMBLE recall dropped 8.32pp BELOW LOW-WATER-MARK (63.33% → 55.01%; LWM tolerance 0.90pp)
  - lua: L50 hostile ENSEMBLE recall dropped 30.77pp BELOW LOW-WATER-MARK (69.23% → 38.46%; LWM tolerance 0.90pp)
  - powershell: L50 hostile ENSEMBLE recall dropped 2.26pp BELOW LOW-WATER-MARK (53.08% → 50.81%; LWM tolerance 0.90pp)
  - python: L50 hostile ENSEMBLE recall dropped 3.42pp BELOW LOW-WATER-MARK (48.46% → 45.04%; LWM tolerance 0.90pp)

net-improvement-fallback DID NOT rescue: net malware-caught delta = -56 TPs across 78 compared filetypes; worst high-volume drop (>=1500 mal) = 3.90pp on 'python' (cap = 5.00pp); worst drop overall = 4.88pp on 'perl' (small-route, not gated)
  reason: aggregate TP delta is not positive

compared 78 filetypes (mal≥1, ben≥1); 5 below threshold and skipped.

blocked by: deployed-tolerance gate (1 filetype(s) regressed vs deployed beyond the 1.70pp tolerance; see list above for the actual drops), low-water-mark gate (4 filetype(s) below LWM beyond the 0.90pp tolerance vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run, or pass --net-improvement-fallback to ship a net-positive deploy whose only regressions are on small routes (below --catastrophe-min-mal). A high-volume filetype cratering past --max-net-route-regression blocks regardless; AZOTH_ALLOW_REGRESSION is the only override for that.
make[2]: *** [Makefile:1317: azoth-validate] Error 1)
