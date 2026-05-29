# Promote REJECTED — `3370631402c9fef2` on `filegroups/documents`

Generated 2026-05-28T11:52:20Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-28T11-45-50_20260528T114506-promote-3370631402c9fef2_azoth-validate.log; tail:   c :: filetypes/c recall@3FP/M +2.04pp (11.94% → 13.98%)
  elf :: filetypes/elf recall@3FP/M +2.67pp (93.35% → 96.01%)
  go :: filetypes/go recall@3FP/M +2.29pp (4.84% → 7.14%)
  javascript :: filetypes/javascript recall@3FP/M +8.46pp (69.53% → 77.99%)
  ole :: filegroups/documents recall@3FP/M +0.87pp (93.45% → 94.32%)
  pdf :: filegroups/documents recall@3FP/M +54.15pp (19.90% → 74.06%)
  rtf :: filegroups/documents recall@3FP/M +1.39pp (97.22% → 98.61%)
  shell :: filetypes/shell recall@3FP/M +32.15pp (55.01% → 87.16%)

per-route regressions (informational; does not block deploy):
  xlsx :: filegroups/documents recall@3FP/M dropped 6.46pp (91.62% → 85.15%)

26 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + 7z: L3 hostile ensemble recall +14.84pp above LWM (72.74% → 87.59%)
  + c: L3 hostile ensemble recall +2.26pp above LWM (10.02% → 12.28%)
  + cab: L3 hostile ensemble recall +46.55pp above LWM (3.45% → 50.00%)
  + chrome-manifest: L3 hostile ensemble recall +16.67pp above LWM (50.00% → 66.67%)
  + crx: L3 hostile ensemble recall +10.81pp above LWM (0.00% → 10.81%)
  + docx: L3 hostile ensemble recall +5.46pp above LWM (71.59% → 77.05%)
  + go: L3 hostile ensemble recall +3.40pp above LWM (1.36% → 4.76%)
  + html: L3 hostile ensemble recall +83.33pp above LWM (16.67% → 100.00%)
  + javascript: L3 hostile ensemble recall +10.08pp above LWM (66.20% → 76.28%)
  + jpeg: L3 hostile ensemble recall +9.12pp above LWM (1.56% → 10.69%)
  + lnk: L3 hostile ensemble recall +22.72pp above LWM (48.66% → 71.38%)
  + package.json: L3 hostile ensemble recall +2.50pp above LWM (86.78% → 89.28%)
  + pdf: L3 hostile ensemble recall +1.20pp above LWM (6.41% → 7.61%)
  + pe: L3 hostile ensemble recall +7.30pp above LWM (61.96% → 69.26%)
  + perl: L3 hostile ensemble recall +11.51pp above LWM (77.78% → 89.29%)
  + php: L3 hostile ensemble recall +4.12pp above LWM (62.11% → 66.23%)
  + plist: L3 hostile ensemble recall +1.47pp above LWM (2.94% → 4.41%)
  + png: L3 hostile ensemble recall +7.72pp above LWM (1.07% → 8.79%)
  + pptx: L3 hostile ensemble recall +13.64pp above LWM (9.09% → 22.73%)
  + tar: L3 hostile ensemble recall +35.37pp above LWM (62.00% → 97.37%)
  + tar.gz: L3 hostile ensemble recall +12.57pp above LWM (56.69% → 69.27%)
  + xls: L3 hostile ensemble recall +2.64pp above LWM (92.44% → 95.08%)
  + xlsx: L3 hostile ensemble recall +4.51pp above LWM (29.01% → 33.53%)
  + xml: L3 hostile ensemble recall +6.06pp above LWM (2.74% → 8.79%)
  + zip: L3 hostile ensemble recall +11.38pp above LWM (40.61% → 51.99%)
  + zst: L3 hostile ensemble recall +1.98pp above LWM (76.60% → 78.58%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - doc: L3 hostile ENSEMBLE recall dropped 18.49pp BELOW LOW-WATER-MARK (90.99% → 72.49%; LWM tolerance 0.90pp)

compared 64 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: low-water-mark gate (1 filetype(s) below LWM beyond the 0.90pp tolerance vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[1]: *** [Makefile:1136: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 1.0000)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `3370631402c9fef2` | `75faf49da5fc2eab` | `0e4bddaddae42eb1` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9997 | 0.9997 | 0.9997 |
| F1 | 0.9962 | 0.9985 | 0.9985 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-28T11-45-50_20260528T114506-promote-3370631402c9fef2_azoth-validate.log; tail:   c :: filetypes/c recall@3FP/M +2.04pp (11.94% → 13.98%)
  elf :: filetypes/elf recall@3FP/M +2.67pp (93.35% → 96.01%)
  go :: filetypes/go recall@3FP/M +2.29pp (4.84% → 7.14%)
  javascript :: filetypes/javascript recall@3FP/M +8.46pp (69.53% → 77.99%)
  ole :: filegroups/documents recall@3FP/M +0.87pp (93.45% → 94.32%)
  pdf :: filegroups/documents recall@3FP/M +54.15pp (19.90% → 74.06%)
  rtf :: filegroups/documents recall@3FP/M +1.39pp (97.22% → 98.61%)
  shell :: filetypes/shell recall@3FP/M +32.15pp (55.01% → 87.16%)

per-route regressions (informational; does not block deploy):
  xlsx :: filegroups/documents recall@3FP/M dropped 6.46pp (91.62% → 85.15%)

26 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + 7z: L3 hostile ensemble recall +14.84pp above LWM (72.74% → 87.59%)
  + c: L3 hostile ensemble recall +2.26pp above LWM (10.02% → 12.28%)
  + cab: L3 hostile ensemble recall +46.55pp above LWM (3.45% → 50.00%)
  + chrome-manifest: L3 hostile ensemble recall +16.67pp above LWM (50.00% → 66.67%)
  + crx: L3 hostile ensemble recall +10.81pp above LWM (0.00% → 10.81%)
  + docx: L3 hostile ensemble recall +5.46pp above LWM (71.59% → 77.05%)
  + go: L3 hostile ensemble recall +3.40pp above LWM (1.36% → 4.76%)
  + html: L3 hostile ensemble recall +83.33pp above LWM (16.67% → 100.00%)
  + javascript: L3 hostile ensemble recall +10.08pp above LWM (66.20% → 76.28%)
  + jpeg: L3 hostile ensemble recall +9.12pp above LWM (1.56% → 10.69%)
  + lnk: L3 hostile ensemble recall +22.72pp above LWM (48.66% → 71.38%)
  + package.json: L3 hostile ensemble recall +2.50pp above LWM (86.78% → 89.28%)
  + pdf: L3 hostile ensemble recall +1.20pp above LWM (6.41% → 7.61%)
  + pe: L3 hostile ensemble recall +7.30pp above LWM (61.96% → 69.26%)
  + perl: L3 hostile ensemble recall +11.51pp above LWM (77.78% → 89.29%)
  + php: L3 hostile ensemble recall +4.12pp above LWM (62.11% → 66.23%)
  + plist: L3 hostile ensemble recall +1.47pp above LWM (2.94% → 4.41%)
  + png: L3 hostile ensemble recall +7.72pp above LWM (1.07% → 8.79%)
  + pptx: L3 hostile ensemble recall +13.64pp above LWM (9.09% → 22.73%)
  + tar: L3 hostile ensemble recall +35.37pp above LWM (62.00% → 97.37%)
  + tar.gz: L3 hostile ensemble recall +12.57pp above LWM (56.69% → 69.27%)
  + xls: L3 hostile ensemble recall +2.64pp above LWM (92.44% → 95.08%)
  + xlsx: L3 hostile ensemble recall +4.51pp above LWM (29.01% → 33.53%)
  + xml: L3 hostile ensemble recall +6.06pp above LWM (2.74% → 8.79%)
  + zip: L3 hostile ensemble recall +11.38pp above LWM (40.61% → 51.99%)
  + zst: L3 hostile ensemble recall +1.98pp above LWM (76.60% → 78.58%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - doc: L3 hostile ENSEMBLE recall dropped 18.49pp BELOW LOW-WATER-MARK (90.99% → 72.49%; LWM tolerance 0.90pp)

compared 64 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: low-water-mark gate (1 filetype(s) below LWM beyond the 0.90pp tolerance vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[1]: *** [Makefile:1136: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')
