# Confirm FAIL — 7266671733664807 on `filetypes/pkg_info`

Cycle `20261102T221633-confirm-7266671733664807` — 2026-11-02T22:16:33Z

confirmation measured L25 recall regressed: 0.75758 -> 0.66667

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `7266671733664807` | `57d8ef321c08a534` | `57d8ef321c08a534` | `57d8ef321c08a534` |
| PR AUC | 0.8673 | 0.8651 | 0.8508 | 0.8466 |
| ROC AUC | 0.9847 | 0.9886 | 0.9860 | 0.9854 |
| Recall@L50 | — | 0.5455 | 0.3939 | 0.4242 |
| verdict | — | PASS | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (1/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
