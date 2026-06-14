# Promote REJECTED — `b0d6f9295501a29b` on `filegroups/scripts`

Generated 2026-06-14T02:39:26Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-14T02-26-41_20260614T022130-promote-b0d6f9295501a29b_azoth-validate.log; tail: per-route improvements (≥0.10pp, informational):
  javascript :: filetypes/javascript recall@1FP-on-slice +4.11pp (62.90% → 67.01%)
  php :: filetypes/php recall@1FP-on-slice +1.54pp (44.74% → 46.28%)
  python :: filegroups/scripts recall@1FP-on-slice +4.25pp (52.76% → 57.01%)
  ruby :: filegroups/scripts recall@1FP-on-slice +23.81pp (19.05% → 42.86%)
  shell :: filegroups/scripts recall@1FP-on-slice +1.13pp (72.46% → 73.59%)
  shell :: filetypes/shell recall@1FP-on-slice +5.64pp (75.28% → 80.92%)

per-route regressions (informational; does not block deploy):
  perl :: filegroups/scripts recall@1FP-on-slice dropped 2.44pp (63.41% → 60.98%)
  php :: filegroups/scripts recall@1FP-on-slice dropped 4.35pp (55.54% → 51.19%)
  powershell :: filetypes/powershell recall@1FP-on-slice dropped 11.08pp (55.39% → 44.31%)

14 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + applescript: L50 hostile ensemble recall +23.08pp above LWM (0.00% → 23.08%)
  + dockerfile: L50 hostile ensemble recall +5.56pp above LWM (0.00% → 5.56%)
  + jar: L50 hostile ensemble recall +8.98pp above LWM (55.51% → 64.49%)
  + jpeg: L50 hostile ensemble recall +6.38pp above LWM (3.85% → 10.23%)
  + objc: L50 hostile ensemble recall +20.00pp above LWM (0.00% → 20.00%)
  + package.json: L50 hostile ensemble recall +3.39pp above LWM (85.89% → 89.28%)
  + pdf: L50 hostile ensemble recall +1.12pp above LWM (4.48% → 5.60%)
  + perl: L50 hostile ensemble recall +9.69pp above LWM (51.28% → 60.98%)
  + php: L50 hostile ensemble recall +7.27pp above LWM (43.22% → 50.49%)
  + pkg-info: L50 hostile ensemble recall +0.94pp above LWM (94.75% → 95.69%)
  + ruby: L50 hostile ensemble recall +1.68pp above LWM (41.18% → 42.86%)
  + vbs: L50 hostile ensemble recall +6.18pp above LWM (56.69% → 62.87%)
  + whl: L50 hostile ensemble recall +37.50pp above LWM (0.00% → 37.50%)
  + xml: L50 hostile ensemble recall +6.95pp above LWM (2.52% → 9.47%)

3 DEPLOYED-TOLERANCE regression(s) (vs currently-deployed bundle /home/t/.local/share/litmus/models/azoth) — THIS IS WHAT BLOCKS THE DEPLOY:
  - powershell: L50 hostile ENSEMBLE recall dropped 5.91pp (50.81% → 44.90%; tolerance 1.70pp; deployed 95% CI lower = 46.98%)
  - python: L50 hostile ENSEMBLE recall dropped 5.21pp (48.94% → 43.73%; tolerance 1.70pp; deployed 95% CI lower = 47.08%)
  - shell: L50 hostile ENSEMBLE recall dropped 4.21pp (73.23% → 69.03%; tolerance 1.70pp; deployed 95% CI lower = 71.21%)

5 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - javascript: L50 hostile ENSEMBLE recall dropped 1.83pp BELOW LOW-WATER-MARK (63.33% → 61.50%; LWM tolerance 0.90pp)
  - lua: L50 hostile ENSEMBLE recall dropped 23.08pp BELOW LOW-WATER-MARK (69.23% → 46.15%; LWM tolerance 0.90pp)
  - powershell: L50 hostile ENSEMBLE recall dropped 8.17pp BELOW LOW-WATER-MARK (53.08% → 44.90%; LWM tolerance 0.90pp)
  - python: L50 hostile ENSEMBLE recall dropped 4.73pp BELOW LOW-WATER-MARK (48.46% → 43.73%; LWM tolerance 0.90pp)
  - shell: L50 hostile ENSEMBLE recall dropped 3.03pp BELOW LOW-WATER-MARK (72.05% → 69.03%; LWM tolerance 0.90pp)

net-improvement-fallback DID NOT rescue: net malware-caught delta = +11,106 TPs across 78 compared filetypes; worst high-volume drop (>=1500 mal) = 5.21pp on 'python' (cap = 5.00pp); worst drop overall = 5.91pp on 'powershell' (small-route, not gated)
  reason: a high-volume filetype cratered (5.21pp on 'python', >=1500 malware) exceeds catastrophe cap (5.00pp)

compared 78 filetypes (mal≥1, ben≥1); 5 below threshold and skipped.

blocked by: deployed-tolerance gate (3 filetype(s) regressed vs deployed beyond the 1.70pp tolerance; see list above for the actual drops), low-water-mark gate (5 filetype(s) below LWM beyond the 0.90pp tolerance vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run, or pass --net-improvement-fallback to ship a net-positive deploy whose only regressions are on small routes (below --catastrophe-min-mal). A high-volume filetype cratering past --max-net-route-regression blocks regardless; AZOTH_ALLOW_REGRESSION is the only override for that.
make[2]: *** [Makefile:1317: azoth-validate] Error 1)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9978)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `b0d6f9295501a29b` | `8f3816b234c1f655` | `55df9056146c4cc4` |
| PR AUC | 0.9978 | 0.9981 | 0.9983 |
| ROC AUC | 0.9976 | 0.9978 | 0.9980 |
| F1 | 0.9693 | 0.9704 | 0.9729 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-14T02-26-41_20260614T022130-promote-b0d6f9295501a29b_azoth-validate.log; tail: per-route improvements (≥0.10pp, informational):
  javascript :: filetypes/javascript recall@1FP-on-slice +4.11pp (62.90% → 67.01%)
  php :: filetypes/php recall@1FP-on-slice +1.54pp (44.74% → 46.28%)
  python :: filegroups/scripts recall@1FP-on-slice +4.25pp (52.76% → 57.01%)
  ruby :: filegroups/scripts recall@1FP-on-slice +23.81pp (19.05% → 42.86%)
  shell :: filegroups/scripts recall@1FP-on-slice +1.13pp (72.46% → 73.59%)
  shell :: filetypes/shell recall@1FP-on-slice +5.64pp (75.28% → 80.92%)

per-route regressions (informational; does not block deploy):
  perl :: filegroups/scripts recall@1FP-on-slice dropped 2.44pp (63.41% → 60.98%)
  php :: filegroups/scripts recall@1FP-on-slice dropped 4.35pp (55.54% → 51.19%)
  powershell :: filetypes/powershell recall@1FP-on-slice dropped 11.08pp (55.39% → 44.31%)

14 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + applescript: L50 hostile ensemble recall +23.08pp above LWM (0.00% → 23.08%)
  + dockerfile: L50 hostile ensemble recall +5.56pp above LWM (0.00% → 5.56%)
  + jar: L50 hostile ensemble recall +8.98pp above LWM (55.51% → 64.49%)
  + jpeg: L50 hostile ensemble recall +6.38pp above LWM (3.85% → 10.23%)
  + objc: L50 hostile ensemble recall +20.00pp above LWM (0.00% → 20.00%)
  + package.json: L50 hostile ensemble recall +3.39pp above LWM (85.89% → 89.28%)
  + pdf: L50 hostile ensemble recall +1.12pp above LWM (4.48% → 5.60%)
  + perl: L50 hostile ensemble recall +9.69pp above LWM (51.28% → 60.98%)
  + php: L50 hostile ensemble recall +7.27pp above LWM (43.22% → 50.49%)
  + pkg-info: L50 hostile ensemble recall +0.94pp above LWM (94.75% → 95.69%)
  + ruby: L50 hostile ensemble recall +1.68pp above LWM (41.18% → 42.86%)
  + vbs: L50 hostile ensemble recall +6.18pp above LWM (56.69% → 62.87%)
  + whl: L50 hostile ensemble recall +37.50pp above LWM (0.00% → 37.50%)
  + xml: L50 hostile ensemble recall +6.95pp above LWM (2.52% → 9.47%)

3 DEPLOYED-TOLERANCE regression(s) (vs currently-deployed bundle /home/t/.local/share/litmus/models/azoth) — THIS IS WHAT BLOCKS THE DEPLOY:
  - powershell: L50 hostile ENSEMBLE recall dropped 5.91pp (50.81% → 44.90%; tolerance 1.70pp; deployed 95% CI lower = 46.98%)
  - python: L50 hostile ENSEMBLE recall dropped 5.21pp (48.94% → 43.73%; tolerance 1.70pp; deployed 95% CI lower = 47.08%)
  - shell: L50 hostile ENSEMBLE recall dropped 4.21pp (73.23% → 69.03%; tolerance 1.70pp; deployed 95% CI lower = 71.21%)

5 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - javascript: L50 hostile ENSEMBLE recall dropped 1.83pp BELOW LOW-WATER-MARK (63.33% → 61.50%; LWM tolerance 0.90pp)
  - lua: L50 hostile ENSEMBLE recall dropped 23.08pp BELOW LOW-WATER-MARK (69.23% → 46.15%; LWM tolerance 0.90pp)
  - powershell: L50 hostile ENSEMBLE recall dropped 8.17pp BELOW LOW-WATER-MARK (53.08% → 44.90%; LWM tolerance 0.90pp)
  - python: L50 hostile ENSEMBLE recall dropped 4.73pp BELOW LOW-WATER-MARK (48.46% → 43.73%; LWM tolerance 0.90pp)
  - shell: L50 hostile ENSEMBLE recall dropped 3.03pp BELOW LOW-WATER-MARK (72.05% → 69.03%; LWM tolerance 0.90pp)

net-improvement-fallback DID NOT rescue: net malware-caught delta = +11,106 TPs across 78 compared filetypes; worst high-volume drop (>=1500 mal) = 5.21pp on 'python' (cap = 5.00pp); worst drop overall = 5.91pp on 'powershell' (small-route, not gated)
  reason: a high-volume filetype cratered (5.21pp on 'python', >=1500 malware) exceeds catastrophe cap (5.00pp)

compared 78 filetypes (mal≥1, ben≥1); 5 below threshold and skipped.

blocked by: deployed-tolerance gate (3 filetype(s) regressed vs deployed beyond the 1.70pp tolerance; see list above for the actual drops), low-water-mark gate (5 filetype(s) below LWM beyond the 0.90pp tolerance vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run, or pass --net-improvement-fallback to ship a net-positive deploy whose only regressions are on small routes (below --catastrophe-min-mal). A high-volume filetype cratering past --max-net-route-regression blocks regardless; AZOTH_ALLOW_REGRESSION is the only override for that.
make[2]: *** [Makefile:1317: azoth-validate] Error 1)
