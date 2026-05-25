# Confirm PASS — 388062cdae015a34 on `filetypes/tar.gz`

Cycle `20260524T082839-confirm-388062cdae015a34` — 2026-05-24T08:28:39Z

PR_AUC held across 3 seeds (orig 0.9994)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `388062cdae015a34` | `d251dec3e738261e` | `d251dec3e738261e` | `d251dec3e738261e` |
| PR AUC | 0.9994 | 0.9994 | 0.9994 | 0.9994 |
| ROC AUC | 0.9987 | 0.9988 | 0.9987 | 0.9987 |
| Recall@3FPM | — | 0.7003 | 0.7252 | 0.6857 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=388062cdae015a34
```
