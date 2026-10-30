# Confirm FAIL — bb8825a47ea45b53 on `filetypes/package.json`

Cycle `20261030T132951-confirm-bb8825a47ea45b53` — 2026-10-30T13:29:51Z

confirmation measured L25 recall regressed: 0.79153 -> 0.77597

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `bb8825a47ea45b53` | `f81a2bb6fd33751a` | `f81a2bb6fd33751a` | `f81a2bb6fd33751a` |
| PR AUC | 0.9776 | 0.9785 | 0.9758 | 0.9782 |
| ROC AUC | 0.9824 | 0.9847 | 0.9782 | 0.9844 |
| Recall@L50 | — | 0.3999 | 0.6960 | 0.4662 |
| verdict | — | PASS | PASS | PASS |

## Disposition

This spec did not survive multi-seed reseeding (3/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
