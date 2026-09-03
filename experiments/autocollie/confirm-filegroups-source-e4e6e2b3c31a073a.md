# Confirm FAIL — e4e6e2b3c31a073a on `filegroups/source`

Cycle `20260825T194359-confirm-e4e6e2b3c31a073a` — 2026-08-25T19:43:59Z

averaged ensemble PR_AUC regressed: 0.9326 -> 0.6710 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `e4e6e2b3c31a073a` | `57f279272b953c2f` | `57f279272b953c2f` | `57f279272b953c2f` |
| PR AUC | 0.9326 | 0.6669 | 0.6552 | 0.6743 |
| ROC AUC | 0.9224 | 0.9337 | 0.9301 | 0.9326 |
| Recall@L50 | — | 0.3548 | 0.3369 | 0.3268 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
