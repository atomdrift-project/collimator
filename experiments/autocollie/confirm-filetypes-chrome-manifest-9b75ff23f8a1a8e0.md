# Confirm PASS — 9b75ff23f8a1a8e0 on `filetypes/chrome-manifest`

Cycle `20260525T212100-confirm-9b75ff23f8a1a8e0` — 2026-05-25T21:21:00Z

PR_AUC held across 3 seeds (orig 0.8769)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `9b75ff23f8a1a8e0` | `961709eb00d4087c` | `961709eb00d4087c` | `961709eb00d4087c` |
| PR AUC | 0.8769 | 0.5388 | 0.8714 | 0.8600 |
| ROC AUC | 0.9590 | 0.8872 | 0.9538 | 0.9692 |
| Recall@3FPM | — | 0.0000 | 0.8000 | 0.6000 |
| verdict | — | FAIL | FAIL | FAIL |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=9b75ff23f8a1a8e0
```
