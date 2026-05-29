# Confirm PASS — bb09c97043e29784 on `filetypes/html`

Cycle `20260527T070050-confirm-bb09c97043e29784` — 2026-05-27T07:00:50Z

PR_AUC held across 3 seeds (orig 0.6154)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `bb09c97043e29784` | `88612d763ced0e87` | `88612d763ced0e87` | `88612d763ced0e87` |
| PR AUC | 0.6154 | 0.6154 | 0.6154 | 0.6154 |
| ROC AUC | 0.5000 | 0.5000 | 0.5000 | 0.5000 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=bb09c97043e29784
```
