# Confirm PASS — afd2a3a5ce658ba8 on `filetypes/batch`

Cycle `20260628T103338-confirm-afd2a3a5ce658ba8` — 2026-06-28T10:33:38Z

PR_AUC held across 3 seeds (orig 0.9999)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `afd2a3a5ce658ba8` | `85d99936d6bc0aba` | `85d99936d6bc0aba` | `85d99936d6bc0aba` |
| PR AUC | 0.9999 | 0.9999 | 0.9999 | 0.9999 |
| ROC AUC | 0.9981 | 0.9978 | 0.9980 | 0.9981 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=afd2a3a5ce658ba8
```
