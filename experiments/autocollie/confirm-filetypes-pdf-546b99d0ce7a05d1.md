# Confirm PASS — 546b99d0ce7a05d1 on `filetypes/pdf`

Cycle `20260601T125336-confirm-546b99d0ce7a05d1` — 2026-06-01T12:53:36Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `546b99d0ce7a05d1` | `5d7c3313f45c10a9` | `5d7c3313f45c10a9` | `5d7c3313f45c10a9` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9992 | 0.9991 | 0.9990 | 0.9991 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=546b99d0ce7a05d1
```
