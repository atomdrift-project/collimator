# Confirm PASS — 9759d4ac7c443d40 on `filetypes/lnk`

Cycle `20260607T205035-confirm-9759d4ac7c443d40` — 2026-06-07T20:50:35Z

PR_AUC held across 3 seeds (orig 0.9957)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `9759d4ac7c443d40` | `163cee0b3d17d258` | `163cee0b3d17d258` | `163cee0b3d17d258` |
| PR AUC | 0.9957 | 0.9959 | 0.9967 | 0.9960 |
| ROC AUC | 0.9808 | 0.9820 | 0.9844 | 0.9820 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=9759d4ac7c443d40
```
