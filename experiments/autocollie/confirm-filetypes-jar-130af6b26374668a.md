# Confirm PASS — 130af6b26374668a on `filetypes/jar`

Cycle `20260713T003014-confirm-130af6b26374668a` — 2026-07-13T00:30:14Z

PR_AUC held across 3 seeds (orig 0.9818)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `130af6b26374668a` | `625c768f971b35cc` | `625c768f971b35cc` | `625c768f971b35cc` |
| PR AUC | 0.9818 | 0.9864 | 0.9842 | 0.9845 |
| ROC AUC | 0.9804 | 0.9849 | 0.9830 | 0.9827 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=130af6b26374668a
```
