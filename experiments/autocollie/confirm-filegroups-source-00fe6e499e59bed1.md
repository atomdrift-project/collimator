# Confirm PASS — 00fe6e499e59bed1 on `filegroups/source`

Cycle `20260713T023106-confirm-00fe6e499e59bed1` — 2026-07-13T02:31:06Z

PR_AUC held across 3 seeds (orig 0.9931)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `00fe6e499e59bed1` | `481d4debf05d5d20` | `481d4debf05d5d20` | `481d4debf05d5d20` |
| PR AUC | 0.9931 | 0.9949 | 0.9947 | 0.9946 |
| ROC AUC | 0.9953 | 0.9965 | 0.9962 | 0.9962 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=00fe6e499e59bed1
```
