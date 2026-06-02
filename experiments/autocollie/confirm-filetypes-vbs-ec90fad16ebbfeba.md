# Confirm PASS — ec90fad16ebbfeba on `filetypes/vbs`

Cycle `20260602T010416-confirm-ec90fad16ebbfeba` — 2026-06-02T01:04:16Z

PR_AUC held across 3 seeds (orig 0.9995)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `ec90fad16ebbfeba` | `e9ffa116806273f9` | `e9ffa116806273f9` | `e9ffa116806273f9` |
| PR AUC | 0.9995 | 0.9975 | 0.9976 | 0.9971 |
| ROC AUC | 0.9993 | 0.9636 | 0.9645 | 0.9557 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=ec90fad16ebbfeba
```
