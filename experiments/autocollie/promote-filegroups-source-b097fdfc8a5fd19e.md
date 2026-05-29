# Promote REJECTED — `b097fdfc8a5fd19e` on `filegroups/source`

Generated 2026-05-28T09:32:48Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-28T09-25-34_20260528T092313-promote-b097fdfc8a5fd19e_azoth-validate.log; tail: per-route improvements (≥0.10pp, informational):
  c :: filegroups/source recall@3FP/M +1.08pp (12.68% → 13.75%)
  c :: filetypes/c recall@3FP/M +4.70pp (11.94% → 16.64%)
  elf :: filetypes/elf recall@3FP/M +2.83pp (93.35% → 96.18%)
  go :: filegroups/source recall@3FP/M +3.14pp (2.12% → 5.27%)
  go :: filetypes/go recall@3FP/M +2.29pp (4.84% → 7.14%)
  javascript :: filetypes/javascript recall@3FP/M +8.46pp (69.53% → 77.99%)
  rust :: filegroups/source recall@3FP/M +2.44pp (2.44% → 4.88%)
  shell :: filetypes/shell recall@3FP/M +32.15pp (55.01% → 87.16%)

per-route regressions (informational; does not block deploy):
  kotlin :: filegroups/source recall@3FP/M dropped 9.84pp (79.76% → 69.91%)

25 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + 7z: L3 hostile ensemble recall +14.84pp above LWM (72.74% → 87.59%)
  + c: L3 hostile ensemble recall +4.07pp above LWM (10.02% → 14.09%)
  + cab: L3 hostile ensemble recall +46.55pp above LWM (3.45% → 50.00%)
  + chrome-manifest: L3 hostile ensemble recall +16.67pp above LWM (50.00% → 66.67%)
  + crx: L3 hostile ensemble recall +10.81pp above LWM (0.00% → 10.81%)
  + docx: L3 hostile ensemble recall +1.09pp above LWM (71.59% → 72.68%)
  + go: L3 hostile ensemble recall +3.40pp above LWM (1.36% → 4.76%)
  + html: L3 hostile ensemble recall +83.33pp above LWM (16.67% → 100.00%)
  + javascript: L3 hostile ensemble recall +10.08pp above LWM (66.20% → 76.28%)
  + jpeg: L3 hostile ensemble recall +9.12pp above LWM (1.56% → 10.69%)
  + kotlin: L3 hostile ensemble recall +3.79pp above LWM (52.67% → 56.46%)
  + lnk: L3 hostile ensemble recall +22.72pp above LWM (48.66% → 71.38%)
  + package.json: L3 hostile ensemble recall +2.50pp above LWM (86.78% → 89.28%)
  + pe: L3 hostile ensemble recall +7.30pp above LWM (61.96% → 69.26%)
  + perl: L3 hostile ensemble recall +11.51pp above LWM (77.78% → 89.29%)
  + php: L3 hostile ensemble recall +4.12pp above LWM (62.11% → 66.23%)
  + plist: L3 hostile ensemble recall +1.47pp above LWM (2.94% → 4.41%)
  + png: L3 hostile ensemble recall +7.72pp above LWM (1.07% → 8.79%)
  + tar: L3 hostile ensemble recall +35.37pp above LWM (62.00% → 97.37%)
  + tar.gz: L3 hostile ensemble recall +12.57pp above LWM (56.69% → 69.27%)
  + xls: L3 hostile ensemble recall +2.72pp above LWM (92.44% → 95.16%)
  + xlsx: L3 hostile ensemble recall +4.47pp above LWM (29.01% → 33.48%)
  + xml: L3 hostile ensemble recall +6.06pp above LWM (2.74% → 8.79%)
  + zip: L3 hostile ensemble recall +11.38pp above LWM (40.61% → 51.99%)
  + zst: L3 hostile ensemble recall +1.98pp above LWM (76.60% → 78.58%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - csharp: L3 hostile ENSEMBLE recall dropped 2.33pp BELOW LOW-WATER-MARK (25.21% → 22.88%; LWM tolerance 0.90pp)

compared 64 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: low-water-mark gate (0.90pp vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[1]: *** [Makefile:1136: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9990)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `b097fdfc8a5fd19e` | `f6c3c2e27d25a516` | `6eff07f30a8c8f51` |
| PR AUC | 0.9990 | 0.9990 | 0.9991 |
| ROC AUC | 0.9982 | 0.9981 | 0.9983 |
| F1 | 0.9781 | 0.9829 | 0.9822 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-28T09-25-34_20260528T092313-promote-b097fdfc8a5fd19e_azoth-validate.log; tail: per-route improvements (≥0.10pp, informational):
  c :: filegroups/source recall@3FP/M +1.08pp (12.68% → 13.75%)
  c :: filetypes/c recall@3FP/M +4.70pp (11.94% → 16.64%)
  elf :: filetypes/elf recall@3FP/M +2.83pp (93.35% → 96.18%)
  go :: filegroups/source recall@3FP/M +3.14pp (2.12% → 5.27%)
  go :: filetypes/go recall@3FP/M +2.29pp (4.84% → 7.14%)
  javascript :: filetypes/javascript recall@3FP/M +8.46pp (69.53% → 77.99%)
  rust :: filegroups/source recall@3FP/M +2.44pp (2.44% → 4.88%)
  shell :: filetypes/shell recall@3FP/M +32.15pp (55.01% → 87.16%)

per-route regressions (informational; does not block deploy):
  kotlin :: filegroups/source recall@3FP/M dropped 9.84pp (79.76% → 69.91%)

25 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + 7z: L3 hostile ensemble recall +14.84pp above LWM (72.74% → 87.59%)
  + c: L3 hostile ensemble recall +4.07pp above LWM (10.02% → 14.09%)
  + cab: L3 hostile ensemble recall +46.55pp above LWM (3.45% → 50.00%)
  + chrome-manifest: L3 hostile ensemble recall +16.67pp above LWM (50.00% → 66.67%)
  + crx: L3 hostile ensemble recall +10.81pp above LWM (0.00% → 10.81%)
  + docx: L3 hostile ensemble recall +1.09pp above LWM (71.59% → 72.68%)
  + go: L3 hostile ensemble recall +3.40pp above LWM (1.36% → 4.76%)
  + html: L3 hostile ensemble recall +83.33pp above LWM (16.67% → 100.00%)
  + javascript: L3 hostile ensemble recall +10.08pp above LWM (66.20% → 76.28%)
  + jpeg: L3 hostile ensemble recall +9.12pp above LWM (1.56% → 10.69%)
  + kotlin: L3 hostile ensemble recall +3.79pp above LWM (52.67% → 56.46%)
  + lnk: L3 hostile ensemble recall +22.72pp above LWM (48.66% → 71.38%)
  + package.json: L3 hostile ensemble recall +2.50pp above LWM (86.78% → 89.28%)
  + pe: L3 hostile ensemble recall +7.30pp above LWM (61.96% → 69.26%)
  + perl: L3 hostile ensemble recall +11.51pp above LWM (77.78% → 89.29%)
  + php: L3 hostile ensemble recall +4.12pp above LWM (62.11% → 66.23%)
  + plist: L3 hostile ensemble recall +1.47pp above LWM (2.94% → 4.41%)
  + png: L3 hostile ensemble recall +7.72pp above LWM (1.07% → 8.79%)
  + tar: L3 hostile ensemble recall +35.37pp above LWM (62.00% → 97.37%)
  + tar.gz: L3 hostile ensemble recall +12.57pp above LWM (56.69% → 69.27%)
  + xls: L3 hostile ensemble recall +2.72pp above LWM (92.44% → 95.16%)
  + xlsx: L3 hostile ensemble recall +4.47pp above LWM (29.01% → 33.48%)
  + xml: L3 hostile ensemble recall +6.06pp above LWM (2.74% → 8.79%)
  + zip: L3 hostile ensemble recall +11.38pp above LWM (40.61% → 51.99%)
  + zst: L3 hostile ensemble recall +1.98pp above LWM (76.60% → 78.58%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - csharp: L3 hostile ENSEMBLE recall dropped 2.33pp BELOW LOW-WATER-MARK (25.21% → 22.88%; LWM tolerance 0.90pp)

compared 64 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: low-water-mark gate (0.90pp vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[1]: *** [Makefile:1136: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')
