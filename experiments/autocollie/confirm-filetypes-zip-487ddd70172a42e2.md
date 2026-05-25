# Confirm PASS — 487ddd70172a42e2 on `filetypes/zip`

Cycle `20260524T063841-confirm-487ddd70172a42e2` — 2026-05-24T06:38:41Z

PR_AUC held across 3 seeds (orig 0.9998)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `487ddd70172a42e2` | `5367018484ed47d0` | `5367018484ed47d0` | `5367018484ed47d0` |
| PR AUC | 0.9998 | 0.9998 | 0.9998 | 0.9998 |
| ROC AUC | 0.9966 | 0.9963 | 0.9962 | 0.9961 |
| Recall@3FPM | — | 0.6578 | 0.6905 | 0.7214 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=487ddd70172a42e2
```
