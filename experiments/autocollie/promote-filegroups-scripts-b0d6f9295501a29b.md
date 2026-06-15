# Promote REJECTED — `b0d6f9295501a29b` on `filegroups/scripts`

Generated 2026-06-14T22:41:48Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-14T22-29-58_20260614T222545-promote-b0d6f9295501a29b_azoth-validate.log; tail: 
ensemble improvements (≥0.10pp):
  lua: L50 hostile ensemble recall +7.69pp (38.46% → 46.15%)
  perl: L50 hostile ensemble recall +4.88pp (56.10% → 60.98%)
  php: L50 hostile ensemble recall +0.98pp (47.69% → 48.67%)

per-route improvements (≥0.10pp, informational):
  php :: filetypes/php recall@1FP-on-slice +3.23pp (44.46% → 47.69%)
  powershell :: filegroups/scripts recall@1FP-on-slice +3.10pp (54.51% → 57.61%)
  powershell :: filetypes/powershell recall@1FP-on-slice +12.85pp (44.31% → 57.16%)
  python :: filegroups/scripts recall@1FP-on-slice +2.71pp (52.76% → 55.47%)
  ruby :: filegroups/scripts recall@1FP-on-slice +19.05pp (19.05% → 38.10%)

per-route regressions (informational; does not block deploy):
  perl :: filegroups/scripts recall@1FP-on-slice dropped 2.44pp (63.41% → 60.98%)
  php :: filegroups/scripts recall@1FP-on-slice dropped 7.85pp (55.54% → 47.69%)
  shell :: filegroups/scripts recall@1FP-on-slice dropped 1.90pp (72.46% → 70.56%)

14 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + applescript: L50 hostile ensemble recall +23.08pp above LWM (0.00% → 23.08%)
  + dockerfile: L50 hostile ensemble recall +5.56pp above LWM (0.00% → 5.56%)
  + jar: L50 hostile ensemble recall +8.98pp above LWM (55.51% → 64.49%)
  + jpeg: L50 hostile ensemble recall +6.38pp above LWM (3.85% → 10.23%)
  + objc: L50 hostile ensemble recall +20.00pp above LWM (0.00% → 20.00%)
  + package.json: L50 hostile ensemble recall +3.39pp above LWM (85.89% → 89.28%)
  + pdf: L50 hostile ensemble recall +1.12pp above LWM (4.48% → 5.60%)
  + perl: L50 hostile ensemble recall +9.69pp above LWM (51.28% → 60.98%)
  + php: L50 hostile ensemble recall +5.45pp above LWM (43.22% → 48.67%)
  + pkg-info: L50 hostile ensemble recall +0.94pp above LWM (94.75% → 95.69%)
  + ruby: L50 hostile ensemble recall +1.68pp above LWM (41.18% → 42.86%)
  + vbs: L50 hostile ensemble recall +6.18pp above LWM (56.69% → 62.87%)
  + whl: L50 hostile ensemble recall +33.33pp above LWM (0.00% → 33.33%)
  + xml: L50 hostile ensemble recall +6.95pp above LWM (2.52% → 9.47%)

5 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - javascript: L50 hostile ENSEMBLE recall dropped 3.23pp BELOW LOW-WATER-MARK (63.33% → 60.10%; LWM tolerance 0.90pp)
  - lua: L50 hostile ENSEMBLE recall dropped 23.08pp BELOW LOW-WATER-MARK (69.23% → 46.15%; LWM tolerance 0.90pp)
  - powershell: L50 hostile ENSEMBLE recall dropped 4.33pp BELOW LOW-WATER-MARK (53.08% → 48.74%; LWM tolerance 0.90pp)
  - python: L50 hostile ENSEMBLE recall dropped 1.43pp BELOW LOW-WATER-MARK (48.46% → 47.03%; LWM tolerance 0.90pp)
  - shell: L50 hostile ENSEMBLE recall dropped 3.54pp BELOW LOW-WATER-MARK (72.05% → 68.51%; LWM tolerance 0.90pp)

net-improvement-fallback DID NOT rescue: net malware-caught delta = -118 TPs across 79 compared filetypes; worst high-volume drop (>=1500 mal) = 1.64pp on 'shell' (cap = 5.00pp); worst drop overall = 2.07pp on 'powershell' (small-route, not gated)
  reason: aggregate TP delta is not positive

compared 79 filetypes (mal≥1, ben≥1); 4 below threshold and skipped.

blocked by: low-water-mark gate (5 filetype(s) below LWM beyond the 0.90pp tolerance vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run, or pass --net-improvement-fallback to ship a net-positive deploy whose only regressions are on small routes (below --catastrophe-min-mal). A high-volume filetype cratering past --max-net-route-regression blocks regardless; AZOTH_ALLOW_REGRESSION is the only override for that.
make[2]: *** [Makefile:1321: azoth-validate] Error 1)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9978)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `b0d6f9295501a29b` | `a33fd6b2e2e2ea3a` | `ccd7f5b645246c31` |
| PR AUC | 0.9978 | 0.9980 | 0.9982 |
| ROC AUC | 0.9976 | 0.9977 | 0.9980 |
| F1 | 0.9693 | 0.9702 | 0.9745 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-14T22-29-58_20260614T222545-promote-b0d6f9295501a29b_azoth-validate.log; tail: 
ensemble improvements (≥0.10pp):
  lua: L50 hostile ensemble recall +7.69pp (38.46% → 46.15%)
  perl: L50 hostile ensemble recall +4.88pp (56.10% → 60.98%)
  php: L50 hostile ensemble recall +0.98pp (47.69% → 48.67%)

per-route improvements (≥0.10pp, informational):
  php :: filetypes/php recall@1FP-on-slice +3.23pp (44.46% → 47.69%)
  powershell :: filegroups/scripts recall@1FP-on-slice +3.10pp (54.51% → 57.61%)
  powershell :: filetypes/powershell recall@1FP-on-slice +12.85pp (44.31% → 57.16%)
  python :: filegroups/scripts recall@1FP-on-slice +2.71pp (52.76% → 55.47%)
  ruby :: filegroups/scripts recall@1FP-on-slice +19.05pp (19.05% → 38.10%)

per-route regressions (informational; does not block deploy):
  perl :: filegroups/scripts recall@1FP-on-slice dropped 2.44pp (63.41% → 60.98%)
  php :: filegroups/scripts recall@1FP-on-slice dropped 7.85pp (55.54% → 47.69%)
  shell :: filegroups/scripts recall@1FP-on-slice dropped 1.90pp (72.46% → 70.56%)

14 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + applescript: L50 hostile ensemble recall +23.08pp above LWM (0.00% → 23.08%)
  + dockerfile: L50 hostile ensemble recall +5.56pp above LWM (0.00% → 5.56%)
  + jar: L50 hostile ensemble recall +8.98pp above LWM (55.51% → 64.49%)
  + jpeg: L50 hostile ensemble recall +6.38pp above LWM (3.85% → 10.23%)
  + objc: L50 hostile ensemble recall +20.00pp above LWM (0.00% → 20.00%)
  + package.json: L50 hostile ensemble recall +3.39pp above LWM (85.89% → 89.28%)
  + pdf: L50 hostile ensemble recall +1.12pp above LWM (4.48% → 5.60%)
  + perl: L50 hostile ensemble recall +9.69pp above LWM (51.28% → 60.98%)
  + php: L50 hostile ensemble recall +5.45pp above LWM (43.22% → 48.67%)
  + pkg-info: L50 hostile ensemble recall +0.94pp above LWM (94.75% → 95.69%)
  + ruby: L50 hostile ensemble recall +1.68pp above LWM (41.18% → 42.86%)
  + vbs: L50 hostile ensemble recall +6.18pp above LWM (56.69% → 62.87%)
  + whl: L50 hostile ensemble recall +33.33pp above LWM (0.00% → 33.33%)
  + xml: L50 hostile ensemble recall +6.95pp above LWM (2.52% → 9.47%)

5 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - javascript: L50 hostile ENSEMBLE recall dropped 3.23pp BELOW LOW-WATER-MARK (63.33% → 60.10%; LWM tolerance 0.90pp)
  - lua: L50 hostile ENSEMBLE recall dropped 23.08pp BELOW LOW-WATER-MARK (69.23% → 46.15%; LWM tolerance 0.90pp)
  - powershell: L50 hostile ENSEMBLE recall dropped 4.33pp BELOW LOW-WATER-MARK (53.08% → 48.74%; LWM tolerance 0.90pp)
  - python: L50 hostile ENSEMBLE recall dropped 1.43pp BELOW LOW-WATER-MARK (48.46% → 47.03%; LWM tolerance 0.90pp)
  - shell: L50 hostile ENSEMBLE recall dropped 3.54pp BELOW LOW-WATER-MARK (72.05% → 68.51%; LWM tolerance 0.90pp)

net-improvement-fallback DID NOT rescue: net malware-caught delta = -118 TPs across 79 compared filetypes; worst high-volume drop (>=1500 mal) = 1.64pp on 'shell' (cap = 5.00pp); worst drop overall = 2.07pp on 'powershell' (small-route, not gated)
  reason: aggregate TP delta is not positive

compared 79 filetypes (mal≥1, ben≥1); 4 below threshold and skipped.

blocked by: low-water-mark gate (5 filetype(s) below LWM beyond the 0.90pp tolerance vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run, or pass --net-improvement-fallback to ship a net-positive deploy whose only regressions are on small routes (below --catastrophe-min-mal). A high-volume filetype cratering past --max-net-route-regression blocks regardless; AZOTH_ALLOW_REGRESSION is the only override for that.
make[2]: *** [Makefile:1321: azoth-validate] Error 1)
