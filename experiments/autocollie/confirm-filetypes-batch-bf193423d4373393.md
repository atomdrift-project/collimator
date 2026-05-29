# Confirm PASS — bf193423d4373393 on `filetypes/batch`

Cycle `20260526T222948-confirm-bf193423d4373393` — 2026-05-26T22:29:48Z

PR_AUC held across 3 seeds (orig 0.9998)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `bf193423d4373393` | `0f2f5fd66767d23a` | `0f2f5fd66767d23a` | `0f2f5fd66767d23a` |
| PR AUC | 0.9998 | 0.9996 | 0.9996 | 0.9995 |
| ROC AUC | 0.9982 | 0.9964 | 0.9962 | 0.9958 |
| Recall@3FPM | — | 0.9791 | 0.9713 | 0.9791 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=bf193423d4373393
```
