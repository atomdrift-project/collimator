# Confirm PASS — 311f7616d6c8dfe0 on `filetypes/batch`

Cycle `20260705T162524-confirm-311f7616d6c8dfe0` — 2026-07-05T16:25:24Z

PR_AUC held across 3 seeds (orig 0.9890)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `311f7616d6c8dfe0` | `51df3f066420fab1` | `51df3f066420fab1` | `51df3f066420fab1` |
| PR AUC | 0.9890 | 0.9928 | 0.9898 | 0.9924 |
| ROC AUC | 0.9139 | 0.8892 | 0.8442 | 0.8884 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=311f7616d6c8dfe0
```
