# Promote REJECTED — `79510faeb184368b` on `filetypes/dex`

Generated 2026-10-31T00:52:26Z

confirm did not hold: confirmation measured L25 recall regressed: 0.93750 -> 0.87500

## Gates

- **Confirm** (different seed, original profile): **FAIL** — confirmation measured L25 recall regressed: 0.93750 -> 0.87500
- **Full-train**: not run (confirm gate failed)

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `79510faeb184368b` | `db4a706dd11ff2af` | `—` |
| PR AUC | 0.9511 | 0.9617 | — |
| ROC AUC | 0.9668 | 0.9707 | — |
| F1 | 0.7200 | 0.9091 | — |

## Disposition

This spec did not survive the promotion ladder.

confirm did not hold: confirmation measured L25 recall regressed: 0.93750 -> 0.87500
