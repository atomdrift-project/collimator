# Promote REJECTED — `becf26ff52bff163` on `filetypes/zip`

Generated 2026-05-28T12:16:19Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-28T12-09-05_20260528T120901-promote-becf26ff52bff163_azoth-validate.log; tail: ensemble improvements (≥0.10pp):
  c: L3 hostile ensemble recall +0.85pp (11.43% → 12.28%)
  elf: L3 hostile ensemble recall +0.33pp (93.13% → 93.45%)
  go: L3 hostile ensemble recall +3.06pp (1.70% → 4.76%)
  javascript: L3 hostile ensemble recall +12.96pp (63.31% → 76.28%)
  shell: L3 hostile ensemble recall +13.26pp (69.73% → 82.99%)

per-route improvements (≥0.10pp, informational):
  c :: filetypes/c recall@3FP/M +2.04pp (11.94% → 13.98%)
  elf :: filetypes/elf recall@3FP/M +2.67pp (93.35% → 96.01%)
  go :: filetypes/go recall@3FP/M +2.29pp (4.84% → 7.14%)
  javascript :: filetypes/javascript recall@3FP/M +8.46pp (69.53% → 77.99%)
  shell :: filetypes/shell recall@3FP/M +32.15pp (55.01% → 87.16%)

24 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + 7z: L3 hostile ensemble recall +14.84pp above LWM (72.74% → 87.59%)
  + c: L3 hostile ensemble recall +2.26pp above LWM (10.02% → 12.28%)
  + cab: L3 hostile ensemble recall +46.55pp above LWM (3.45% → 50.00%)
  + chrome-manifest: L3 hostile ensemble recall +16.67pp above LWM (50.00% → 66.67%)
  + crx: L3 hostile ensemble recall +10.81pp above LWM (0.00% → 10.81%)
  + docx: L3 hostile ensemble recall +1.09pp above LWM (71.59% → 72.68%)
  + go: L3 hostile ensemble recall +3.40pp above LWM (1.36% → 4.76%)
  + html: L3 hostile ensemble recall +83.33pp above LWM (16.67% → 100.00%)
  + javascript: L3 hostile ensemble recall +10.08pp above LWM (66.20% → 76.28%)
  + jpeg: L3 hostile ensemble recall +9.12pp above LWM (1.56% → 10.69%)
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
  + zip: L3 hostile ensemble recall +5.61pp above LWM (40.61% → 46.23%)
  + zst: L3 hostile ensemble recall +1.98pp above LWM (76.60% → 78.58%)

1 DEPLOYED-TOLERANCE regression(s) (vs currently-deployed bundle /home/t/.local/share/litmus/models/azoth) — THIS IS WHAT BLOCKS THE DEPLOY:
  - zip: L3 hostile ENSEMBLE recall dropped 5.76pp (51.99% → 46.23%; tolerance 1.70pp; deployed 95% CI lower = 50.86%)

compared 64 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: deployed-tolerance gate (1 filetype(s) regressed vs deployed beyond the 1.70pp tolerance; see list above for the actual drops)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[1]: *** [Makefile:1136: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9997)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `becf26ff52bff163` | `3b2acb4890542414` | `ce4bfe4cd1e58e98` |
| PR AUC | 0.9997 | 0.9997 | 0.9997 |
| ROC AUC | 0.9957 | 0.9960 | 0.9962 |
| F1 | 0.0000 | 0.8136 | 0.8076 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-28T12-09-05_20260528T120901-promote-becf26ff52bff163_azoth-validate.log; tail: ensemble improvements (≥0.10pp):
  c: L3 hostile ensemble recall +0.85pp (11.43% → 12.28%)
  elf: L3 hostile ensemble recall +0.33pp (93.13% → 93.45%)
  go: L3 hostile ensemble recall +3.06pp (1.70% → 4.76%)
  javascript: L3 hostile ensemble recall +12.96pp (63.31% → 76.28%)
  shell: L3 hostile ensemble recall +13.26pp (69.73% → 82.99%)

per-route improvements (≥0.10pp, informational):
  c :: filetypes/c recall@3FP/M +2.04pp (11.94% → 13.98%)
  elf :: filetypes/elf recall@3FP/M +2.67pp (93.35% → 96.01%)
  go :: filetypes/go recall@3FP/M +2.29pp (4.84% → 7.14%)
  javascript :: filetypes/javascript recall@3FP/M +8.46pp (69.53% → 77.99%)
  shell :: filetypes/shell recall@3FP/M +32.15pp (55.01% → 87.16%)

24 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + 7z: L3 hostile ensemble recall +14.84pp above LWM (72.74% → 87.59%)
  + c: L3 hostile ensemble recall +2.26pp above LWM (10.02% → 12.28%)
  + cab: L3 hostile ensemble recall +46.55pp above LWM (3.45% → 50.00%)
  + chrome-manifest: L3 hostile ensemble recall +16.67pp above LWM (50.00% → 66.67%)
  + crx: L3 hostile ensemble recall +10.81pp above LWM (0.00% → 10.81%)
  + docx: L3 hostile ensemble recall +1.09pp above LWM (71.59% → 72.68%)
  + go: L3 hostile ensemble recall +3.40pp above LWM (1.36% → 4.76%)
  + html: L3 hostile ensemble recall +83.33pp above LWM (16.67% → 100.00%)
  + javascript: L3 hostile ensemble recall +10.08pp above LWM (66.20% → 76.28%)
  + jpeg: L3 hostile ensemble recall +9.12pp above LWM (1.56% → 10.69%)
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
  + zip: L3 hostile ensemble recall +5.61pp above LWM (40.61% → 46.23%)
  + zst: L3 hostile ensemble recall +1.98pp above LWM (76.60% → 78.58%)

1 DEPLOYED-TOLERANCE regression(s) (vs currently-deployed bundle /home/t/.local/share/litmus/models/azoth) — THIS IS WHAT BLOCKS THE DEPLOY:
  - zip: L3 hostile ENSEMBLE recall dropped 5.76pp (51.99% → 46.23%; tolerance 1.70pp; deployed 95% CI lower = 50.86%)

compared 64 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: deployed-tolerance gate (1 filetype(s) regressed vs deployed beyond the 1.70pp tolerance; see list above for the actual drops)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[1]: *** [Makefile:1136: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')
