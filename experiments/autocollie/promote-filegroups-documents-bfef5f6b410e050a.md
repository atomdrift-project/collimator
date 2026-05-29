# Promote REJECTED — `bfef5f6b410e050a` on `filegroups/documents`

Generated 2026-05-28T03:41:29Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-28T03-36-53_20260528T033501-promote-bfef5f6b410e050a_azoth-validate.log; tail:   doc: L3 hostile ensemble recall +0.93pp (72.26% → 73.19%)
  docx: L3 hostile ensemble recall +4.92pp (72.68% → 77.60%)
  elf: L3 hostile ensemble recall +0.23pp (93.13% → 93.36%)
  ole: L3 hostile ensemble recall +0.87pp (91.27% → 92.14%)
  pdf: L3 hostile ensemble recall +3.63pp (7.30% → 10.94%)
  pptx: L3 hostile ensemble recall +18.18pp (4.55% → 22.73%)

per-route improvements (≥0.10pp, informational):
  c :: filetypes/c recall@3FP/M +4.70pp (11.94% → 16.64%)
  elf :: filetypes/elf recall@3FP/M +2.83pp (93.35% → 96.18%)
  ole :: filegroups/documents recall@3FP/M +0.87pp (93.45% → 94.32%)
  pdf :: filegroups/documents recall@3FP/M +55.46pp (19.90% → 75.36%)
  rtf :: filegroups/documents recall@3FP/M +1.85pp (97.22% → 99.07%)

24 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + 7z: L3 hostile ensemble recall +14.84pp above LWM (72.74% → 87.59%)
  + c: L3 hostile ensemble recall +2.60pp above LWM (10.02% → 12.62%)
  + cab: L3 hostile ensemble recall +46.55pp above LWM (3.45% → 50.00%)
  + chrome-manifest: L3 hostile ensemble recall +16.67pp above LWM (50.00% → 66.67%)
  + crx: L3 hostile ensemble recall +10.81pp above LWM (0.00% → 10.81%)
  + docx: L3 hostile ensemble recall +6.00pp above LWM (71.59% → 77.60%)
  + html: L3 hostile ensemble recall +83.33pp above LWM (16.67% → 100.00%)
  + jpeg: L3 hostile ensemble recall +9.12pp above LWM (1.56% → 10.69%)
  + lnk: L3 hostile ensemble recall +22.72pp above LWM (48.66% → 71.38%)
  + package.json: L3 hostile ensemble recall +2.50pp above LWM (86.78% → 89.28%)
  + pdf: L3 hostile ensemble recall +4.52pp above LWM (6.41% → 10.94%)
  + pe: L3 hostile ensemble recall +7.30pp above LWM (61.96% → 69.26%)
  + perl: L3 hostile ensemble recall +11.51pp above LWM (77.78% → 89.29%)
  + php: L3 hostile ensemble recall +4.12pp above LWM (62.11% → 66.23%)
  + plist: L3 hostile ensemble recall +1.47pp above LWM (2.94% → 4.41%)
  + png: L3 hostile ensemble recall +7.72pp above LWM (1.07% → 8.79%)
  + pptx: L3 hostile ensemble recall +13.64pp above LWM (9.09% → 22.73%)
  + tar: L3 hostile ensemble recall +35.37pp above LWM (62.00% → 97.37%)
  + tar.gz: L3 hostile ensemble recall +12.57pp above LWM (56.69% → 69.27%)
  + xls: L3 hostile ensemble recall +2.49pp above LWM (92.44% → 94.93%)
  + xlsx: L3 hostile ensemble recall +4.51pp above LWM (29.01% → 33.53%)
  + xml: L3 hostile ensemble recall +6.06pp above LWM (2.74% → 8.79%)
  + zip: L3 hostile ensemble recall +11.38pp above LWM (40.61% → 51.99%)
  + zst: L3 hostile ensemble recall +1.98pp above LWM (76.60% → 78.58%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - doc: L3 hostile ENSEMBLE recall dropped 17.79pp BELOW LOW-WATER-MARK (90.99% → 73.19%; LWM tolerance 0.90pp)

compared 64 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: low-water-mark gate (0.90pp vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[1]: *** [Makefile:1136: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 1.0000)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `bfef5f6b410e050a` | `3896f5c8f16f9508` | `9a728d755cc61d33` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9997 | 0.9997 | 0.9997 |
| F1 | 0.9951 | 0.9979 | 0.9979 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-28T03-36-53_20260528T033501-promote-bfef5f6b410e050a_azoth-validate.log; tail:   doc: L3 hostile ensemble recall +0.93pp (72.26% → 73.19%)
  docx: L3 hostile ensemble recall +4.92pp (72.68% → 77.60%)
  elf: L3 hostile ensemble recall +0.23pp (93.13% → 93.36%)
  ole: L3 hostile ensemble recall +0.87pp (91.27% → 92.14%)
  pdf: L3 hostile ensemble recall +3.63pp (7.30% → 10.94%)
  pptx: L3 hostile ensemble recall +18.18pp (4.55% → 22.73%)

per-route improvements (≥0.10pp, informational):
  c :: filetypes/c recall@3FP/M +4.70pp (11.94% → 16.64%)
  elf :: filetypes/elf recall@3FP/M +2.83pp (93.35% → 96.18%)
  ole :: filegroups/documents recall@3FP/M +0.87pp (93.45% → 94.32%)
  pdf :: filegroups/documents recall@3FP/M +55.46pp (19.90% → 75.36%)
  rtf :: filegroups/documents recall@3FP/M +1.85pp (97.22% → 99.07%)

24 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + 7z: L3 hostile ensemble recall +14.84pp above LWM (72.74% → 87.59%)
  + c: L3 hostile ensemble recall +2.60pp above LWM (10.02% → 12.62%)
  + cab: L3 hostile ensemble recall +46.55pp above LWM (3.45% → 50.00%)
  + chrome-manifest: L3 hostile ensemble recall +16.67pp above LWM (50.00% → 66.67%)
  + crx: L3 hostile ensemble recall +10.81pp above LWM (0.00% → 10.81%)
  + docx: L3 hostile ensemble recall +6.00pp above LWM (71.59% → 77.60%)
  + html: L3 hostile ensemble recall +83.33pp above LWM (16.67% → 100.00%)
  + jpeg: L3 hostile ensemble recall +9.12pp above LWM (1.56% → 10.69%)
  + lnk: L3 hostile ensemble recall +22.72pp above LWM (48.66% → 71.38%)
  + package.json: L3 hostile ensemble recall +2.50pp above LWM (86.78% → 89.28%)
  + pdf: L3 hostile ensemble recall +4.52pp above LWM (6.41% → 10.94%)
  + pe: L3 hostile ensemble recall +7.30pp above LWM (61.96% → 69.26%)
  + perl: L3 hostile ensemble recall +11.51pp above LWM (77.78% → 89.29%)
  + php: L3 hostile ensemble recall +4.12pp above LWM (62.11% → 66.23%)
  + plist: L3 hostile ensemble recall +1.47pp above LWM (2.94% → 4.41%)
  + png: L3 hostile ensemble recall +7.72pp above LWM (1.07% → 8.79%)
  + pptx: L3 hostile ensemble recall +13.64pp above LWM (9.09% → 22.73%)
  + tar: L3 hostile ensemble recall +35.37pp above LWM (62.00% → 97.37%)
  + tar.gz: L3 hostile ensemble recall +12.57pp above LWM (56.69% → 69.27%)
  + xls: L3 hostile ensemble recall +2.49pp above LWM (92.44% → 94.93%)
  + xlsx: L3 hostile ensemble recall +4.51pp above LWM (29.01% → 33.53%)
  + xml: L3 hostile ensemble recall +6.06pp above LWM (2.74% → 8.79%)
  + zip: L3 hostile ensemble recall +11.38pp above LWM (40.61% → 51.99%)
  + zst: L3 hostile ensemble recall +1.98pp above LWM (76.60% → 78.58%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - doc: L3 hostile ENSEMBLE recall dropped 17.79pp BELOW LOW-WATER-MARK (90.99% → 73.19%; LWM tolerance 0.90pp)

compared 64 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: low-water-mark gate (0.90pp vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[1]: *** [Makefile:1136: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')
