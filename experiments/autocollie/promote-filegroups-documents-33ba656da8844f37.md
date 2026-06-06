# Promote REJECTED — `33ba656da8844f37` on `filegroups/documents`

Generated 2026-06-06T13:35:23Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-06T13-32-14_20260606T133148-promote-33ba656da8844f37_azoth-validate.log; tail: per-route regressions (informational; does not block deploy):
  docx :: filetypes/docx recall@1FP-on-slice dropped 9.07pp (89.15% → 80.07%)
  ole :: general recall@1FP-on-slice dropped 7.06pp (90.64% → 83.59%)
  ole :: filegroups/documents recall@1FP-on-slice dropped 6.31pp (93.68% → 87.37%)
  ole :: filetypes/ole recall@1FP-on-slice dropped 8.83pp (93.05% → 84.22%)
  pptx :: general recall@1FP-on-slice dropped 34.72pp (44.44% → 9.72%)
  pptx :: filegroups/documents recall@1FP-on-slice dropped 5.56pp (44.44% → 38.89%)
  xlsx :: general recall@1FP-on-slice dropped 14.94pp (45.91% → 30.97%)
  xlsx :: filetypes/xlsx recall@1FP-on-slice dropped 13.12pp (44.30% → 31.17%)

29 pre-existing drift(s) on unimpacted filetypes (informational — not caused by this promote, see --source-bundle impact analysis):
  ~ 7z: pre-existing drift, recall 16.24% → 12.63% (+3.61pp; unimpacted by this promote)
  ~ batch: pre-existing drift, recall 97.46% → 1.24% (+96.23pp; unimpacted by this promote)
  ~ c: pre-existing drift, recall 3.93% → 8.53% (+4.60pp; unimpacted by this promote)
  ~ chrome-manifest: pre-existing drift, recall 28.57% → 42.86% (+14.29pp; unimpacted by this promote)
  ~ csharp: pre-existing drift, recall 24.38% → 25.62% (+1.24pp; unimpacted by this promote)
  ~ elf: pre-existing drift, recall 95.93% → 98.61% (+2.68pp; unimpacted by this promote)
  ~ go: pre-existing drift, recall 2.20% → 5.90% (+3.70pp; unimpacted by this promote)
  ~ jar: pre-existing drift, recall 70.65% → 85.39% (+14.74pp; unimpacted by this promote)
  ~ java_class: pre-existing drift, recall 17.65% → 23.08% (+5.43pp; unimpacted by this promote)
  ~ javascript: pre-existing drift, recall 59.50% → 71.30% (+11.80pp; unimpacted by this promote)
  ~ jpeg: pre-existing drift, recall 10.60% → 13.25% (+2.65pp; unimpacted by this promote)
  ~ kotlin: pre-existing drift, recall 51.39% → 46.48% (+4.91pp; unimpacted by this promote)
  ~ lnk: pre-existing drift, recall 82.68% → 66.73% (+15.95pp; unimpacted by this promote)
  ~ lua: pre-existing drift, recall 30.77% → 53.85% (+23.08pp; unimpacted by this promote)
  ~ macho: pre-existing drift, recall 80.24% → 68.26% (+11.98pp; unimpacted by this promote)
  ~ msi: pre-existing drift, recall 0.00% → 58.05% (+58.05pp; unimpacted by this promote)
  ~ pe: pre-existing drift, recall 51.78% → 56.91% (+5.12pp; unimpacted by this promote)
  ~ perl: pre-existing drift, recall 69.44% → 83.33% (+13.89pp; unimpacted by this promote)
  ~ pkg-info: pre-existing drift, recall 87.00% → 65.47% (+21.53pp; unimpacted by this promote)
  ~ png: pre-existing drift, recall 0.00% → 7.27% (+7.27pp; unimpacted by this promote)
  ~ powershell: pre-existing drift, recall 52.76% → 43.71% (+9.05pp; unimpacted by this promote)
  ~ python: pre-existing drift, recall 48.01% → 48.19% (+0.18pp; unimpacted by this promote)
  ~ python-bytecode: pre-existing drift, recall 92.09% → 88.14% (+3.95pp; unimpacted by this promote)
  ~ shell: pre-existing drift, recall 81.64% → 87.71% (+6.08pp; unimpacted by this promote)
  ~ tar: pre-existing drift, recall 88.19% → 81.54% (+6.65pp; unimpacted by this promote)
  ~ vbs: pre-existing drift, recall 42.72% → 47.69% (+4.97pp; unimpacted by this promote)
  ~ xml: pre-existing drift, recall 2.55% → 13.23% (+10.68pp; unimpacted by this promote)
  ~ zip: pre-existing drift, recall 31.45% → 31.98% (+0.53pp; unimpacted by this promote)
  ~ zst: pre-existing drift, recall 6.39% → 8.26% (+1.87pp; unimpacted by this promote)

1 DEPLOYED-TOLERANCE regression(s) (vs currently-deployed bundle /home/t/.local/share/litmus/models/azoth) — THIS IS WHAT BLOCKS THE DEPLOY:
  - xlsx: L50 hostile ENSEMBLE recall dropped 5.50pp (36.08% → 30.58%; tolerance 1.70pp; deployed 95% CI lower = 34.98%)

compared 75 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: deployed-tolerance gate (1 filetype(s) regressed vs deployed beyond the 1.70pp tolerance; see list above for the actual drops)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1291: azoth-validate] Error 1)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 1.0000)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `33ba656da8844f37` | `0b0b8faa06a4d5ce` | `194145bfbc9451a7` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9998 | 0.9992 | 0.9992 |
| F1 | 0.9976 | 0.9973 | 0.9972 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-06T13-32-14_20260606T133148-promote-33ba656da8844f37_azoth-validate.log; tail: per-route regressions (informational; does not block deploy):
  docx :: filetypes/docx recall@1FP-on-slice dropped 9.07pp (89.15% → 80.07%)
  ole :: general recall@1FP-on-slice dropped 7.06pp (90.64% → 83.59%)
  ole :: filegroups/documents recall@1FP-on-slice dropped 6.31pp (93.68% → 87.37%)
  ole :: filetypes/ole recall@1FP-on-slice dropped 8.83pp (93.05% → 84.22%)
  pptx :: general recall@1FP-on-slice dropped 34.72pp (44.44% → 9.72%)
  pptx :: filegroups/documents recall@1FP-on-slice dropped 5.56pp (44.44% → 38.89%)
  xlsx :: general recall@1FP-on-slice dropped 14.94pp (45.91% → 30.97%)
  xlsx :: filetypes/xlsx recall@1FP-on-slice dropped 13.12pp (44.30% → 31.17%)

29 pre-existing drift(s) on unimpacted filetypes (informational — not caused by this promote, see --source-bundle impact analysis):
  ~ 7z: pre-existing drift, recall 16.24% → 12.63% (+3.61pp; unimpacted by this promote)
  ~ batch: pre-existing drift, recall 97.46% → 1.24% (+96.23pp; unimpacted by this promote)
  ~ c: pre-existing drift, recall 3.93% → 8.53% (+4.60pp; unimpacted by this promote)
  ~ chrome-manifest: pre-existing drift, recall 28.57% → 42.86% (+14.29pp; unimpacted by this promote)
  ~ csharp: pre-existing drift, recall 24.38% → 25.62% (+1.24pp; unimpacted by this promote)
  ~ elf: pre-existing drift, recall 95.93% → 98.61% (+2.68pp; unimpacted by this promote)
  ~ go: pre-existing drift, recall 2.20% → 5.90% (+3.70pp; unimpacted by this promote)
  ~ jar: pre-existing drift, recall 70.65% → 85.39% (+14.74pp; unimpacted by this promote)
  ~ java_class: pre-existing drift, recall 17.65% → 23.08% (+5.43pp; unimpacted by this promote)
  ~ javascript: pre-existing drift, recall 59.50% → 71.30% (+11.80pp; unimpacted by this promote)
  ~ jpeg: pre-existing drift, recall 10.60% → 13.25% (+2.65pp; unimpacted by this promote)
  ~ kotlin: pre-existing drift, recall 51.39% → 46.48% (+4.91pp; unimpacted by this promote)
  ~ lnk: pre-existing drift, recall 82.68% → 66.73% (+15.95pp; unimpacted by this promote)
  ~ lua: pre-existing drift, recall 30.77% → 53.85% (+23.08pp; unimpacted by this promote)
  ~ macho: pre-existing drift, recall 80.24% → 68.26% (+11.98pp; unimpacted by this promote)
  ~ msi: pre-existing drift, recall 0.00% → 58.05% (+58.05pp; unimpacted by this promote)
  ~ pe: pre-existing drift, recall 51.78% → 56.91% (+5.12pp; unimpacted by this promote)
  ~ perl: pre-existing drift, recall 69.44% → 83.33% (+13.89pp; unimpacted by this promote)
  ~ pkg-info: pre-existing drift, recall 87.00% → 65.47% (+21.53pp; unimpacted by this promote)
  ~ png: pre-existing drift, recall 0.00% → 7.27% (+7.27pp; unimpacted by this promote)
  ~ powershell: pre-existing drift, recall 52.76% → 43.71% (+9.05pp; unimpacted by this promote)
  ~ python: pre-existing drift, recall 48.01% → 48.19% (+0.18pp; unimpacted by this promote)
  ~ python-bytecode: pre-existing drift, recall 92.09% → 88.14% (+3.95pp; unimpacted by this promote)
  ~ shell: pre-existing drift, recall 81.64% → 87.71% (+6.08pp; unimpacted by this promote)
  ~ tar: pre-existing drift, recall 88.19% → 81.54% (+6.65pp; unimpacted by this promote)
  ~ vbs: pre-existing drift, recall 42.72% → 47.69% (+4.97pp; unimpacted by this promote)
  ~ xml: pre-existing drift, recall 2.55% → 13.23% (+10.68pp; unimpacted by this promote)
  ~ zip: pre-existing drift, recall 31.45% → 31.98% (+0.53pp; unimpacted by this promote)
  ~ zst: pre-existing drift, recall 6.39% → 8.26% (+1.87pp; unimpacted by this promote)

1 DEPLOYED-TOLERANCE regression(s) (vs currently-deployed bundle /home/t/.local/share/litmus/models/azoth) — THIS IS WHAT BLOCKS THE DEPLOY:
  - xlsx: L50 hostile ENSEMBLE recall dropped 5.50pp (36.08% → 30.58%; tolerance 1.70pp; deployed 95% CI lower = 34.98%)

compared 75 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: deployed-tolerance gate (1 filetype(s) regressed vs deployed beyond the 1.70pp tolerance; see list above for the actual drops)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1291: azoth-validate] Error 1)
