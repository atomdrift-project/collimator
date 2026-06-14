# Promote REJECTED — `48ae66e380562440` on `filegroups/documents`

Generated 2026-06-13T01:45:32Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-13T01-40-55_20260613T014008-promote-48ae66e380562440_azoth-validate.log; tail: 
ensemble improvements (≥0.10pp):
  docx: L50 hostile ensemble recall +4.22pp (74.34% → 78.56%)
  ole: L50 hostile ensemble recall +0.25pp (81.67% → 81.92%)
  xls: L50 hostile ensemble recall +0.57pp (93.76% → 94.34%)

per-route improvements (≥0.10pp, informational):
  doc :: filegroups/documents recall@1FP-on-slice +0.53pp (98.90% → 99.42%)
  xlsx :: filegroups/documents recall@1FP-on-slice +5.89pp (31.05% → 36.95%)

per-route regressions (informational; does not block deploy):
  docx :: filegroups/documents recall@1FP-on-slice dropped 4.92pp (83.48% → 78.56%)
  html :: filegroups/documents recall@1FP-on-slice dropped 35.71pp (100.00% → 64.29%)
  ole :: filegroups/documents recall@1FP-on-slice dropped 2.58pp (81.80% → 79.21%)
  pdf :: filegroups/documents recall@1FP-on-slice dropped 10.99pp (16.54% → 5.55%)
  pptx :: filegroups/documents recall@1FP-on-slice dropped 35.62pp (43.84% → 8.22%)

15 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + applescript: L50 hostile ensemble recall +23.08pp above LWM (0.00% → 23.08%)
  + dockerfile: L50 hostile ensemble recall +5.56pp above LWM (0.00% → 5.56%)
  + jar: L50 hostile ensemble recall +3.10pp above LWM (55.51% → 58.61%)
  + jpeg: L50 hostile ensemble recall +6.38pp above LWM (3.85% → 10.23%)
  + macho: L50 hostile ensemble recall +3.03pp above LWM (77.91% → 80.94%)
  + objc: L50 hostile ensemble recall +20.00pp above LWM (0.00% → 20.00%)
  + ole: L50 hostile ensemble recall +1.02pp above LWM (80.90% → 81.92%)
  + package.json: L50 hostile ensemble recall +3.39pp above LWM (85.89% → 89.28%)
  + perl: L50 hostile ensemble recall +4.82pp above LWM (51.28% → 56.10%)
  + php: L50 hostile ensemble recall +5.03pp above LWM (43.22% → 48.25%)
  + pkg-info: L50 hostile ensemble recall +0.94pp above LWM (94.75% → 95.69%)
  + ruby: L50 hostile ensemble recall +1.68pp above LWM (41.18% → 42.86%)
  + shell: L50 hostile ensemble recall +1.18pp above LWM (72.05% → 73.23%)
  + whl: L50 hostile ensemble recall +37.50pp above LWM (0.00% → 37.50%)
  + xml: L50 hostile ensemble recall +6.95pp above LWM (2.52% → 9.47%)

1 DEPLOYED-TOLERANCE regression(s) (vs currently-deployed bundle /home/t/.local/share/litmus/models/azoth) — THIS IS WHAT BLOCKS THE DEPLOY:
  - pdf: L50 hostile ENSEMBLE recall dropped 2.61pp (7.87% → 5.26%; tolerance 1.70pp; deployed 95% CI lower = 7.52%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - docx: L50 hostile ENSEMBLE recall dropped 1.01pp BELOW LOW-WATER-MARK (79.57% → 78.56%; LWM tolerance 0.90pp)

net-improvement-fallback DID NOT rescue: net malware-caught delta = -467 TPs across 78 compared filetypes; worst high-volume drop (>=1500 mal) = 2.61pp on 'pdf' (cap = 5.00pp); worst drop overall = 2.61pp on 'pdf' (small-route, not gated)
  reason: aggregate TP delta is not positive

compared 78 filetypes (mal≥1, ben≥1); 5 below threshold and skipped.

blocked by: deployed-tolerance gate (1 filetype(s) regressed vs deployed beyond the 1.70pp tolerance; see list above for the actual drops), low-water-mark gate (1 filetype(s) below LWM beyond the 0.90pp tolerance vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run, or pass --net-improvement-fallback to ship a net-positive deploy whose only regressions are on small routes (below --catastrophe-min-mal). A high-volume filetype cratering past --max-net-route-regression blocks regardless; AZOTH_ALLOW_REGRESSION is the only override for that.
make[1]: *** [Makefile:1317: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9999)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `48ae66e380562440` | `9bd8441c86251310` | `0d8081be74661543` |
| PR AUC | 0.9999 | 1.0000 | 1.0000 |
| ROC AUC | 0.9986 | 0.9992 | 0.9992 |
| F1 | 0.9914 | 0.9978 | 0.9976 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-13T01-40-55_20260613T014008-promote-48ae66e380562440_azoth-validate.log; tail: 
ensemble improvements (≥0.10pp):
  docx: L50 hostile ensemble recall +4.22pp (74.34% → 78.56%)
  ole: L50 hostile ensemble recall +0.25pp (81.67% → 81.92%)
  xls: L50 hostile ensemble recall +0.57pp (93.76% → 94.34%)

per-route improvements (≥0.10pp, informational):
  doc :: filegroups/documents recall@1FP-on-slice +0.53pp (98.90% → 99.42%)
  xlsx :: filegroups/documents recall@1FP-on-slice +5.89pp (31.05% → 36.95%)

per-route regressions (informational; does not block deploy):
  docx :: filegroups/documents recall@1FP-on-slice dropped 4.92pp (83.48% → 78.56%)
  html :: filegroups/documents recall@1FP-on-slice dropped 35.71pp (100.00% → 64.29%)
  ole :: filegroups/documents recall@1FP-on-slice dropped 2.58pp (81.80% → 79.21%)
  pdf :: filegroups/documents recall@1FP-on-slice dropped 10.99pp (16.54% → 5.55%)
  pptx :: filegroups/documents recall@1FP-on-slice dropped 35.62pp (43.84% → 8.22%)

15 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + applescript: L50 hostile ensemble recall +23.08pp above LWM (0.00% → 23.08%)
  + dockerfile: L50 hostile ensemble recall +5.56pp above LWM (0.00% → 5.56%)
  + jar: L50 hostile ensemble recall +3.10pp above LWM (55.51% → 58.61%)
  + jpeg: L50 hostile ensemble recall +6.38pp above LWM (3.85% → 10.23%)
  + macho: L50 hostile ensemble recall +3.03pp above LWM (77.91% → 80.94%)
  + objc: L50 hostile ensemble recall +20.00pp above LWM (0.00% → 20.00%)
  + ole: L50 hostile ensemble recall +1.02pp above LWM (80.90% → 81.92%)
  + package.json: L50 hostile ensemble recall +3.39pp above LWM (85.89% → 89.28%)
  + perl: L50 hostile ensemble recall +4.82pp above LWM (51.28% → 56.10%)
  + php: L50 hostile ensemble recall +5.03pp above LWM (43.22% → 48.25%)
  + pkg-info: L50 hostile ensemble recall +0.94pp above LWM (94.75% → 95.69%)
  + ruby: L50 hostile ensemble recall +1.68pp above LWM (41.18% → 42.86%)
  + shell: L50 hostile ensemble recall +1.18pp above LWM (72.05% → 73.23%)
  + whl: L50 hostile ensemble recall +37.50pp above LWM (0.00% → 37.50%)
  + xml: L50 hostile ensemble recall +6.95pp above LWM (2.52% → 9.47%)

1 DEPLOYED-TOLERANCE regression(s) (vs currently-deployed bundle /home/t/.local/share/litmus/models/azoth) — THIS IS WHAT BLOCKS THE DEPLOY:
  - pdf: L50 hostile ENSEMBLE recall dropped 2.61pp (7.87% → 5.26%; tolerance 1.70pp; deployed 95% CI lower = 7.52%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - docx: L50 hostile ENSEMBLE recall dropped 1.01pp BELOW LOW-WATER-MARK (79.57% → 78.56%; LWM tolerance 0.90pp)

net-improvement-fallback DID NOT rescue: net malware-caught delta = -467 TPs across 78 compared filetypes; worst high-volume drop (>=1500 mal) = 2.61pp on 'pdf' (cap = 5.00pp); worst drop overall = 2.61pp on 'pdf' (small-route, not gated)
  reason: aggregate TP delta is not positive

compared 78 filetypes (mal≥1, ben≥1); 5 below threshold and skipped.

blocked by: deployed-tolerance gate (1 filetype(s) regressed vs deployed beyond the 1.70pp tolerance; see list above for the actual drops), low-water-mark gate (1 filetype(s) below LWM beyond the 0.90pp tolerance vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run, or pass --net-improvement-fallback to ship a net-positive deploy whose only regressions are on small routes (below --catastrophe-min-mal). A high-volume filetype cratering past --max-net-route-regression blocks regardless; AZOTH_ALLOW_REGRESSION is the only override for that.
make[1]: *** [Makefile:1317: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')
