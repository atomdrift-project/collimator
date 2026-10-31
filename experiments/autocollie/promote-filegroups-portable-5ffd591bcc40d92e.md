# Promote REJECTED — `5ffd591bcc40d92e` on `filegroups/portable`

Generated 2026-10-30T21:26:29Z

confirm did not hold: confirmation measured L25 recall regressed: 0.80488 -> 0.78184

## Gates

- **Confirm** (different seed, original profile): **FAIL** — confirmation measured L25 recall regressed: 0.80488 -> 0.78184
- **Full-train**: not run (confirm gate failed)

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `5ffd591bcc40d92e` | `943755424ae796a9` | `—` |
| PR AUC | 0.9695 | 0.9754 | — |
| ROC AUC | 0.9943 | 0.9954 | — |
| F1 | 0.9193 | 0.9317 | — |

## Disposition

This spec did not survive the promotion ladder.

confirm did not hold: confirmation measured L25 recall regressed: 0.80488 -> 0.78184
