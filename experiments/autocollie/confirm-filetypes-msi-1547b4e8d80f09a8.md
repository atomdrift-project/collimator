# Confirm PASS — 1547b4e8d80f09a8 on `filetypes/msi`

Cycle `20260525T202328-confirm-1547b4e8d80f09a8` — 2026-05-25T20:23:28Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `1547b4e8d80f09a8` | `d359ca514f554c0a` | `d359ca514f554c0a` | `d359ca514f554c0a` |
| PR AUC | 1.0000 | 0.9999 | 0.9998 | 0.9999 |
| ROC AUC | 1.0000 | 0.9973 | 0.9933 | 0.9970 |
| Recall@3FPM | — | 0.9900 | 0.9800 | 0.9900 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=1547b4e8d80f09a8
```
