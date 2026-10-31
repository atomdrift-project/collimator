# Promote REJECTED — `107889095c2ad603` on `filetypes/apk_android`

Generated 2026-10-30T21:45:12Z

confirm did not hold: confirmation measured L25 recall regressed: 0.98013 -> 0.97682

## Gates

- **Confirm** (different seed, original profile): **FAIL** — confirmation measured L25 recall regressed: 0.98013 -> 0.97682
- **Full-train**: not run (confirm gate failed)

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `107889095c2ad603` | `0e220736a22407fc` | `—` |
| PR AUC | 0.9992 | 0.9997 | — |
| ROC AUC | 0.9956 | 0.9982 | — |
| F1 | 0.9789 | 0.9885 | — |

## Disposition

This spec did not survive the promotion ladder.

confirm did not hold: confirmation measured L25 recall regressed: 0.98013 -> 0.97682
