# Confirm PASS — 7d7232faa905d0fb on `general`

Cycle `20260524T171807-confirm-7d7232faa905d0fb` — 2026-05-24T17:18:07Z

PR_AUC held across 3 seeds (orig 0.9987)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `7d7232faa905d0fb` | `e54dc37669382441` | `e54dc37669382441` | `e54dc37669382441` |
| PR AUC | 0.9987 | 0.9999 | 0.9999 | 0.9999 |
| ROC AUC | 0.9987 | 0.9996 | 0.9996 | 0.9996 |
| Recall@3FPM | — | 0.6170 | 0.6529 | 0.5912 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=7d7232faa905d0fb
```
