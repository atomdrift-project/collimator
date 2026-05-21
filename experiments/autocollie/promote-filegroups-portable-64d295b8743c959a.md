# Promote REJECTED — `64d295b8743c959a` on `filegroups/portable`

Generated 2026-05-20T18:48:18Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-20T18-43-57_20260520T184342-promote-64d295b8743c959a_azoth-validate.log; tail: azoth bundle ok: /tmp/tmp.lUYpIais5h

ensemble improvements (≥0.10pp):
  kotlin: L3 hostile ensemble recall +6.85pp (50.59% → 57.44%)
  php: L3 hostile ensemble recall +3.91pp (51.27% → 55.19%)
  tar.gz: L3 hostile ensemble recall +4.06pp (58.52% → 62.58%)
  zip: L3 hostile ensemble recall +4.31pp (45.25% → 49.56%)
  zst: L3 hostile ensemble recall +7.55pp (79.95% → 87.50%)

per-route improvements (≥0.10pp, informational):
  c :: filetypes/c recall@3FP/M +0.62pp (12.74% → 13.36%)
  elf :: general recall@3FP/M +0.11pp (89.05% → 89.16%)
  elf :: filetypes/elf recall@3FP/M +2.15pp (94.45% → 96.60%)
  go :: general recall@3FP/M +0.17pp (2.04% → 2.21%)
  go :: filetypes/go recall@3FP/M +0.25pp (4.76% → 5.01%)
  javascript :: general recall@3FP/M +1.57pp (72.29% → 73.85%)
  javascript :: filegroups/scripts recall@3FP/M +8.71pp (64.40% → 73.11%)
  pdf :: general recall@3FP/M +0.51pp (6.56% → 7.06%)
  php :: general recall@3FP/M +0.20pp (66.54% → 66.73%)
  php :: filegroups/scripts recall@3FP/M +0.78pp (65.36% → 66.14%)
  python :: general recall@3FP/M +0.53pp (60.18% → 60.71%)
  python :: filegroups/scripts recall@3FP/M +34.40pp (27.94% → 62.34%)
  shell :: filegroups/scripts recall@3FP/M +9.56pp (69.49% → 79.04%)
  unknown :: general recall@3FP/M +6.01pp (29.08% → 35.09%)

per-route regressions (informational; does not block deploy):
  c :: general recall@3FP/M dropped 1.13pp (9.85% → 8.72%)
  elf :: filegroups/native recall@3FP/M dropped 6.96pp (95.97% → 89.00%)
  javascript :: filetypes/javascript recall@3FP/M dropped 1.83pp (73.85% → 72.02%)
  kotlin :: filegroups/source recall@3FP/M dropped 1.75pp (69.20% → 67.45%)
  kotlin :: filetypes/kotlin recall@3FP/M dropped 2.19pp (65.56% → 63.37%)
  pe :: general recall@3FP/M dropped 2.19pp (72.82% → 70.63%)
  pe :: filegroups/native recall@3FP/M dropped 27.40pp (83.75% → 56.35%)
  pe :: filetypes/pe recall@3FP/M dropped 6.39pp (62.87% → 56.48%)
  php :: filetypes/php recall@3FP/M dropped 3.52pp (72.21% → 68.69%)
  shell :: general recall@3FP/M dropped 1.59pp (78.19% → 76.59%)
  tar.gz :: general recall@3FP/M dropped 2.30pp (83.95% → 81.65%)

error: 5 ensemble regression(s) over tolerance:
  - c: L3 hostile ENSEMBLE recall dropped 1.36pp (5.49% → 4.13%; tolerance 1.00pp)
  - javascript: L3 hostile ENSEMBLE recall dropped 3.03pp (64.61% → 61.58%; tolerance 1.00pp)
  - pe: L3 hostile ENSEMBLE recall dropped 7.71pp (69.97% → 62.25%; tolerance 1.00pp)
  - png: L3 hostile ENSEMBLE recall dropped 6.09pp (6.24% → 0.15%; tolerance 1.00pp)
  - python: L3 hostile ENSEMBLE recall dropped 8.27pp (56.40% → 48.13%; tolerance 1.00pp)

compared 16 filetypes (mal≥500, ben≥500); 49 below threshold and skipped.

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run.
make[1]: *** [Makefile:1077: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9967)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `64d295b8743c959a` | `36faffff0426af0e` | `2da43de64e855a82` |
| PR AUC | 0.9967 | 0.9966 | 0.9967 |
| ROC AUC | 0.9992 | 0.9992 | 0.9992 |
| F1 | 0.9740 | 0.9740 | 0.9740 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-20T18-43-57_20260520T184342-promote-64d295b8743c959a_azoth-validate.log; tail: azoth bundle ok: /tmp/tmp.lUYpIais5h

ensemble improvements (≥0.10pp):
  kotlin: L3 hostile ensemble recall +6.85pp (50.59% → 57.44%)
  php: L3 hostile ensemble recall +3.91pp (51.27% → 55.19%)
  tar.gz: L3 hostile ensemble recall +4.06pp (58.52% → 62.58%)
  zip: L3 hostile ensemble recall +4.31pp (45.25% → 49.56%)
  zst: L3 hostile ensemble recall +7.55pp (79.95% → 87.50%)

per-route improvements (≥0.10pp, informational):
  c :: filetypes/c recall@3FP/M +0.62pp (12.74% → 13.36%)
  elf :: general recall@3FP/M +0.11pp (89.05% → 89.16%)
  elf :: filetypes/elf recall@3FP/M +2.15pp (94.45% → 96.60%)
  go :: general recall@3FP/M +0.17pp (2.04% → 2.21%)
  go :: filetypes/go recall@3FP/M +0.25pp (4.76% → 5.01%)
  javascript :: general recall@3FP/M +1.57pp (72.29% → 73.85%)
  javascript :: filegroups/scripts recall@3FP/M +8.71pp (64.40% → 73.11%)
  pdf :: general recall@3FP/M +0.51pp (6.56% → 7.06%)
  php :: general recall@3FP/M +0.20pp (66.54% → 66.73%)
  php :: filegroups/scripts recall@3FP/M +0.78pp (65.36% → 66.14%)
  python :: general recall@3FP/M +0.53pp (60.18% → 60.71%)
  python :: filegroups/scripts recall@3FP/M +34.40pp (27.94% → 62.34%)
  shell :: filegroups/scripts recall@3FP/M +9.56pp (69.49% → 79.04%)
  unknown :: general recall@3FP/M +6.01pp (29.08% → 35.09%)

per-route regressions (informational; does not block deploy):
  c :: general recall@3FP/M dropped 1.13pp (9.85% → 8.72%)
  elf :: filegroups/native recall@3FP/M dropped 6.96pp (95.97% → 89.00%)
  javascript :: filetypes/javascript recall@3FP/M dropped 1.83pp (73.85% → 72.02%)
  kotlin :: filegroups/source recall@3FP/M dropped 1.75pp (69.20% → 67.45%)
  kotlin :: filetypes/kotlin recall@3FP/M dropped 2.19pp (65.56% → 63.37%)
  pe :: general recall@3FP/M dropped 2.19pp (72.82% → 70.63%)
  pe :: filegroups/native recall@3FP/M dropped 27.40pp (83.75% → 56.35%)
  pe :: filetypes/pe recall@3FP/M dropped 6.39pp (62.87% → 56.48%)
  php :: filetypes/php recall@3FP/M dropped 3.52pp (72.21% → 68.69%)
  shell :: general recall@3FP/M dropped 1.59pp (78.19% → 76.59%)
  tar.gz :: general recall@3FP/M dropped 2.30pp (83.95% → 81.65%)

error: 5 ensemble regression(s) over tolerance:
  - c: L3 hostile ENSEMBLE recall dropped 1.36pp (5.49% → 4.13%; tolerance 1.00pp)
  - javascript: L3 hostile ENSEMBLE recall dropped 3.03pp (64.61% → 61.58%; tolerance 1.00pp)
  - pe: L3 hostile ENSEMBLE recall dropped 7.71pp (69.97% → 62.25%; tolerance 1.00pp)
  - png: L3 hostile ENSEMBLE recall dropped 6.09pp (6.24% → 0.15%; tolerance 1.00pp)
  - python: L3 hostile ENSEMBLE recall dropped 8.27pp (56.40% → 48.13%; tolerance 1.00pp)

compared 16 filetypes (mal≥500, ben≥500); 49 below threshold and skipped.

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run.
make[1]: *** [Makefile:1077: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')
