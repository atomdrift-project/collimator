# Confirm PASS — 41ea6a671694d8b9 on `filetypes/java_class`

Cycle `20260718T152029-confirm-41ea6a671694d8b9` — 2026-07-18T15:20:29Z

PR_AUC held across 3 seeds (orig 0.9863)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `41ea6a671694d8b9` | `ef77fc8d32097b8c` | `ef77fc8d32097b8c` | `ef77fc8d32097b8c` |
| PR AUC | 0.9863 | 0.9898 | 0.9903 | 0.9853 |
| ROC AUC | 0.9979 | 0.9984 | 0.9985 | 0.9978 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=41ea6a671694d8b9
```
