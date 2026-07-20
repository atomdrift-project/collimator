# Confirm PASS — f39dd406bc3c00d1 on `filetypes/elf`

Cycle `20260716T011508-confirm-f39dd406bc3c00d1` — 2026-07-16T01:15:08Z

PR_AUC held across 3 seeds (orig 0.9999)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `f39dd406bc3c00d1` | `22d08e28556d6ae8` | `22d08e28556d6ae8` | `22d08e28556d6ae8` |
| PR AUC | 0.9999 | 0.9999 | 0.9999 | 0.9999 |
| ROC AUC | 0.9998 | 0.9999 | 0.9999 | 0.9999 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=f39dd406bc3c00d1
```
