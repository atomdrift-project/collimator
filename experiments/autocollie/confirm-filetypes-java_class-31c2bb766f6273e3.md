# Confirm PASS — 31c2bb766f6273e3 on `filetypes/java_class`

Cycle `20260613T012926-confirm-31c2bb766f6273e3` — 2026-06-13T01:29:26Z

PR_AUC held across 3 seeds (orig 0.9890)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `31c2bb766f6273e3` | `e54203c906ab21b9` | `e54203c906ab21b9` | `e54203c906ab21b9` |
| PR AUC | 0.9890 | 0.9871 | 0.9860 | 0.9882 |
| ROC AUC | 0.9981 | 0.9978 | 0.9975 | 0.9980 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=31c2bb766f6273e3
```
