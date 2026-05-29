# Promote REJECTED — `fa5823cbed9d49a4` on `filegroups/documents`

Generated 2026-05-25T20:28:38Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-25T20-25-14_20260525T202451-promote-fa5823cbed9d49a4_azoth-validate.log; tail:   java_class: L3 hostile ensemble recall +8.09pp (73.41% → 81.50%)
  javascript: L3 hostile ensemble recall +5.92pp (66.20% → 72.12%)
  package.json: L3 hostile ensemble recall +4.35pp (86.78% → 91.12%)
  pdf: L3 hostile ensemble recall +14.44pp (6.41% → 20.85%)
  perl: L3 hostile ensemble recall +7.41pp (77.78% → 85.19%)
  xls: L3 hostile ensemble recall +1.62pp (92.44% → 94.06%)
  xlsx: L3 hostile ensemble recall +4.51pp (29.01% → 33.53%)
  xml: L3 hostile ensemble recall +8.22pp (2.74% → 10.96%)

per-route improvements (≥0.10pp, informational):
  c :: filetypes/c recall@3FP/M +0.28pp (13.53% → 13.82%)
  elf :: filetypes/elf recall@3FP/M +3.72pp (93.40% → 97.12%)
  go :: filetypes/go recall@3FP/M +0.34pp (4.84% → 5.18%)
  java_class :: filetypes/java_class recall@3FP/M +1.64pp (82.66% → 84.30%)
  javascript :: filetypes/javascript recall@3FP/M +11.24pp (65.71% → 76.95%)
  ole :: filegroups/documents recall@3FP/M +5.62pp (91.70% → 97.32%)
  package.json :: filegroups/config recall@3FP/M +0.92pp (98.71% → 99.63%)
  package.json :: filetypes/package.json recall@3FP/M +1.02pp (98.66% → 99.68%)
  pdf :: filegroups/documents recall@3FP/M +66.81pp (8.41% → 75.22%)
  perl :: filetypes/perl recall@3FP/M +3.70pp (85.19% → 88.89%)
  pkg-info :: filetypes/pkg-info recall@3FP/M +0.24pp (99.69% → 99.92%)
  rtf :: filegroups/documents recall@3FP/M +0.93pp (96.74% → 97.67%)
  xls :: filetypes/xls recall@3FP/M +1.15pp (95.99% → 97.15%)
  xml :: filegroups/config recall@3FP/M +7.88pp (3.42% → 11.30%)
  xml :: filetypes/xml recall@3FP/M +4.11pp (1.71% → 5.82%)

per-route regressions (informational; does not block deploy):
  pdf :: filetypes/pdf recall@3FP/M dropped 23.17pp (96.53% → 73.36%)

9 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + c: L3 hostile ensemble recall +1.30pp above LWM (10.02% → 11.33%)
  + java_class: L3 hostile ensemble recall +8.09pp above LWM (73.41% → 81.50%)
  + javascript: L3 hostile ensemble recall +5.92pp above LWM (66.20% → 72.12%)
  + package.json: L3 hostile ensemble recall +4.35pp above LWM (86.78% → 91.12%)
  + pdf: L3 hostile ensemble recall +14.44pp above LWM (6.41% → 20.85%)
  + perl: L3 hostile ensemble recall +7.41pp above LWM (77.78% → 85.19%)
  + xls: L3 hostile ensemble recall +1.62pp above LWM (92.44% → 94.06%)
  + xlsx: L3 hostile ensemble recall +4.51pp above LWM (29.01% → 33.53%)
  + xml: L3 hostile ensemble recall +8.22pp above LWM (2.74% → 10.96%)

2 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - doc: L3 hostile ENSEMBLE recall dropped 18.18pp BELOW LOW-WATER-MARK (90.99% → 72.80%; LWM tolerance 0.90pp)
  - html: L3 hostile ENSEMBLE recall dropped 16.67pp BELOW LOW-WATER-MARK (16.67% → 0.00%; LWM tolerance 0.90pp)

compared 63 filetypes (mal≥1, ben≥1); 2 below threshold and skipped.

blocked by: deployed-tolerance gate (1.70pp), low-water-mark gate (0.90pp vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1136: azoth-validate] Error 1)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 1.0000)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `fa5823cbed9d49a4` | `3213e1fdd0123bde` | `71c89464a47b59da` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9991 | 0.9997 | 0.9997 |
| F1 | 0.9961 | 0.9980 | 0.9980 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-25T20-25-14_20260525T202451-promote-fa5823cbed9d49a4_azoth-validate.log; tail:   java_class: L3 hostile ensemble recall +8.09pp (73.41% → 81.50%)
  javascript: L3 hostile ensemble recall +5.92pp (66.20% → 72.12%)
  package.json: L3 hostile ensemble recall +4.35pp (86.78% → 91.12%)
  pdf: L3 hostile ensemble recall +14.44pp (6.41% → 20.85%)
  perl: L3 hostile ensemble recall +7.41pp (77.78% → 85.19%)
  xls: L3 hostile ensemble recall +1.62pp (92.44% → 94.06%)
  xlsx: L3 hostile ensemble recall +4.51pp (29.01% → 33.53%)
  xml: L3 hostile ensemble recall +8.22pp (2.74% → 10.96%)

per-route improvements (≥0.10pp, informational):
  c :: filetypes/c recall@3FP/M +0.28pp (13.53% → 13.82%)
  elf :: filetypes/elf recall@3FP/M +3.72pp (93.40% → 97.12%)
  go :: filetypes/go recall@3FP/M +0.34pp (4.84% → 5.18%)
  java_class :: filetypes/java_class recall@3FP/M +1.64pp (82.66% → 84.30%)
  javascript :: filetypes/javascript recall@3FP/M +11.24pp (65.71% → 76.95%)
  ole :: filegroups/documents recall@3FP/M +5.62pp (91.70% → 97.32%)
  package.json :: filegroups/config recall@3FP/M +0.92pp (98.71% → 99.63%)
  package.json :: filetypes/package.json recall@3FP/M +1.02pp (98.66% → 99.68%)
  pdf :: filegroups/documents recall@3FP/M +66.81pp (8.41% → 75.22%)
  perl :: filetypes/perl recall@3FP/M +3.70pp (85.19% → 88.89%)
  pkg-info :: filetypes/pkg-info recall@3FP/M +0.24pp (99.69% → 99.92%)
  rtf :: filegroups/documents recall@3FP/M +0.93pp (96.74% → 97.67%)
  xls :: filetypes/xls recall@3FP/M +1.15pp (95.99% → 97.15%)
  xml :: filegroups/config recall@3FP/M +7.88pp (3.42% → 11.30%)
  xml :: filetypes/xml recall@3FP/M +4.11pp (1.71% → 5.82%)

per-route regressions (informational; does not block deploy):
  pdf :: filetypes/pdf recall@3FP/M dropped 23.17pp (96.53% → 73.36%)

9 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + c: L3 hostile ensemble recall +1.30pp above LWM (10.02% → 11.33%)
  + java_class: L3 hostile ensemble recall +8.09pp above LWM (73.41% → 81.50%)
  + javascript: L3 hostile ensemble recall +5.92pp above LWM (66.20% → 72.12%)
  + package.json: L3 hostile ensemble recall +4.35pp above LWM (86.78% → 91.12%)
  + pdf: L3 hostile ensemble recall +14.44pp above LWM (6.41% → 20.85%)
  + perl: L3 hostile ensemble recall +7.41pp above LWM (77.78% → 85.19%)
  + xls: L3 hostile ensemble recall +1.62pp above LWM (92.44% → 94.06%)
  + xlsx: L3 hostile ensemble recall +4.51pp above LWM (29.01% → 33.53%)
  + xml: L3 hostile ensemble recall +8.22pp above LWM (2.74% → 10.96%)

2 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - doc: L3 hostile ENSEMBLE recall dropped 18.18pp BELOW LOW-WATER-MARK (90.99% → 72.80%; LWM tolerance 0.90pp)
  - html: L3 hostile ENSEMBLE recall dropped 16.67pp BELOW LOW-WATER-MARK (16.67% → 0.00%; LWM tolerance 0.90pp)

compared 63 filetypes (mal≥1, ben≥1); 2 below threshold and skipped.

blocked by: deployed-tolerance gate (1.70pp), low-water-mark gate (0.90pp vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1136: azoth-validate] Error 1)
