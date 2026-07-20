# Confirm PASS — 22d0798161ba6548 on `filegroups/documents`

Cycle `20260718T141129-confirm-22d0798161ba6548` — 2026-07-18T14:11:29Z

PR_AUC held across 3 seeds (orig 0.9999)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `22d0798161ba6548` | `ad722cca511455c3` | `ad722cca511455c3` | `ad722cca511455c3` |
| PR AUC | 0.9999 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9992 | 0.9991 | 0.9991 | 0.9991 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=22d0798161ba6548
```
