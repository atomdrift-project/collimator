# Confirm PASS — 971e248095c9a1b2 on `filetypes/pe`

Cycle `20260715T135344-confirm-971e248095c9a1b2` — 2026-07-15T13:53:44Z

PR_AUC held across 3 seeds (orig 0.9990)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `971e248095c9a1b2` | `48eb0bb729de7c0f` | `48eb0bb729de7c0f` | `48eb0bb729de7c0f` |
| PR AUC | 0.9990 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9990 | 0.9997 | 0.9998 | 0.9998 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=971e248095c9a1b2
```
