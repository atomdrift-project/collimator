# Confirm PASS — 8aa942ec129fabae on `filetypes/go`

Cycle `20261106T012546-confirm-8aa942ec129fabae` — 2026-11-06T01:25:46Z

averaged 3-seed ensemble PR_AUC held: 0.9305 -> 0.9415; individual seeds may be noisy

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `8aa942ec129fabae` | `2aa1669fa8474cc1` | `2aa1669fa8474cc1` | `2aa1669fa8474cc1` |
| PR AUC | 0.9305 | 0.9335 | 0.9377 | 0.9375 |
| ROC AUC | 0.9741 | 0.9747 | 0.9788 | 0.9793 |
| Recall@L50 | — | 0.5696 | 0.6400 | 0.5129 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=8aa942ec129fabae
```
