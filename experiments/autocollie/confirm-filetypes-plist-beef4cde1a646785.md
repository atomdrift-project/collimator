# Confirm FAIL — beef4cde1a646785 on `filetypes/plist`

Cycle `20260608T120311-confirm-beef4cde1a646785` — 2026-06-08T12:03:11Z

averaged ensemble PR_AUC regressed: 0.2669 -> 0.2460 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `beef4cde1a646785` | `baa85c689bacd16c` | `baa85c689bacd16c` | `baa85c689bacd16c` |
| PR AUC | 0.2669 | 0.2337 | 0.2512 | 0.1438 |
| ROC AUC | 0.8032 | 0.7916 | 0.8011 | 0.6555 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
