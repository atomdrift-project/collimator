# Confirm PASS — a5215de4aee3d9d4 on `filetypes/shell`

Cycle `20260527T010407-confirm-a5215de4aee3d9d4` — 2026-05-27T01:04:07Z

PR_AUC held across 3 seeds (orig 0.9986)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `a5215de4aee3d9d4` | `0e418aa7e6d885e1` | `0e418aa7e6d885e1` | `0e418aa7e6d885e1` |
| PR AUC | 0.9986 | 0.9969 | 0.9970 | 0.9970 |
| ROC AUC | 0.9996 | 0.9979 | 0.9979 | 0.9979 |
| Recall@3FPM | — | 0.8734 | 0.8305 | 0.8455 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=a5215de4aee3d9d4
```
