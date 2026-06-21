# Confirm PASS — 6155efedfb00c7f7 on `filetypes/python`

Cycle `20260618T015600-confirm-6155efedfb00c7f7` — 2026-06-18T01:56:00Z

PR_AUC held across 3 seeds (orig 0.9919)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `6155efedfb00c7f7` | `85d47b41b914ed5d` | `85d47b41b914ed5d` | `85d47b41b914ed5d` |
| PR AUC | 0.9919 | 0.9924 | 0.9926 | 0.9927 |
| ROC AUC | 0.9943 | 0.9944 | 0.9946 | 0.9947 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=6155efedfb00c7f7
```
