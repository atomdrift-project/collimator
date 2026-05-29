# Confirm PASS — e94b42506416aae8 on `filetypes/docx`

Cycle `20260527T074626-confirm-e94b42506416aae8` — 2026-05-27T07:46:26Z

PR_AUC held across 3 seeds (orig 0.9897)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `e94b42506416aae8` | `595df58c677a5f6f` | `595df58c677a5f6f` | `595df58c677a5f6f` |
| PR AUC | 0.9897 | 0.9898 | 0.9898 | 0.9898 |
| ROC AUC | 0.5000 | 0.5000 | 0.5000 | 0.5000 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=e94b42506416aae8
```
