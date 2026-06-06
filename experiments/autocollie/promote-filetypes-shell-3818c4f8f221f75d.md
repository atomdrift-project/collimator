# Promote REJECTED — `3818c4f8f221f75d` on `filetypes/shell`

Generated 2026-06-06T13:44:56Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-06T13-41-44_20260606T134124-promote-3818c4f8f221f75d_azoth-validate.log; tail:   shell :: filetypes/shell recall@1FP-on-slice +0.14pp (84.10% → 84.24%)

per-route regressions (informational; does not block deploy):
  shell :: general recall@1FP-on-slice dropped 28.10pp (74.79% → 46.69%)

34 pre-existing drift(s) on unimpacted filetypes (informational — not caused by this promote, see --source-bundle impact analysis):
  ~ 7z: pre-existing drift, recall 16.24% → 12.63% (+3.61pp; unimpacted by this promote)
  ~ batch: pre-existing drift, recall 97.46% → 1.24% (+96.23pp; unimpacted by this promote)
  ~ c: pre-existing drift, recall 3.93% → 6.30% (+2.37pp; unimpacted by this promote)
  ~ chrome-manifest: pre-existing drift, recall 28.57% → 42.86% (+14.29pp; unimpacted by this promote)
  ~ doc: pre-existing drift, recall 38.51% → 66.38% (+27.87pp; unimpacted by this promote)
  ~ docx: pre-existing drift, recall 82.92% → 44.66% (+38.26pp; unimpacted by this promote)
  ~ elf: pre-existing drift, recall 95.93% → 98.61% (+2.68pp; unimpacted by this promote)
  ~ go: pre-existing drift, recall 2.20% → 6.06% (+3.86pp; unimpacted by this promote)
  ~ jar: pre-existing drift, recall 70.65% → 85.39% (+14.74pp; unimpacted by this promote)
  ~ java_class: pre-existing drift, recall 17.65% → 23.08% (+5.43pp; unimpacted by this promote)
  ~ javascript: pre-existing drift, recall 59.50% → 71.30% (+11.80pp; unimpacted by this promote)
  ~ jpeg: pre-existing drift, recall 10.60% → 13.25% (+2.65pp; unimpacted by this promote)
  ~ kotlin: pre-existing drift, recall 51.39% → 52.99% (+1.60pp; unimpacted by this promote)
  ~ lnk: pre-existing drift, recall 82.68% → 66.73% (+15.95pp; unimpacted by this promote)
  ~ lua: pre-existing drift, recall 30.77% → 53.85% (+23.08pp; unimpacted by this promote)
  ~ macho: pre-existing drift, recall 80.24% → 68.26% (+11.98pp; unimpacted by this promote)
  ~ msi: pre-existing drift, recall 0.00% → 58.05% (+58.05pp; unimpacted by this promote)
  ~ ole: pre-existing drift, recall 82.17% → 50.88% (+31.29pp; unimpacted by this promote)
  ~ pdf: pre-existing drift, recall 6.50% → 4.25% (+2.25pp; unimpacted by this promote)
  ~ pe: pre-existing drift, recall 51.78% → 56.91% (+5.12pp; unimpacted by this promote)
  ~ perl: pre-existing drift, recall 69.44% → 83.33% (+13.89pp; unimpacted by this promote)
  ~ pkg-info: pre-existing drift, recall 87.00% → 65.47% (+21.53pp; unimpacted by this promote)
  ~ png: pre-existing drift, recall 0.00% → 7.27% (+7.27pp; unimpacted by this promote)
  ~ powershell: pre-existing drift, recall 52.76% → 43.71% (+9.05pp; unimpacted by this promote)
  ~ pptx: pre-existing drift, recall 22.22% → 1.39% (+20.83pp; unimpacted by this promote)
  ~ python: pre-existing drift, recall 48.01% → 48.19% (+0.18pp; unimpacted by this promote)
  ~ python-bytecode: pre-existing drift, recall 92.09% → 88.14% (+3.95pp; unimpacted by this promote)
  ~ tar: pre-existing drift, recall 88.19% → 81.54% (+6.65pp; unimpacted by this promote)
  ~ vbs: pre-existing drift, recall 42.72% → 47.69% (+4.97pp; unimpacted by this promote)
  ~ xls: pre-existing drift, recall 93.19% → 90.97% (+2.22pp; unimpacted by this promote)
  ~ xlsx: pre-existing drift, recall 36.08% → 29.09% (+6.99pp; unimpacted by this promote)
  ~ xml: pre-existing drift, recall 2.55% → 13.23% (+10.68pp; unimpacted by this promote)
  ~ zip: pre-existing drift, recall 31.45% → 31.98% (+0.53pp; unimpacted by this promote)
  ~ zst: pre-existing drift, recall 6.39% → 8.26% (+1.87pp; unimpacted by this promote)

1 DEPLOYED-TOLERANCE regression(s) (vs currently-deployed bundle /home/t/.local/share/litmus/models/azoth) — THIS IS WHAT BLOCKS THE DEPLOY:
  - shell: L50 hostile ENSEMBLE recall dropped 1.99pp (81.64% → 79.65%; tolerance 1.70pp; deployed 95% CI lower = 79.81%)

compared 75 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: deployed-tolerance gate (1 filetype(s) regressed vs deployed beyond the 1.70pp tolerance; see list above for the actual drops)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1297: azoth-validate] Error 1)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9963)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `3818c4f8f221f75d` | `43e964486f908713` | `a1dec9071922fcdc` |
| PR AUC | 0.9963 | 0.9987 | 0.9987 |
| ROC AUC | 0.9976 | 0.9988 | 0.9987 |
| F1 | 0.9650 | 0.9812 | 0.9777 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-06T13-41-44_20260606T134124-promote-3818c4f8f221f75d_azoth-validate.log; tail:   shell :: filetypes/shell recall@1FP-on-slice +0.14pp (84.10% → 84.24%)

per-route regressions (informational; does not block deploy):
  shell :: general recall@1FP-on-slice dropped 28.10pp (74.79% → 46.69%)

34 pre-existing drift(s) on unimpacted filetypes (informational — not caused by this promote, see --source-bundle impact analysis):
  ~ 7z: pre-existing drift, recall 16.24% → 12.63% (+3.61pp; unimpacted by this promote)
  ~ batch: pre-existing drift, recall 97.46% → 1.24% (+96.23pp; unimpacted by this promote)
  ~ c: pre-existing drift, recall 3.93% → 6.30% (+2.37pp; unimpacted by this promote)
  ~ chrome-manifest: pre-existing drift, recall 28.57% → 42.86% (+14.29pp; unimpacted by this promote)
  ~ doc: pre-existing drift, recall 38.51% → 66.38% (+27.87pp; unimpacted by this promote)
  ~ docx: pre-existing drift, recall 82.92% → 44.66% (+38.26pp; unimpacted by this promote)
  ~ elf: pre-existing drift, recall 95.93% → 98.61% (+2.68pp; unimpacted by this promote)
  ~ go: pre-existing drift, recall 2.20% → 6.06% (+3.86pp; unimpacted by this promote)
  ~ jar: pre-existing drift, recall 70.65% → 85.39% (+14.74pp; unimpacted by this promote)
  ~ java_class: pre-existing drift, recall 17.65% → 23.08% (+5.43pp; unimpacted by this promote)
  ~ javascript: pre-existing drift, recall 59.50% → 71.30% (+11.80pp; unimpacted by this promote)
  ~ jpeg: pre-existing drift, recall 10.60% → 13.25% (+2.65pp; unimpacted by this promote)
  ~ kotlin: pre-existing drift, recall 51.39% → 52.99% (+1.60pp; unimpacted by this promote)
  ~ lnk: pre-existing drift, recall 82.68% → 66.73% (+15.95pp; unimpacted by this promote)
  ~ lua: pre-existing drift, recall 30.77% → 53.85% (+23.08pp; unimpacted by this promote)
  ~ macho: pre-existing drift, recall 80.24% → 68.26% (+11.98pp; unimpacted by this promote)
  ~ msi: pre-existing drift, recall 0.00% → 58.05% (+58.05pp; unimpacted by this promote)
  ~ ole: pre-existing drift, recall 82.17% → 50.88% (+31.29pp; unimpacted by this promote)
  ~ pdf: pre-existing drift, recall 6.50% → 4.25% (+2.25pp; unimpacted by this promote)
  ~ pe: pre-existing drift, recall 51.78% → 56.91% (+5.12pp; unimpacted by this promote)
  ~ perl: pre-existing drift, recall 69.44% → 83.33% (+13.89pp; unimpacted by this promote)
  ~ pkg-info: pre-existing drift, recall 87.00% → 65.47% (+21.53pp; unimpacted by this promote)
  ~ png: pre-existing drift, recall 0.00% → 7.27% (+7.27pp; unimpacted by this promote)
  ~ powershell: pre-existing drift, recall 52.76% → 43.71% (+9.05pp; unimpacted by this promote)
  ~ pptx: pre-existing drift, recall 22.22% → 1.39% (+20.83pp; unimpacted by this promote)
  ~ python: pre-existing drift, recall 48.01% → 48.19% (+0.18pp; unimpacted by this promote)
  ~ python-bytecode: pre-existing drift, recall 92.09% → 88.14% (+3.95pp; unimpacted by this promote)
  ~ tar: pre-existing drift, recall 88.19% → 81.54% (+6.65pp; unimpacted by this promote)
  ~ vbs: pre-existing drift, recall 42.72% → 47.69% (+4.97pp; unimpacted by this promote)
  ~ xls: pre-existing drift, recall 93.19% → 90.97% (+2.22pp; unimpacted by this promote)
  ~ xlsx: pre-existing drift, recall 36.08% → 29.09% (+6.99pp; unimpacted by this promote)
  ~ xml: pre-existing drift, recall 2.55% → 13.23% (+10.68pp; unimpacted by this promote)
  ~ zip: pre-existing drift, recall 31.45% → 31.98% (+0.53pp; unimpacted by this promote)
  ~ zst: pre-existing drift, recall 6.39% → 8.26% (+1.87pp; unimpacted by this promote)

1 DEPLOYED-TOLERANCE regression(s) (vs currently-deployed bundle /home/t/.local/share/litmus/models/azoth) — THIS IS WHAT BLOCKS THE DEPLOY:
  - shell: L50 hostile ENSEMBLE recall dropped 1.99pp (81.64% → 79.65%; tolerance 1.70pp; deployed 95% CI lower = 79.81%)

compared 75 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: deployed-tolerance gate (1 filetype(s) regressed vs deployed beyond the 1.70pp tolerance; see list above for the actual drops)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1297: azoth-validate] Error 1)
