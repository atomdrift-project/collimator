# Confirm PASS — 4546ad7cbfb4ff7b on `filetypes/chrome_manifest`

Cycle `20261030T231954-confirm-4546ad7cbfb4ff7b` — 2026-10-30T23:19:54Z

averaged 3-seed ensemble PR_AUC held: 0.9390 -> 0.9390; individual seeds may be noisy

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `4546ad7cbfb4ff7b` | `a0b4d0f7bc0dfc66` | `a0b4d0f7bc0dfc66` | `a0b4d0f7bc0dfc66` |
| PR AUC | 0.9390 | 0.9514 | 0.9293 | 0.9242 |
| ROC AUC | 0.9933 | 0.9942 | 0.9933 | 0.9933 |
| Recall@L50 | — | 0.8889 | 0.6667 | 0.6667 |
| verdict | — | PASS | FAIL | FAIL |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=4546ad7cbfb4ff7b
```
