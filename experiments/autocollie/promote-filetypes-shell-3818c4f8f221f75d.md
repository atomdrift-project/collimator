# Promote REJECTED — `3818c4f8f221f75d` on `filetypes/shell`

Generated 2026-06-01T16:18:02Z

azoth-validate failed: signal: terminated (log /home/t/collimator/out/autocollie/runs/2026-06-01T14-17-15_20260601T141649-promote-3818c4f8f221f75d_azoth-validate.log; tail: 2026-06-01 10:19:08,566 INFO azoth_calibrate_ensemble: filetypes/macho: using cached scores
2026-06-01 10:19:08,671 INFO azoth_calibrate_ensemble: filetypes/plist: using cached scores
2026-06-01 10:19:08,797 INFO azoth_calibrate_ensemble: filetypes/vbs: using cached scores
2026-06-01 10:19:08,985 INFO azoth_calibrate_ensemble: filetypes/pkg-info: using cached scores
2026-06-01 10:19:09,109 INFO azoth_calibrate_ensemble: filetypes/ole: using cached scores
2026-06-01 10:19:09,234 INFO azoth_calibrate_ensemble: filetypes/powershell: using cached scores
2026-06-01 10:19:09,323 INFO azoth_calibrate_ensemble: filetypes/deb: using cached scores
2026-06-01 10:19:09,435 INFO azoth_calibrate_ensemble: filetypes/jar: using cached scores
2026-06-01 10:19:09,569 INFO azoth_calibrate_ensemble: filetypes/groovy: using cached scores
2026-06-01 10:19:09,725 INFO azoth_calibrate_ensemble: filetypes/rtf: using cached scores
2026-06-01 10:19:09,799 INFO azoth_calibrate_ensemble: filetypes/lnk: using cached scores
2026-06-01 10:19:09,908 INFO azoth_calibrate_ensemble: filetypes/docx: using cached scores
2026-06-01 10:19:10,036 INFO azoth_calibrate_ensemble: filetypes/clojure: using cached scores
2026-06-01 10:19:10,188 INFO azoth_calibrate_ensemble: filetypes/tar: using cached scores
2026-06-01 10:19:10,333 INFO azoth_calibrate_ensemble: filetypes/dockerfile: using cached scores
2026-06-01 10:19:10,411 INFO azoth_calibrate_ensemble: filetypes/package-lock.json: using cached scores
2026-06-01 10:19:10,497 INFO azoth_calibrate_ensemble: filetypes/pptx: using cached scores
2026-06-01 10:19:10,625 INFO azoth_calibrate_ensemble: filetypes/chrome-manifest: using cached scores
2026-06-01 10:19:10,759 INFO azoth_calibrate_ensemble: filetypes/crx: using cached scores
2026-06-01 10:19:11,098 INFO azoth_calibrate_ensemble: L0 on test: hostile recall=0.00% fp=0 (FP/100M=0.00)
2026-06-01 10:19:11,121 INFO azoth_calibrate_ensemble: L1 on test: hostile recall=62.54% fp=4265 (FP/100M=812226.24)
2026-06-01 10:19:11,143 INFO azoth_calibrate_ensemble: L2 on test: hostile recall=62.56% fp=4265 (FP/100M=812226.24)
2026-06-01 10:19:11,166 INFO azoth_calibrate_ensemble: L3 on test: hostile recall=62.58% fp=4265 (FP/100M=812226.24)
2026-06-01 10:19:11,188 INFO azoth_calibrate_ensemble: L5 on test: hostile recall=62.61% fp=4265 (FP/100M=812226.24)
2026-06-01 10:19:11,210 INFO azoth_calibrate_ensemble: L10 on test: hostile recall=62.67% fp=4265 (FP/100M=812226.24)
2026-06-01 10:19:11,233 INFO azoth_calibrate_ensemble: L20 on test: hostile recall=62.82% fp=4265 (FP/100M=812226.24)
2026-06-01 10:19:11,255 INFO azoth_calibrate_ensemble: L30 on test: hostile recall=62.91% fp=4265 (FP/100M=812226.24)
2026-06-01 10:19:11,277 INFO azoth_calibrate_ensemble: L40 on test: hostile recall=63.04% fp=4266 (FP/100M=812416.68)
2026-06-01 10:19:11,299 INFO azoth_calibrate_ensemble: L50 on test: hostile recall=63.10% fp=4266 (FP/100M=812416.68)
2026-06-01 10:19:11,321 INFO azoth_calibrate_ensemble: L60 on test: hostile recall=63.21% fp=4266 (FP/100M=812416.68)
2026-06-01 10:19:11,344 INFO azoth_calibrate_ensemble: L70 on test: hostile recall=63.27% fp=4266 (FP/100M=812416.68)
2026-06-01 10:19:11,366 INFO azoth_calibrate_ensemble: L80 on test: hostile recall=63.32% fp=4265 (FP/100M=812226.24)
2026-06-01 10:19:11,388 INFO azoth_calibrate_ensemble: L90 on test: hostile recall=63.36% fp=4265 (FP/100M=812226.24)
2026-06-01 10:19:11,410 INFO azoth_calibrate_ensemble: L100 on test: hostile recall=63.40% fp=4265 (FP/100M=812226.24)
2026-06-01 10:19:11,433 INFO azoth_calibrate_ensemble: L200 on test: hostile recall=64.41% fp=4262 (FP/100M=811654.92)
2026-06-01 10:19:11,455 INFO azoth_calibrate_ensemble: L300 on test: hostile recall=64.64% fp=4262 (FP/100M=811654.92)
2026-06-01 10:19:11,477 INFO azoth_calibrate_ensemble: L500 on test: hostile recall=65.38% fp=4263 (FP/100M=811845.36)
2026-06-01 10:19:11,500 INFO azoth_calibrate_ensemble: L1000 on test: hostile recall=67.42% fp=4264 (FP/100M=812035.80)
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-shell-3818c4f8f221f75d/test_metrics.json
.venv/bin/python scripts/azoth_route_policy_search.py \
	 \
	--config /home/t/collimator/out/models/azoth-candidate-filetypes-shell-3818c4f8f221f75d/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-shell-3818c4f8f221f75d/score_table.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-shell-3818c4f8f221f75d/route_policies.json \
	--csv /home/t/collimator/out/models/azoth-candidate-filetypes-shell-3818c4f8f221f75d/route_policies.csv \
	--markdown /home/t/collimator/out/models/azoth-candidate-filetypes-shell-3818c4f8f221f75d/route_policies.md \
	 \
	--previous-bundle out/models/azoth \
	--workers 128
make[2]: *** [Makefile:1140: azoth-validate] Terminated)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9963)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `3818c4f8f221f75d` | `4b17289988f59346` | `aaa32205fd6d98f8` |
| PR AUC | 0.9963 | 0.9986 | 0.9987 |
| ROC AUC | 0.9976 | 0.9987 | 0.9988 |
| F1 | 0.9650 | 0.9769 | 0.9772 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: signal: terminated (log /home/t/collimator/out/autocollie/runs/2026-06-01T14-17-15_20260601T141649-promote-3818c4f8f221f75d_azoth-validate.log; tail: 2026-06-01 10:19:08,566 INFO azoth_calibrate_ensemble: filetypes/macho: using cached scores
2026-06-01 10:19:08,671 INFO azoth_calibrate_ensemble: filetypes/plist: using cached scores
2026-06-01 10:19:08,797 INFO azoth_calibrate_ensemble: filetypes/vbs: using cached scores
2026-06-01 10:19:08,985 INFO azoth_calibrate_ensemble: filetypes/pkg-info: using cached scores
2026-06-01 10:19:09,109 INFO azoth_calibrate_ensemble: filetypes/ole: using cached scores
2026-06-01 10:19:09,234 INFO azoth_calibrate_ensemble: filetypes/powershell: using cached scores
2026-06-01 10:19:09,323 INFO azoth_calibrate_ensemble: filetypes/deb: using cached scores
2026-06-01 10:19:09,435 INFO azoth_calibrate_ensemble: filetypes/jar: using cached scores
2026-06-01 10:19:09,569 INFO azoth_calibrate_ensemble: filetypes/groovy: using cached scores
2026-06-01 10:19:09,725 INFO azoth_calibrate_ensemble: filetypes/rtf: using cached scores
2026-06-01 10:19:09,799 INFO azoth_calibrate_ensemble: filetypes/lnk: using cached scores
2026-06-01 10:19:09,908 INFO azoth_calibrate_ensemble: filetypes/docx: using cached scores
2026-06-01 10:19:10,036 INFO azoth_calibrate_ensemble: filetypes/clojure: using cached scores
2026-06-01 10:19:10,188 INFO azoth_calibrate_ensemble: filetypes/tar: using cached scores
2026-06-01 10:19:10,333 INFO azoth_calibrate_ensemble: filetypes/dockerfile: using cached scores
2026-06-01 10:19:10,411 INFO azoth_calibrate_ensemble: filetypes/package-lock.json: using cached scores
2026-06-01 10:19:10,497 INFO azoth_calibrate_ensemble: filetypes/pptx: using cached scores
2026-06-01 10:19:10,625 INFO azoth_calibrate_ensemble: filetypes/chrome-manifest: using cached scores
2026-06-01 10:19:10,759 INFO azoth_calibrate_ensemble: filetypes/crx: using cached scores
2026-06-01 10:19:11,098 INFO azoth_calibrate_ensemble: L0 on test: hostile recall=0.00% fp=0 (FP/100M=0.00)
2026-06-01 10:19:11,121 INFO azoth_calibrate_ensemble: L1 on test: hostile recall=62.54% fp=4265 (FP/100M=812226.24)
2026-06-01 10:19:11,143 INFO azoth_calibrate_ensemble: L2 on test: hostile recall=62.56% fp=4265 (FP/100M=812226.24)
2026-06-01 10:19:11,166 INFO azoth_calibrate_ensemble: L3 on test: hostile recall=62.58% fp=4265 (FP/100M=812226.24)
2026-06-01 10:19:11,188 INFO azoth_calibrate_ensemble: L5 on test: hostile recall=62.61% fp=4265 (FP/100M=812226.24)
2026-06-01 10:19:11,210 INFO azoth_calibrate_ensemble: L10 on test: hostile recall=62.67% fp=4265 (FP/100M=812226.24)
2026-06-01 10:19:11,233 INFO azoth_calibrate_ensemble: L20 on test: hostile recall=62.82% fp=4265 (FP/100M=812226.24)
2026-06-01 10:19:11,255 INFO azoth_calibrate_ensemble: L30 on test: hostile recall=62.91% fp=4265 (FP/100M=812226.24)
2026-06-01 10:19:11,277 INFO azoth_calibrate_ensemble: L40 on test: hostile recall=63.04% fp=4266 (FP/100M=812416.68)
2026-06-01 10:19:11,299 INFO azoth_calibrate_ensemble: L50 on test: hostile recall=63.10% fp=4266 (FP/100M=812416.68)
2026-06-01 10:19:11,321 INFO azoth_calibrate_ensemble: L60 on test: hostile recall=63.21% fp=4266 (FP/100M=812416.68)
2026-06-01 10:19:11,344 INFO azoth_calibrate_ensemble: L70 on test: hostile recall=63.27% fp=4266 (FP/100M=812416.68)
2026-06-01 10:19:11,366 INFO azoth_calibrate_ensemble: L80 on test: hostile recall=63.32% fp=4265 (FP/100M=812226.24)
2026-06-01 10:19:11,388 INFO azoth_calibrate_ensemble: L90 on test: hostile recall=63.36% fp=4265 (FP/100M=812226.24)
2026-06-01 10:19:11,410 INFO azoth_calibrate_ensemble: L100 on test: hostile recall=63.40% fp=4265 (FP/100M=812226.24)
2026-06-01 10:19:11,433 INFO azoth_calibrate_ensemble: L200 on test: hostile recall=64.41% fp=4262 (FP/100M=811654.92)
2026-06-01 10:19:11,455 INFO azoth_calibrate_ensemble: L300 on test: hostile recall=64.64% fp=4262 (FP/100M=811654.92)
2026-06-01 10:19:11,477 INFO azoth_calibrate_ensemble: L500 on test: hostile recall=65.38% fp=4263 (FP/100M=811845.36)
2026-06-01 10:19:11,500 INFO azoth_calibrate_ensemble: L1000 on test: hostile recall=67.42% fp=4264 (FP/100M=812035.80)
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-shell-3818c4f8f221f75d/test_metrics.json
.venv/bin/python scripts/azoth_route_policy_search.py \
	 \
	--config /home/t/collimator/out/models/azoth-candidate-filetypes-shell-3818c4f8f221f75d/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-shell-3818c4f8f221f75d/score_table.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-shell-3818c4f8f221f75d/route_policies.json \
	--csv /home/t/collimator/out/models/azoth-candidate-filetypes-shell-3818c4f8f221f75d/route_policies.csv \
	--markdown /home/t/collimator/out/models/azoth-candidate-filetypes-shell-3818c4f8f221f75d/route_policies.md \
	 \
	--previous-bundle out/models/azoth \
	--workers 128
make[2]: *** [Makefile:1140: azoth-validate] Terminated)
