# Promote REJECTED — `6dc878c459ec40c6` on `filetypes/static-lib`

Generated 2026-10-29T12:53:20Z

confirm did not hold: confirmation measured L25 recall regressed: 0.33077 -> 0.31538

## Gates

- **Confirm** (different seed, original profile): **FAIL** — confirmation measured L25 recall regressed: 0.33077 -> 0.31538
- **Full-train**: not run (confirm gate failed)

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `6dc878c459ec40c6` | `eeb5fe926bfe18b6` | `—` |
| PR AUC | 0.7575 | 0.7608 | — |
| ROC AUC | 0.9452 | 0.9425 | — |
| F1 | 0.2895 | 0.6390 | — |

## Disposition

This spec did not survive the promotion ladder.

confirm did not hold: confirmation measured L25 recall regressed: 0.33077 -> 0.31538
