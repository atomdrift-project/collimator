# Confirm PASS — f632d855f0afef68 on `filetypes/batch`

Cycle `20260607T003823-confirm-f632d855f0afef68` — 2026-06-07T00:38:23Z

PR_AUC held across 3 seeds (orig 0.9998)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `f632d855f0afef68` | `54d08386bb9b6d24` | `54d08386bb9b6d24` | `54d08386bb9b6d24` |
| PR AUC | 0.9998 | 0.9998 | 0.9998 | 0.9998 |
| ROC AUC | 0.9973 | 0.9979 | 0.9977 | 0.9973 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=f632d855f0afef68
```
