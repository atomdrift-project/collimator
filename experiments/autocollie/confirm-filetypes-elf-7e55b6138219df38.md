# Confirm PASS — 7e55b6138219df38 on `filetypes/elf`

Cycle `20260825T001237-confirm-7e55b6138219df38` — 2026-08-25T00:12:37Z

PR_AUC held across 3 seeds (orig 0.9999)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `7e55b6138219df38` | `a1c904f8a3dba1cf` | `a1c904f8a3dba1cf` | `a1c904f8a3dba1cf` |
| PR AUC | 0.9999 | 0.9998 | 0.9998 | 0.9998 |
| ROC AUC | 0.9998 | 0.9999 | 0.9999 | 0.9999 |
| Recall@L50 | — | 0.9736 | 0.9740 | 0.9738 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=7e55b6138219df38
```
