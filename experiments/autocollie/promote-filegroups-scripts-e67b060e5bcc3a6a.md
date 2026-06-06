# Promote REJECTED — `e67b060e5bcc3a6a` on `filegroups/scripts`

Generated 2026-06-06T15:52:43Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-06T15-44-36_20260606T154051-promote-e67b060e5bcc3a6a_azoth-validate.log; tail: staged runtime azoth bundle: /tmp/tmp.1PMjInm8F9
azoth bundle ok: /tmp/tmp.1PMjInm8F9
--source-bundle out/models/azoth: 1 routes changed → 9 filetypes impacted, 69 unimpacted (drift treated as pre-existing)

ensemble improvements (≥0.10pp):
  lua: L50 hostile ensemble recall +30.77pp (30.77% → 61.54%)
  perl: L50 hostile ensemble recall +2.78pp (69.44% → 72.22%)
  php: L50 hostile ensemble recall +5.09pp (47.88% → 52.97%)
  python: L50 hostile ensemble recall +1.21pp (48.01% → 49.22%)
  ruby: L50 hostile ensemble recall +16.67pp (50.00% → 66.67%)
  shell: L50 hostile ensemble recall +6.66pp (81.64% → 88.30%)

per-route improvements (≥0.10pp, informational):
  batch :: general recall@1FP-on-slice +0.20pp (1.46% → 1.67%)
  perl :: general recall@1FP-on-slice +8.33pp (55.56% → 63.89%)
  php :: general recall@1FP-on-slice +2.84pp (52.47% → 55.31%)
  php :: filegroups/scripts recall@1FP-on-slice +4.99pp (47.35% → 52.34%)
  powershell :: general recall@1FP-on-slice +0.69pp (54.19% → 54.87%)
  powershell :: filetypes/powershell recall@1FP-on-slice +11.16pp (33.18% → 44.34%)
  python :: general recall@1FP-on-slice +2.33pp (61.94% → 64.27%)
  python :: filegroups/scripts recall@1FP-on-slice +6.63pp (55.42% → 62.05%)
  ruby :: general recall@1FP-on-slice +8.33pp (58.33% → 66.67%)
  ruby :: filetypes/ruby recall@1FP-on-slice +33.33pp (41.67% → 75.00%)
  shell :: filetypes/shell recall@1FP-on-slice +5.70pp (84.10% → 89.80%)

per-route regressions (informational; does not block deploy):
  batch :: filegroups/scripts recall@1FP-on-slice dropped 96.32pp (97.82% → 1.50%)
  batch :: filetypes/batch recall@1FP-on-slice dropped 95.61pp (97.54% → 1.93%)
  javascript :: filegroups/scripts recall@1FP-on-slice dropped 3.89pp (63.30% → 59.41%)
  javascript :: filetypes/javascript recall@1FP-on-slice dropped 3.49pp (66.71% → 63.22%)
  lua :: general recall@1FP-on-slice dropped 7.69pp (76.92% → 69.23%)
  lua :: filegroups/scripts recall@1FP-on-slice dropped 7.69pp (76.92% → 69.23%)
  perl :: filetypes/perl recall@1FP-on-slice dropped 11.11pp (94.44% → 83.33%)
  php :: filetypes/php recall@1FP-on-slice dropped 10.53pp (61.31% → 50.78%)
  powershell :: filegroups/scripts recall@1FP-on-slice dropped 12.90pp (67.93% → 55.03%)
  python :: filetypes/python recall@1FP-on-slice dropped 3.73pp (61.05% → 57.32%)
  shell :: general recall@1FP-on-slice dropped 28.10pp (74.79% → 46.69%)
  shell :: filegroups/scripts recall@1FP-on-slice dropped 4.38pp (76.34% → 71.96%)

3 DEPLOYED-TOLERANCE regression(s) (vs currently-deployed bundle /home/t/.local/share/litmus/models/azoth) — THIS IS WHAT BLOCKS THE DEPLOY:
  - batch: L50 hostile ENSEMBLE recall dropped 96.07pp (97.46% → 1.39%; tolerance 1.70pp; deployed 95% CI lower = 97.25%)
  - javascript: L50 hostile ENSEMBLE recall dropped 8.13pp (59.50% → 51.37%; tolerance 1.70pp; deployed 95% CI lower = 58.69%)
  - powershell: L50 hostile ENSEMBLE recall dropped 13.30pp (52.76% → 39.47%; tolerance 1.70pp; deployed 95% CI lower = 48.79%)

compared 75 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: deployed-tolerance gate (3 filetype(s) regressed vs deployed beyond the 1.70pp tolerance; see list above for the actual drops)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1297: azoth-validate] Error 1)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9979)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `e67b060e5bcc3a6a` | `f0310ae5577896bb` | `f6e8608260164af0` |
| PR AUC | 0.9979 | 0.9987 | 0.9988 |
| ROC AUC | 0.9977 | 0.9983 | 0.9985 |
| F1 | 0.9725 | 0.9794 | 0.9791 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-06T15-44-36_20260606T154051-promote-e67b060e5bcc3a6a_azoth-validate.log; tail: staged runtime azoth bundle: /tmp/tmp.1PMjInm8F9
azoth bundle ok: /tmp/tmp.1PMjInm8F9
--source-bundle out/models/azoth: 1 routes changed → 9 filetypes impacted, 69 unimpacted (drift treated as pre-existing)

ensemble improvements (≥0.10pp):
  lua: L50 hostile ensemble recall +30.77pp (30.77% → 61.54%)
  perl: L50 hostile ensemble recall +2.78pp (69.44% → 72.22%)
  php: L50 hostile ensemble recall +5.09pp (47.88% → 52.97%)
  python: L50 hostile ensemble recall +1.21pp (48.01% → 49.22%)
  ruby: L50 hostile ensemble recall +16.67pp (50.00% → 66.67%)
  shell: L50 hostile ensemble recall +6.66pp (81.64% → 88.30%)

per-route improvements (≥0.10pp, informational):
  batch :: general recall@1FP-on-slice +0.20pp (1.46% → 1.67%)
  perl :: general recall@1FP-on-slice +8.33pp (55.56% → 63.89%)
  php :: general recall@1FP-on-slice +2.84pp (52.47% → 55.31%)
  php :: filegroups/scripts recall@1FP-on-slice +4.99pp (47.35% → 52.34%)
  powershell :: general recall@1FP-on-slice +0.69pp (54.19% → 54.87%)
  powershell :: filetypes/powershell recall@1FP-on-slice +11.16pp (33.18% → 44.34%)
  python :: general recall@1FP-on-slice +2.33pp (61.94% → 64.27%)
  python :: filegroups/scripts recall@1FP-on-slice +6.63pp (55.42% → 62.05%)
  ruby :: general recall@1FP-on-slice +8.33pp (58.33% → 66.67%)
  ruby :: filetypes/ruby recall@1FP-on-slice +33.33pp (41.67% → 75.00%)
  shell :: filetypes/shell recall@1FP-on-slice +5.70pp (84.10% → 89.80%)

per-route regressions (informational; does not block deploy):
  batch :: filegroups/scripts recall@1FP-on-slice dropped 96.32pp (97.82% → 1.50%)
  batch :: filetypes/batch recall@1FP-on-slice dropped 95.61pp (97.54% → 1.93%)
  javascript :: filegroups/scripts recall@1FP-on-slice dropped 3.89pp (63.30% → 59.41%)
  javascript :: filetypes/javascript recall@1FP-on-slice dropped 3.49pp (66.71% → 63.22%)
  lua :: general recall@1FP-on-slice dropped 7.69pp (76.92% → 69.23%)
  lua :: filegroups/scripts recall@1FP-on-slice dropped 7.69pp (76.92% → 69.23%)
  perl :: filetypes/perl recall@1FP-on-slice dropped 11.11pp (94.44% → 83.33%)
  php :: filetypes/php recall@1FP-on-slice dropped 10.53pp (61.31% → 50.78%)
  powershell :: filegroups/scripts recall@1FP-on-slice dropped 12.90pp (67.93% → 55.03%)
  python :: filetypes/python recall@1FP-on-slice dropped 3.73pp (61.05% → 57.32%)
  shell :: general recall@1FP-on-slice dropped 28.10pp (74.79% → 46.69%)
  shell :: filegroups/scripts recall@1FP-on-slice dropped 4.38pp (76.34% → 71.96%)

3 DEPLOYED-TOLERANCE regression(s) (vs currently-deployed bundle /home/t/.local/share/litmus/models/azoth) — THIS IS WHAT BLOCKS THE DEPLOY:
  - batch: L50 hostile ENSEMBLE recall dropped 96.07pp (97.46% → 1.39%; tolerance 1.70pp; deployed 95% CI lower = 97.25%)
  - javascript: L50 hostile ENSEMBLE recall dropped 8.13pp (59.50% → 51.37%; tolerance 1.70pp; deployed 95% CI lower = 58.69%)
  - powershell: L50 hostile ENSEMBLE recall dropped 13.30pp (52.76% → 39.47%; tolerance 1.70pp; deployed 95% CI lower = 48.79%)

compared 75 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: deployed-tolerance gate (3 filetype(s) regressed vs deployed beyond the 1.70pp tolerance; see list above for the actual drops)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1297: azoth-validate] Error 1)
