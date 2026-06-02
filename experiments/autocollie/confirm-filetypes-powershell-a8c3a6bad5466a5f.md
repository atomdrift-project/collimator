# Confirm PASS — a8c3a6bad5466a5f on `filetypes/powershell`

Cycle `20260602T013212-confirm-a8c3a6bad5466a5f` — 2026-06-02T01:32:12Z

PR_AUC held across 3 seeds (orig 0.9992)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `a8c3a6bad5466a5f` | `bbc88e116167162f` | `bbc88e116167162f` | `bbc88e116167162f` |
| PR AUC | 0.9992 | 0.9993 | 0.9995 | 0.9994 |
| ROC AUC | 0.9970 | 0.9963 | 0.9976 | 0.9971 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=a8c3a6bad5466a5f
```
