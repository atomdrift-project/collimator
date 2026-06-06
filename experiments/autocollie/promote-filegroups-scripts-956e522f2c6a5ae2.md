# Promote REJECTED — `956e522f2c6a5ae2` on `filegroups/scripts`

Generated 2026-06-06T15:28:29Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-06T15-20-39_20260606T151649-promote-956e522f2c6a5ae2_azoth-validate.log; tail: --source-bundle out/models/azoth: 1 routes changed → 9 filetypes impacted, 69 unimpacted (drift treated as pre-existing)

ensemble improvements (≥0.10pp):
  lua: L50 hostile ensemble recall +38.46pp (30.77% → 69.23%)
  perl: L50 hostile ensemble recall +2.78pp (69.44% → 72.22%)
  php: L50 hostile ensemble recall +1.50pp (47.88% → 49.38%)
  python: L50 hostile ensemble recall +6.06pp (48.01% → 54.07%)
  ruby: L50 hostile ensemble recall +16.67pp (50.00% → 66.67%)
  shell: L50 hostile ensemble recall +5.65pp (81.64% → 87.29%)

per-route improvements (≥0.10pp, informational):
  batch :: general recall@1FP-on-slice +0.20pp (1.46% → 1.67%)
  perl :: general recall@1FP-on-slice +8.33pp (55.56% → 63.89%)
  perl :: filegroups/scripts recall@1FP-on-slice +8.33pp (69.44% → 77.78%)
  php :: general recall@1FP-on-slice +2.84pp (52.47% → 55.31%)
  php :: filegroups/scripts recall@1FP-on-slice +1.09pp (47.35% → 48.44%)
  powershell :: general recall@1FP-on-slice +0.69pp (54.19% → 54.87%)
  powershell :: filetypes/powershell recall@1FP-on-slice +11.16pp (33.18% → 44.34%)
  python :: general recall@1FP-on-slice +2.33pp (61.94% → 64.27%)
  python :: filegroups/scripts recall@1FP-on-slice +4.61pp (55.42% → 60.03%)
  ruby :: general recall@1FP-on-slice +8.33pp (58.33% → 66.67%)
  ruby :: filegroups/scripts recall@1FP-on-slice +8.33pp (66.67% → 75.00%)
  ruby :: filetypes/ruby recall@1FP-on-slice +33.33pp (41.67% → 75.00%)
  shell :: filetypes/shell recall@1FP-on-slice +5.70pp (84.10% → 89.80%)

per-route regressions (informational; does not block deploy):
  batch :: filegroups/scripts recall@1FP-on-slice dropped 96.30pp (97.82% → 1.52%)
  batch :: filetypes/batch recall@1FP-on-slice dropped 95.61pp (97.54% → 1.93%)
  javascript :: filegroups/scripts recall@1FP-on-slice dropped 2.49pp (63.30% → 60.80%)
  javascript :: filetypes/javascript recall@1FP-on-slice dropped 3.49pp (66.71% → 63.22%)
  lua :: general recall@1FP-on-slice dropped 7.69pp (76.92% → 69.23%)
  lua :: filegroups/scripts recall@1FP-on-slice dropped 7.69pp (76.92% → 69.23%)
  perl :: filetypes/perl recall@1FP-on-slice dropped 11.11pp (94.44% → 83.33%)
  php :: filetypes/php recall@1FP-on-slice dropped 10.53pp (61.31% → 50.78%)
  powershell :: filegroups/scripts recall@1FP-on-slice dropped 6.92pp (67.93% → 61.01%)
  python :: filetypes/python recall@1FP-on-slice dropped 3.73pp (61.05% → 57.32%)
  shell :: general recall@1FP-on-slice dropped 28.10pp (74.79% → 46.69%)
  shell :: filegroups/scripts recall@1FP-on-slice dropped 4.38pp (76.34% → 71.96%)

3 DEPLOYED-TOLERANCE regression(s) (vs currently-deployed bundle /home/t/.local/share/litmus/models/azoth) — THIS IS WHAT BLOCKS THE DEPLOY:
  - batch: L50 hostile ENSEMBLE recall dropped 96.17pp (97.46% → 1.29%; tolerance 1.70pp; deployed 95% CI lower = 97.25%)
  - javascript: L50 hostile ENSEMBLE recall dropped 5.84pp (59.50% → 53.66%; tolerance 1.70pp; deployed 95% CI lower = 58.69%)
  - powershell: L50 hostile ENSEMBLE recall dropped 15.03pp (52.76% → 37.74%; tolerance 1.70pp; deployed 95% CI lower = 48.79%)

compared 75 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: deployed-tolerance gate (3 filetype(s) regressed vs deployed beyond the 1.70pp tolerance; see list above for the actual drops)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1297: azoth-validate] Error 1)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9981)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `956e522f2c6a5ae2` | `45c79bf81d382e9f` | `8c146cdf24a17c72` |
| PR AUC | 0.9981 | 0.9986 | 0.9988 |
| ROC AUC | 0.9979 | 0.9982 | 0.9984 |
| F1 | 0.9787 | 0.9766 | 0.9812 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-06T15-20-39_20260606T151649-promote-956e522f2c6a5ae2_azoth-validate.log; tail: --source-bundle out/models/azoth: 1 routes changed → 9 filetypes impacted, 69 unimpacted (drift treated as pre-existing)

ensemble improvements (≥0.10pp):
  lua: L50 hostile ensemble recall +38.46pp (30.77% → 69.23%)
  perl: L50 hostile ensemble recall +2.78pp (69.44% → 72.22%)
  php: L50 hostile ensemble recall +1.50pp (47.88% → 49.38%)
  python: L50 hostile ensemble recall +6.06pp (48.01% → 54.07%)
  ruby: L50 hostile ensemble recall +16.67pp (50.00% → 66.67%)
  shell: L50 hostile ensemble recall +5.65pp (81.64% → 87.29%)

per-route improvements (≥0.10pp, informational):
  batch :: general recall@1FP-on-slice +0.20pp (1.46% → 1.67%)
  perl :: general recall@1FP-on-slice +8.33pp (55.56% → 63.89%)
  perl :: filegroups/scripts recall@1FP-on-slice +8.33pp (69.44% → 77.78%)
  php :: general recall@1FP-on-slice +2.84pp (52.47% → 55.31%)
  php :: filegroups/scripts recall@1FP-on-slice +1.09pp (47.35% → 48.44%)
  powershell :: general recall@1FP-on-slice +0.69pp (54.19% → 54.87%)
  powershell :: filetypes/powershell recall@1FP-on-slice +11.16pp (33.18% → 44.34%)
  python :: general recall@1FP-on-slice +2.33pp (61.94% → 64.27%)
  python :: filegroups/scripts recall@1FP-on-slice +4.61pp (55.42% → 60.03%)
  ruby :: general recall@1FP-on-slice +8.33pp (58.33% → 66.67%)
  ruby :: filegroups/scripts recall@1FP-on-slice +8.33pp (66.67% → 75.00%)
  ruby :: filetypes/ruby recall@1FP-on-slice +33.33pp (41.67% → 75.00%)
  shell :: filetypes/shell recall@1FP-on-slice +5.70pp (84.10% → 89.80%)

per-route regressions (informational; does not block deploy):
  batch :: filegroups/scripts recall@1FP-on-slice dropped 96.30pp (97.82% → 1.52%)
  batch :: filetypes/batch recall@1FP-on-slice dropped 95.61pp (97.54% → 1.93%)
  javascript :: filegroups/scripts recall@1FP-on-slice dropped 2.49pp (63.30% → 60.80%)
  javascript :: filetypes/javascript recall@1FP-on-slice dropped 3.49pp (66.71% → 63.22%)
  lua :: general recall@1FP-on-slice dropped 7.69pp (76.92% → 69.23%)
  lua :: filegroups/scripts recall@1FP-on-slice dropped 7.69pp (76.92% → 69.23%)
  perl :: filetypes/perl recall@1FP-on-slice dropped 11.11pp (94.44% → 83.33%)
  php :: filetypes/php recall@1FP-on-slice dropped 10.53pp (61.31% → 50.78%)
  powershell :: filegroups/scripts recall@1FP-on-slice dropped 6.92pp (67.93% → 61.01%)
  python :: filetypes/python recall@1FP-on-slice dropped 3.73pp (61.05% → 57.32%)
  shell :: general recall@1FP-on-slice dropped 28.10pp (74.79% → 46.69%)
  shell :: filegroups/scripts recall@1FP-on-slice dropped 4.38pp (76.34% → 71.96%)

3 DEPLOYED-TOLERANCE regression(s) (vs currently-deployed bundle /home/t/.local/share/litmus/models/azoth) — THIS IS WHAT BLOCKS THE DEPLOY:
  - batch: L50 hostile ENSEMBLE recall dropped 96.17pp (97.46% → 1.29%; tolerance 1.70pp; deployed 95% CI lower = 97.25%)
  - javascript: L50 hostile ENSEMBLE recall dropped 5.84pp (59.50% → 53.66%; tolerance 1.70pp; deployed 95% CI lower = 58.69%)
  - powershell: L50 hostile ENSEMBLE recall dropped 15.03pp (52.76% → 37.74%; tolerance 1.70pp; deployed 95% CI lower = 48.79%)

compared 75 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: deployed-tolerance gate (3 filetype(s) regressed vs deployed beyond the 1.70pp tolerance; see list above for the actual drops)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1297: azoth-validate] Error 1)
