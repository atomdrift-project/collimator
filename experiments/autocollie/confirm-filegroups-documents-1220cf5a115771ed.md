# Confirm PASS — 1220cf5a115771ed on `filegroups/documents`

Cycle `20260601T134037-confirm-1220cf5a115771ed` — 2026-06-01T13:40:37Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `1220cf5a115771ed` | `adee597e6826de40` | `adee597e6826de40` | `adee597e6826de40` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9998 | 0.9992 | 0.9992 | 0.9992 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=1220cf5a115771ed
```
