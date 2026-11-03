# Confirm PASS — 5ce32696fa36da2b on `filetypes/c`

Cycle `20261102T221904-confirm-5ce32696fa36da2b` — 2026-11-02T22:19:04Z

averaged 3-seed ensemble PR_AUC held: 0.9434 -> 0.9420; individual seeds may be noisy

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `5ce32696fa36da2b` | `81f0f458ce64414c` | `81f0f458ce64414c` | `81f0f458ce64414c` |
| PR AUC | 0.9434 | 0.9341 | 0.9183 | 0.9428 |
| ROC AUC | 0.9784 | 0.9693 | 0.9606 | 0.9782 |
| Recall@L50 | — | 0.3249 | 0.5489 | 0.5118 |
| verdict | — | FAIL | FAIL | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=5ce32696fa36da2b
```
