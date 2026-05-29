# Confirm PASS — c415afac4cc71022 on `filetypes/powershell`

Cycle `20260527T010930-confirm-c415afac4cc71022` — 2026-05-27T01:09:30Z

PR_AUC held across 3 seeds (orig 0.9987)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `c415afac4cc71022` | `a8c3a6bad5466a5f` | `a8c3a6bad5466a5f` | `a8c3a6bad5466a5f` |
| PR AUC | 0.9987 | 0.9989 | 0.9995 | 0.9987 |
| ROC AUC | 0.9967 | 0.9961 | 0.9982 | 0.9957 |
| Recall@3FPM | — | 0.8433 | 0.9202 | 0.8063 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=c415afac4cc71022
```
