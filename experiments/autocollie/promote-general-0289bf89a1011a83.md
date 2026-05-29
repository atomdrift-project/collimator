# Promote REJECTED — `0289bf89a1011a83` on `general`

Generated 2026-05-27T03:36:47Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-27T03-31-50_20260527T031724-promote-0289bf89a1011a83_azoth-validate.log; tail: .venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-general-0289bf89a1011a83
staged runtime azoth bundle: /tmp/tmp.j1fIwOdo4E
azoth bundle ok: /tmp/tmp.j1fIwOdo4E
--source-bundle out/models/azoth: 1 routes changed → 66 filetypes impacted, 0 unimpacted (drift treated as pre-existing)

ensemble improvements (≥0.10pp):
  elf: L3 hostile ensemble recall +1.89pp (93.30% → 95.19%)
  go: L3 hostile ensemble recall +0.17pp (1.02% → 1.19%)
  pe: L3 hostile ensemble recall +0.48pp (64.17% → 64.65%)
  png: L3 hostile ensemble recall +4.72pp (4.26% → 8.98%)
  powershell: L3 hostile ensemble recall +1.15pp (31.15% → 32.31%)
  xls: L3 hostile ensemble recall +0.31pp (95.22% → 95.53%)

per-route improvements (≥0.10pp, informational):
  csharp :: filetypes/csharp recall@3FP/M +5.56pp (32.05% → 37.61%)
  java_class :: filetypes/java_class recall@3FP/M +4.07pp (84.30% → 88.37%)
  png :: filetypes/png recall@3FP/M +8.98pp (0.00% → 8.98%)
  powershell :: filetypes/powershell recall@3FP/M +0.38pp (76.15% → 76.54%)

per-route regressions (informational; does not block deploy):
  jpeg :: filegroups/media recall@3FP/M dropped 2.34pp (17.19% → 14.84%)
  perl :: filetypes/perl recall@3FP/M dropped 3.70pp (88.89% → 85.19%)
  xml :: filetypes/xml recall@3FP/M dropped 4.45pp (5.82% → 1.37%)

15 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + c: L3 hostile ensemble recall +2.72pp above LWM (10.02% → 12.74%)
  + elf: L3 hostile ensemble recall +2.40pp above LWM (92.79% → 95.19%)
  + java_class: L3 hostile ensemble recall +2.89pp above LWM (73.41% → 76.30%)
  + javascript: L3 hostile ensemble recall +8.43pp above LWM (66.20% → 74.63%)
  + lnk: L3 hostile ensemble recall +13.03pp above LWM (48.66% → 61.69%)
  + package.json: L3 hostile ensemble recall +3.79pp above LWM (86.78% → 90.57%)
  + pdf: L3 hostile ensemble recall +1.09pp above LWM (6.41% → 7.50%)
  + pe: L3 hostile ensemble recall +2.69pp above LWM (61.96% → 64.65%)
  + perl: L3 hostile ensemble recall +3.70pp above LWM (77.78% → 81.48%)
  + plist: L3 hostile ensemble recall +1.47pp above LWM (2.94% → 4.41%)
  + png: L3 hostile ensemble recall +7.91pp above LWM (1.07% → 8.98%)
  + powershell: L3 hostile ensemble recall +2.69pp above LWM (29.62% → 32.31%)
  + python: L3 hostile ensemble recall +1.44pp above LWM (64.28% → 65.71%)
  + xls: L3 hostile ensemble recall +3.08pp above LWM (92.44% → 95.53%)
  + xml: L3 hostile ensemble recall +4.11pp above LWM (2.74% → 6.85%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - csharp: L3 hostile ENSEMBLE recall dropped 2.99pp BELOW LOW-WATER-MARK (25.21% → 22.22%; LWM tolerance 0.90pp)

compared 63 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: low-water-mark gate (0.90pp vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1136: azoth-validate] Error 1)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9988)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `0289bf89a1011a83` | `57a6c7593efdf4cc` | `95722da743d9d451` |
| PR AUC | 0.9988 | 0.9999 | 0.9997 |
| ROC AUC | 0.9988 | 0.9997 | 0.9997 |
| F1 | 0.9843 | 0.9948 | 0.9913 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-27T03-31-50_20260527T031724-promote-0289bf89a1011a83_azoth-validate.log; tail: .venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-general-0289bf89a1011a83
staged runtime azoth bundle: /tmp/tmp.j1fIwOdo4E
azoth bundle ok: /tmp/tmp.j1fIwOdo4E
--source-bundle out/models/azoth: 1 routes changed → 66 filetypes impacted, 0 unimpacted (drift treated as pre-existing)

ensemble improvements (≥0.10pp):
  elf: L3 hostile ensemble recall +1.89pp (93.30% → 95.19%)
  go: L3 hostile ensemble recall +0.17pp (1.02% → 1.19%)
  pe: L3 hostile ensemble recall +0.48pp (64.17% → 64.65%)
  png: L3 hostile ensemble recall +4.72pp (4.26% → 8.98%)
  powershell: L3 hostile ensemble recall +1.15pp (31.15% → 32.31%)
  xls: L3 hostile ensemble recall +0.31pp (95.22% → 95.53%)

per-route improvements (≥0.10pp, informational):
  csharp :: filetypes/csharp recall@3FP/M +5.56pp (32.05% → 37.61%)
  java_class :: filetypes/java_class recall@3FP/M +4.07pp (84.30% → 88.37%)
  png :: filetypes/png recall@3FP/M +8.98pp (0.00% → 8.98%)
  powershell :: filetypes/powershell recall@3FP/M +0.38pp (76.15% → 76.54%)

per-route regressions (informational; does not block deploy):
  jpeg :: filegroups/media recall@3FP/M dropped 2.34pp (17.19% → 14.84%)
  perl :: filetypes/perl recall@3FP/M dropped 3.70pp (88.89% → 85.19%)
  xml :: filetypes/xml recall@3FP/M dropped 4.45pp (5.82% → 1.37%)

15 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + c: L3 hostile ensemble recall +2.72pp above LWM (10.02% → 12.74%)
  + elf: L3 hostile ensemble recall +2.40pp above LWM (92.79% → 95.19%)
  + java_class: L3 hostile ensemble recall +2.89pp above LWM (73.41% → 76.30%)
  + javascript: L3 hostile ensemble recall +8.43pp above LWM (66.20% → 74.63%)
  + lnk: L3 hostile ensemble recall +13.03pp above LWM (48.66% → 61.69%)
  + package.json: L3 hostile ensemble recall +3.79pp above LWM (86.78% → 90.57%)
  + pdf: L3 hostile ensemble recall +1.09pp above LWM (6.41% → 7.50%)
  + pe: L3 hostile ensemble recall +2.69pp above LWM (61.96% → 64.65%)
  + perl: L3 hostile ensemble recall +3.70pp above LWM (77.78% → 81.48%)
  + plist: L3 hostile ensemble recall +1.47pp above LWM (2.94% → 4.41%)
  + png: L3 hostile ensemble recall +7.91pp above LWM (1.07% → 8.98%)
  + powershell: L3 hostile ensemble recall +2.69pp above LWM (29.62% → 32.31%)
  + python: L3 hostile ensemble recall +1.44pp above LWM (64.28% → 65.71%)
  + xls: L3 hostile ensemble recall +3.08pp above LWM (92.44% → 95.53%)
  + xml: L3 hostile ensemble recall +4.11pp above LWM (2.74% → 6.85%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - csharp: L3 hostile ENSEMBLE recall dropped 2.99pp BELOW LOW-WATER-MARK (25.21% → 22.22%; LWM tolerance 0.90pp)

compared 63 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: low-water-mark gate (0.90pp vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1136: azoth-validate] Error 1)
