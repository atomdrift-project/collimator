# Promote REJECTED — `23ac532f6c6a7756` on `filetypes/rtf`

Generated 2026-05-25T21:46:35Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-25T21-43-08_20260525T214301-promote-23ac532f6c6a7756_azoth-validate.log; tail:   python: L3 hostile ensemble recall +2.05pp (64.28% → 66.33%)
  xls: L3 hostile ensemble recall +2.78pp (92.44% → 95.22%)
  xml: L3 hostile ensemble recall +8.22pp (2.74% → 10.96%)

per-route improvements (≥0.10pp, informational):
  c :: filetypes/c recall@3FP/M +0.28pp (13.53% → 13.82%)
  elf :: filetypes/elf recall@3FP/M +3.72pp (93.40% → 97.12%)
  go :: filetypes/go recall@3FP/M +0.34pp (4.84% → 5.18%)
  groovy :: filetypes/groovy recall@3FP/M +6.67pp (0.00% → 6.67%)
  java_class :: filegroups/portable recall@3FP/M +2.23pp (83.24% → 85.47%)
  java_class :: filetypes/java_class recall@3FP/M +1.64pp (82.66% → 84.30%)
  javascript :: filetypes/javascript recall@3FP/M +11.24pp (65.71% → 76.95%)
  package.json :: filegroups/config recall@3FP/M +0.92pp (98.71% → 99.63%)
  package.json :: filetypes/package.json recall@3FP/M +1.02pp (98.66% → 99.68%)
  perl :: filetypes/perl recall@3FP/M +3.70pp (85.19% → 88.89%)
  pkg-info :: filetypes/pkg-info recall@3FP/M +0.24pp (99.69% → 99.92%)
  powershell :: filetypes/powershell recall@3FP/M +1.54pp (74.62% → 76.15%)
  python :: filetypes/python recall@3FP/M +2.97pp (68.37% → 71.33%)
  xls :: filetypes/xls recall@3FP/M +1.15pp (95.99% → 97.15%)
  xml :: filegroups/config recall@3FP/M +7.88pp (3.42% → 11.30%)
  xml :: filetypes/xml recall@3FP/M +4.11pp (1.71% → 5.82%)

per-route regressions (informational; does not block deploy):
  lnk :: filetypes/lnk recall@3FP/M dropped 11.65pp (70.50% → 58.85%)
  pdf :: filetypes/pdf recall@3FP/M dropped 23.17pp (96.53% → 73.36%)
  rtf :: filetypes/rtf recall@3FP/M dropped 98.14pp (98.14% → 0.00%)

12 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + c: L3 hostile ensemble recall +1.30pp above LWM (10.02% → 11.33%)
  + java_class: L3 hostile ensemble recall +2.89pp above LWM (73.41% → 76.30%)
  + javascript: L3 hostile ensemble recall +5.92pp above LWM (66.20% → 72.12%)
  + lnk: L3 hostile ensemble recall +13.03pp above LWM (48.66% → 61.69%)
  + package.json: L3 hostile ensemble recall +4.35pp above LWM (86.78% → 91.12%)
  + pdf: L3 hostile ensemble recall +1.09pp above LWM (6.41% → 7.50%)
  + perl: L3 hostile ensemble recall +7.41pp above LWM (77.78% → 85.19%)
  + png: L3 hostile ensemble recall +3.20pp above LWM (1.07% → 4.26%)
  + powershell: L3 hostile ensemble recall +1.54pp above LWM (29.62% → 31.15%)
  + python: L3 hostile ensemble recall +2.05pp above LWM (64.28% → 66.33%)
  + xls: L3 hostile ensemble recall +2.78pp above LWM (92.44% → 95.22%)
  + xml: L3 hostile ensemble recall +8.22pp above LWM (2.74% → 10.96%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - rtf: L3 hostile ENSEMBLE recall dropped 2.33pp BELOW LOW-WATER-MARK (97.67% → 95.35%; LWM tolerance 0.90pp)

compared 63 filetypes (mal≥1, ben≥1); 2 below threshold and skipped.

blocked by: low-water-mark gate (0.90pp vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1136: azoth-validate] Error 1)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9780)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `23ac532f6c6a7756` | `803d2b0157ec5b48` | `8daf968773d3fb70` |
| PR AUC | 0.9780 | 0.9784 | 0.9784 |
| ROC AUC | 0.5000 | 0.5000 | 0.5000 |
| F1 | 0.9889 | 0.9891 | 0.9891 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-25T21-43-08_20260525T214301-promote-23ac532f6c6a7756_azoth-validate.log; tail:   python: L3 hostile ensemble recall +2.05pp (64.28% → 66.33%)
  xls: L3 hostile ensemble recall +2.78pp (92.44% → 95.22%)
  xml: L3 hostile ensemble recall +8.22pp (2.74% → 10.96%)

per-route improvements (≥0.10pp, informational):
  c :: filetypes/c recall@3FP/M +0.28pp (13.53% → 13.82%)
  elf :: filetypes/elf recall@3FP/M +3.72pp (93.40% → 97.12%)
  go :: filetypes/go recall@3FP/M +0.34pp (4.84% → 5.18%)
  groovy :: filetypes/groovy recall@3FP/M +6.67pp (0.00% → 6.67%)
  java_class :: filegroups/portable recall@3FP/M +2.23pp (83.24% → 85.47%)
  java_class :: filetypes/java_class recall@3FP/M +1.64pp (82.66% → 84.30%)
  javascript :: filetypes/javascript recall@3FP/M +11.24pp (65.71% → 76.95%)
  package.json :: filegroups/config recall@3FP/M +0.92pp (98.71% → 99.63%)
  package.json :: filetypes/package.json recall@3FP/M +1.02pp (98.66% → 99.68%)
  perl :: filetypes/perl recall@3FP/M +3.70pp (85.19% → 88.89%)
  pkg-info :: filetypes/pkg-info recall@3FP/M +0.24pp (99.69% → 99.92%)
  powershell :: filetypes/powershell recall@3FP/M +1.54pp (74.62% → 76.15%)
  python :: filetypes/python recall@3FP/M +2.97pp (68.37% → 71.33%)
  xls :: filetypes/xls recall@3FP/M +1.15pp (95.99% → 97.15%)
  xml :: filegroups/config recall@3FP/M +7.88pp (3.42% → 11.30%)
  xml :: filetypes/xml recall@3FP/M +4.11pp (1.71% → 5.82%)

per-route regressions (informational; does not block deploy):
  lnk :: filetypes/lnk recall@3FP/M dropped 11.65pp (70.50% → 58.85%)
  pdf :: filetypes/pdf recall@3FP/M dropped 23.17pp (96.53% → 73.36%)
  rtf :: filetypes/rtf recall@3FP/M dropped 98.14pp (98.14% → 0.00%)

12 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + c: L3 hostile ensemble recall +1.30pp above LWM (10.02% → 11.33%)
  + java_class: L3 hostile ensemble recall +2.89pp above LWM (73.41% → 76.30%)
  + javascript: L3 hostile ensemble recall +5.92pp above LWM (66.20% → 72.12%)
  + lnk: L3 hostile ensemble recall +13.03pp above LWM (48.66% → 61.69%)
  + package.json: L3 hostile ensemble recall +4.35pp above LWM (86.78% → 91.12%)
  + pdf: L3 hostile ensemble recall +1.09pp above LWM (6.41% → 7.50%)
  + perl: L3 hostile ensemble recall +7.41pp above LWM (77.78% → 85.19%)
  + png: L3 hostile ensemble recall +3.20pp above LWM (1.07% → 4.26%)
  + powershell: L3 hostile ensemble recall +1.54pp above LWM (29.62% → 31.15%)
  + python: L3 hostile ensemble recall +2.05pp above LWM (64.28% → 66.33%)
  + xls: L3 hostile ensemble recall +2.78pp above LWM (92.44% → 95.22%)
  + xml: L3 hostile ensemble recall +8.22pp above LWM (2.74% → 10.96%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - rtf: L3 hostile ENSEMBLE recall dropped 2.33pp BELOW LOW-WATER-MARK (97.67% → 95.35%; LWM tolerance 0.90pp)

compared 63 filetypes (mal≥1, ben≥1); 2 below threshold and skipped.

blocked by: low-water-mark gate (0.90pp vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1136: azoth-validate] Error 1)
