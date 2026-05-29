# Promote REJECTED — `e788920478a0ad69` on `filetypes/macho`

Generated 2026-05-25T20:32:56Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-25T20-29-48_20260525T202923-promote-e788920478a0ad69_azoth-validate.log; tail: staged runtime azoth bundle: /tmp/tmp.YOmmu66Y43
azoth bundle ok: /tmp/tmp.YOmmu66Y43
--source-bundle out/models/azoth: 1 routes changed → 1 filetypes impacted, 64 unimpacted (drift treated as pre-existing)

ensemble improvements (≥0.10pp):
  c: L3 hostile ensemble recall +1.30pp (10.02% → 11.33%)
  java_class: L3 hostile ensemble recall +8.09pp (73.41% → 81.50%)
  javascript: L3 hostile ensemble recall +5.92pp (66.20% → 72.12%)
  package.json: L3 hostile ensemble recall +4.35pp (86.78% → 91.12%)
  pdf: L3 hostile ensemble recall +1.09pp (6.41% → 7.50%)
  perl: L3 hostile ensemble recall +7.41pp (77.78% → 85.19%)
  xls: L3 hostile ensemble recall +2.78pp (92.44% → 95.22%)
  xml: L3 hostile ensemble recall +8.22pp (2.74% → 10.96%)

per-route improvements (≥0.10pp, informational):
  c :: filetypes/c recall@3FP/M +0.28pp (13.53% → 13.82%)
  elf :: filetypes/elf recall@3FP/M +3.72pp (93.40% → 97.12%)
  go :: filetypes/go recall@3FP/M +0.34pp (4.84% → 5.18%)
  java_class :: filetypes/java_class recall@3FP/M +1.64pp (82.66% → 84.30%)
  javascript :: filetypes/javascript recall@3FP/M +11.24pp (65.71% → 76.95%)
  package.json :: filegroups/config recall@3FP/M +0.92pp (98.71% → 99.63%)
  package.json :: filetypes/package.json recall@3FP/M +1.02pp (98.66% → 99.68%)
  perl :: filetypes/perl recall@3FP/M +3.70pp (85.19% → 88.89%)
  pkg-info :: filetypes/pkg-info recall@3FP/M +0.24pp (99.69% → 99.92%)
  xls :: filetypes/xls recall@3FP/M +1.15pp (95.99% → 97.15%)
  xml :: filegroups/config recall@3FP/M +7.88pp (3.42% → 11.30%)
  xml :: filetypes/xml recall@3FP/M +4.11pp (1.71% → 5.82%)

per-route regressions (informational; does not block deploy):
  pdf :: filetypes/pdf recall@3FP/M dropped 23.17pp (96.53% → 73.36%)

8 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + c: L3 hostile ensemble recall +1.30pp above LWM (10.02% → 11.33%)
  + java_class: L3 hostile ensemble recall +8.09pp above LWM (73.41% → 81.50%)
  + javascript: L3 hostile ensemble recall +5.92pp above LWM (66.20% → 72.12%)
  + package.json: L3 hostile ensemble recall +4.35pp above LWM (86.78% → 91.12%)
  + pdf: L3 hostile ensemble recall +1.09pp above LWM (6.41% → 7.50%)
  + perl: L3 hostile ensemble recall +7.41pp above LWM (77.78% → 85.19%)
  + xls: L3 hostile ensemble recall +2.78pp above LWM (92.44% → 95.22%)
  + xml: L3 hostile ensemble recall +8.22pp above LWM (2.74% → 10.96%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - macho: L3 hostile ENSEMBLE recall dropped 14.12pp BELOW LOW-WATER-MARK (86.64% → 72.52%; LWM tolerance 0.90pp)

compared 63 filetypes (mal≥1, ben≥1); 2 below threshold and skipped.

blocked by: deployed-tolerance gate (1.70pp), low-water-mark gate (0.90pp vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1136: azoth-validate] Error 1)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9992)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `e788920478a0ad69` | `9b215c3126a94421` | `36b873089ce67140` |
| PR AUC | 0.9992 | 0.9976 | 0.9976 |
| ROC AUC | 0.9998 | 0.9995 | 0.9995 |
| F1 | 0.9833 | 0.9758 | 0.9774 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-25T20-29-48_20260525T202923-promote-e788920478a0ad69_azoth-validate.log; tail: staged runtime azoth bundle: /tmp/tmp.YOmmu66Y43
azoth bundle ok: /tmp/tmp.YOmmu66Y43
--source-bundle out/models/azoth: 1 routes changed → 1 filetypes impacted, 64 unimpacted (drift treated as pre-existing)

ensemble improvements (≥0.10pp):
  c: L3 hostile ensemble recall +1.30pp (10.02% → 11.33%)
  java_class: L3 hostile ensemble recall +8.09pp (73.41% → 81.50%)
  javascript: L3 hostile ensemble recall +5.92pp (66.20% → 72.12%)
  package.json: L3 hostile ensemble recall +4.35pp (86.78% → 91.12%)
  pdf: L3 hostile ensemble recall +1.09pp (6.41% → 7.50%)
  perl: L3 hostile ensemble recall +7.41pp (77.78% → 85.19%)
  xls: L3 hostile ensemble recall +2.78pp (92.44% → 95.22%)
  xml: L3 hostile ensemble recall +8.22pp (2.74% → 10.96%)

per-route improvements (≥0.10pp, informational):
  c :: filetypes/c recall@3FP/M +0.28pp (13.53% → 13.82%)
  elf :: filetypes/elf recall@3FP/M +3.72pp (93.40% → 97.12%)
  go :: filetypes/go recall@3FP/M +0.34pp (4.84% → 5.18%)
  java_class :: filetypes/java_class recall@3FP/M +1.64pp (82.66% → 84.30%)
  javascript :: filetypes/javascript recall@3FP/M +11.24pp (65.71% → 76.95%)
  package.json :: filegroups/config recall@3FP/M +0.92pp (98.71% → 99.63%)
  package.json :: filetypes/package.json recall@3FP/M +1.02pp (98.66% → 99.68%)
  perl :: filetypes/perl recall@3FP/M +3.70pp (85.19% → 88.89%)
  pkg-info :: filetypes/pkg-info recall@3FP/M +0.24pp (99.69% → 99.92%)
  xls :: filetypes/xls recall@3FP/M +1.15pp (95.99% → 97.15%)
  xml :: filegroups/config recall@3FP/M +7.88pp (3.42% → 11.30%)
  xml :: filetypes/xml recall@3FP/M +4.11pp (1.71% → 5.82%)

per-route regressions (informational; does not block deploy):
  pdf :: filetypes/pdf recall@3FP/M dropped 23.17pp (96.53% → 73.36%)

8 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + c: L3 hostile ensemble recall +1.30pp above LWM (10.02% → 11.33%)
  + java_class: L3 hostile ensemble recall +8.09pp above LWM (73.41% → 81.50%)
  + javascript: L3 hostile ensemble recall +5.92pp above LWM (66.20% → 72.12%)
  + package.json: L3 hostile ensemble recall +4.35pp above LWM (86.78% → 91.12%)
  + pdf: L3 hostile ensemble recall +1.09pp above LWM (6.41% → 7.50%)
  + perl: L3 hostile ensemble recall +7.41pp above LWM (77.78% → 85.19%)
  + xls: L3 hostile ensemble recall +2.78pp above LWM (92.44% → 95.22%)
  + xml: L3 hostile ensemble recall +8.22pp above LWM (2.74% → 10.96%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - macho: L3 hostile ENSEMBLE recall dropped 14.12pp BELOW LOW-WATER-MARK (86.64% → 72.52%; LWM tolerance 0.90pp)

compared 63 filetypes (mal≥1, ben≥1); 2 below threshold and skipped.

blocked by: deployed-tolerance gate (1.70pp), low-water-mark gate (0.90pp vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1136: azoth-validate] Error 1)
