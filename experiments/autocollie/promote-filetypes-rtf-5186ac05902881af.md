# Promote REJECTED — `5186ac05902881af` on `filetypes/rtf`

Generated 2026-05-27T07:46:21Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-27T07-43-08_20260527T074252-promote-5186ac05902881af_azoth-validate.log; tail:   png: L3 hostile ensemble recall +4.72pp (4.26% → 8.98%)
  powershell: L3 hostile ensemble recall +1.15pp (31.15% → 32.31%)
  rust: L3 hostile ensemble recall +4.88pp (1.22% → 6.10%)
  xls: L3 hostile ensemble recall +0.31pp (95.22% → 95.53%)

per-route improvements (≥0.10pp, informational):
  csharp :: filetypes/csharp recall@3FP/M +5.56pp (32.05% → 37.61%)
  java_class :: filetypes/java_class recall@3FP/M +4.07pp (84.30% → 88.37%)
  png :: filetypes/png recall@3FP/M +8.98pp (0.00% → 8.98%)
  powershell :: filetypes/powershell recall@3FP/M +0.38pp (76.15% → 76.54%)
  rust :: filetypes/rust recall@3FP/M +2.44pp (3.05% → 5.49%)

per-route regressions (informational; does not block deploy):
  groovy :: filetypes/groovy recall@3FP/M dropped 6.67pp (6.67% → 0.00%)
  jpeg :: filegroups/media recall@3FP/M dropped 2.34pp (17.19% → 14.84%)
  makefile :: filetypes/makefile recall@3FP/M dropped 5.88pp (5.88% → 0.00%)
  perl :: filetypes/perl recall@3FP/M dropped 3.70pp (88.89% → 85.19%)
  pkg-info :: filetypes/pkg-info recall@3FP/M dropped 99.92pp (99.92% → 0.00%)
  plist :: filetypes/plist recall@3FP/M dropped 4.41pp (4.41% → 0.00%)
  rtf :: filetypes/rtf recall@3FP/M dropped 98.14pp (98.14% → 0.00%)
  xml :: filetypes/xml recall@3FP/M dropped 4.45pp (5.82% → 1.37%)

17 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + c: L3 hostile ensemble recall +2.72pp above LWM (10.02% → 12.74%)
  + csharp: L3 hostile ensemble recall +8.12pp above LWM (25.21% → 33.33%)
  + java_class: L3 hostile ensemble recall +2.89pp above LWM (73.41% → 76.30%)
  + javascript: L3 hostile ensemble recall +8.35pp above LWM (66.20% → 74.55%)
  + lnk: L3 hostile ensemble recall +13.03pp above LWM (48.66% → 61.69%)
  + package.json: L3 hostile ensemble recall +3.79pp above LWM (86.78% → 90.57%)
  + pdf: L3 hostile ensemble recall +1.09pp above LWM (6.41% → 7.50%)
  + pe: L3 hostile ensemble recall +2.21pp above LWM (61.96% → 64.17%)
  + perl: L3 hostile ensemble recall +3.70pp above LWM (77.78% → 81.48%)
  + plist: L3 hostile ensemble recall +1.47pp above LWM (2.94% → 4.41%)
  + png: L3 hostile ensemble recall +7.91pp above LWM (1.07% → 8.98%)
  + powershell: L3 hostile ensemble recall +2.69pp above LWM (29.62% → 32.31%)
  + pptx: L3 hostile ensemble recall +9.09pp above LWM (9.09% → 18.18%)
  + python: L3 hostile ensemble recall +1.44pp above LWM (64.28% → 65.71%)
  + rust: L3 hostile ensemble recall +4.88pp above LWM (1.22% → 6.10%)
  + xls: L3 hostile ensemble recall +3.08pp above LWM (92.44% → 95.53%)
  + xml: L3 hostile ensemble recall +4.11pp above LWM (2.74% → 6.85%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - rtf: L3 hostile ENSEMBLE recall dropped 2.33pp BELOW LOW-WATER-MARK (97.67% → 95.35%; LWM tolerance 0.90pp)

compared 63 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: low-water-mark gate (0.90pp vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1136: azoth-validate] Error 1)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9780)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `5186ac05902881af` | `56a54bd5eb6f5ae1` | `740489e6ee36f4a5` |
| PR AUC | 0.9780 | 0.9784 | 0.9784 |
| ROC AUC | 0.5000 | 0.5000 | 0.5000 |
| F1 | 0.9889 | 0.9891 | 0.9891 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-27T07-43-08_20260527T074252-promote-5186ac05902881af_azoth-validate.log; tail:   png: L3 hostile ensemble recall +4.72pp (4.26% → 8.98%)
  powershell: L3 hostile ensemble recall +1.15pp (31.15% → 32.31%)
  rust: L3 hostile ensemble recall +4.88pp (1.22% → 6.10%)
  xls: L3 hostile ensemble recall +0.31pp (95.22% → 95.53%)

per-route improvements (≥0.10pp, informational):
  csharp :: filetypes/csharp recall@3FP/M +5.56pp (32.05% → 37.61%)
  java_class :: filetypes/java_class recall@3FP/M +4.07pp (84.30% → 88.37%)
  png :: filetypes/png recall@3FP/M +8.98pp (0.00% → 8.98%)
  powershell :: filetypes/powershell recall@3FP/M +0.38pp (76.15% → 76.54%)
  rust :: filetypes/rust recall@3FP/M +2.44pp (3.05% → 5.49%)

per-route regressions (informational; does not block deploy):
  groovy :: filetypes/groovy recall@3FP/M dropped 6.67pp (6.67% → 0.00%)
  jpeg :: filegroups/media recall@3FP/M dropped 2.34pp (17.19% → 14.84%)
  makefile :: filetypes/makefile recall@3FP/M dropped 5.88pp (5.88% → 0.00%)
  perl :: filetypes/perl recall@3FP/M dropped 3.70pp (88.89% → 85.19%)
  pkg-info :: filetypes/pkg-info recall@3FP/M dropped 99.92pp (99.92% → 0.00%)
  plist :: filetypes/plist recall@3FP/M dropped 4.41pp (4.41% → 0.00%)
  rtf :: filetypes/rtf recall@3FP/M dropped 98.14pp (98.14% → 0.00%)
  xml :: filetypes/xml recall@3FP/M dropped 4.45pp (5.82% → 1.37%)

17 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + c: L3 hostile ensemble recall +2.72pp above LWM (10.02% → 12.74%)
  + csharp: L3 hostile ensemble recall +8.12pp above LWM (25.21% → 33.33%)
  + java_class: L3 hostile ensemble recall +2.89pp above LWM (73.41% → 76.30%)
  + javascript: L3 hostile ensemble recall +8.35pp above LWM (66.20% → 74.55%)
  + lnk: L3 hostile ensemble recall +13.03pp above LWM (48.66% → 61.69%)
  + package.json: L3 hostile ensemble recall +3.79pp above LWM (86.78% → 90.57%)
  + pdf: L3 hostile ensemble recall +1.09pp above LWM (6.41% → 7.50%)
  + pe: L3 hostile ensemble recall +2.21pp above LWM (61.96% → 64.17%)
  + perl: L3 hostile ensemble recall +3.70pp above LWM (77.78% → 81.48%)
  + plist: L3 hostile ensemble recall +1.47pp above LWM (2.94% → 4.41%)
  + png: L3 hostile ensemble recall +7.91pp above LWM (1.07% → 8.98%)
  + powershell: L3 hostile ensemble recall +2.69pp above LWM (29.62% → 32.31%)
  + pptx: L3 hostile ensemble recall +9.09pp above LWM (9.09% → 18.18%)
  + python: L3 hostile ensemble recall +1.44pp above LWM (64.28% → 65.71%)
  + rust: L3 hostile ensemble recall +4.88pp above LWM (1.22% → 6.10%)
  + xls: L3 hostile ensemble recall +3.08pp above LWM (92.44% → 95.53%)
  + xml: L3 hostile ensemble recall +4.11pp above LWM (2.74% → 6.85%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - rtf: L3 hostile ENSEMBLE recall dropped 2.33pp BELOW LOW-WATER-MARK (97.67% → 95.35%; LWM tolerance 0.90pp)

compared 63 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: low-water-mark gate (0.90pp vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1136: azoth-validate] Error 1)
