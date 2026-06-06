# Promote REJECTED — `5344f113a9f3f14a` on `filegroups/portable`

Generated 2026-06-06T16:34:17Z

azoth-validate failed: signal: terminated (log /home/t/collimator/out/autocollie/runs/2026-06-06T16-31-19_20260606T163111-promote-5344f113a9f3f14a_azoth-validate.log; tail: 2026-06-06 12:33:13,577 INFO azoth_calibrate_ensemble: filetypes/crx: using cached scores
2026-06-06 12:33:13,666 INFO azoth_calibrate_ensemble: filetypes/chrome-manifest: using cached scores
2026-06-06 12:33:14,006 INFO azoth_calibrate_ensemble: L0 on test: hostile recall=58.11% fp=221 (FP/100M=41757.20)
2026-06-06 12:33:14,022 INFO azoth_calibrate_ensemble: L1 on test: hostile recall=58.11% fp=221 (FP/100M=41757.20)
2026-06-06 12:33:14,038 INFO azoth_calibrate_ensemble: L2 on test: hostile recall=58.11% fp=221 (FP/100M=41757.20)
2026-06-06 12:33:14,053 INFO azoth_calibrate_ensemble: L3 on test: hostile recall=58.12% fp=221 (FP/100M=41757.20)
2026-06-06 12:33:14,069 INFO azoth_calibrate_ensemble: L4 on test: hostile recall=58.12% fp=221 (FP/100M=41757.20)
2026-06-06 12:33:14,085 INFO azoth_calibrate_ensemble: L5 on test: hostile recall=58.12% fp=221 (FP/100M=41757.20)
2026-06-06 12:33:14,100 INFO azoth_calibrate_ensemble: L10 on test: hostile recall=58.13% fp=221 (FP/100M=41757.20)
2026-06-06 12:33:14,116 INFO azoth_calibrate_ensemble: L20 on test: hostile recall=58.15% fp=221 (FP/100M=41757.20)
2026-06-06 12:33:14,133 INFO azoth_calibrate_ensemble: L30 on test: hostile recall=58.17% fp=221 (FP/100M=41757.20)
2026-06-06 12:33:14,148 INFO azoth_calibrate_ensemble: L40 on test: hostile recall=58.18% fp=221 (FP/100M=41757.20)
2026-06-06 12:33:14,164 INFO azoth_calibrate_ensemble: L50 on test: hostile recall=58.20% fp=221 (FP/100M=41757.20)
2026-06-06 12:33:14,180 INFO azoth_calibrate_ensemble: L60 on test: hostile recall=58.21% fp=221 (FP/100M=41757.20)
2026-06-06 12:33:14,196 INFO azoth_calibrate_ensemble: L70 on test: hostile recall=58.23% fp=221 (FP/100M=41757.20)
2026-06-06 12:33:14,212 INFO azoth_calibrate_ensemble: L80 on test: hostile recall=58.25% fp=221 (FP/100M=41757.20)
2026-06-06 12:33:14,228 INFO azoth_calibrate_ensemble: L90 on test: hostile recall=58.26% fp=221 (FP/100M=41757.20)
2026-06-06 12:33:14,244 INFO azoth_calibrate_ensemble: L100 on test: hostile recall=58.27% fp=221 (FP/100M=41757.20)
2026-06-06 12:33:14,261 INFO azoth_calibrate_ensemble: L200 on test: hostile recall=58.45% fp=223 (FP/100M=42135.10)
2026-06-06 12:33:14,282 INFO azoth_calibrate_ensemble: L300 on test: hostile recall=58.94% fp=224 (FP/100M=42324.04)
2026-06-06 12:33:14,303 INFO azoth_calibrate_ensemble: L500 on test: hostile recall=59.48% fp=227 (FP/100M=42890.88)
2026-06-06 12:33:14,324 INFO azoth_calibrate_ensemble: L1000 on test: hostile recall=60.81% fp=231 (FP/100M=43646.67)
2026-06-06 12:33:14,346 INFO azoth_calibrate_ensemble: L2000 on test: hostile recall=63.72% fp=246 (FP/100M=46480.87)
2026-06-06 12:33:14,367 INFO azoth_calibrate_ensemble: L5000 on test: hostile recall=67.17% fp=285 (FP/100M=53849.79)
2026-06-06 12:33:14,388 INFO azoth_calibrate_ensemble: L7500 on test: hostile recall=69.45% fp=311 (FP/100M=58762.40)
2026-06-06 12:33:14,410 INFO azoth_calibrate_ensemble: L10000 on test: hostile recall=70.87% fp=345 (FP/100M=65186.58)
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-portable-5344f113a9f3f14a/test_metrics.json
.venv/bin/python scripts/azoth_route_policy_search.py \
	 \
	--config /home/t/collimator/out/models/azoth-candidate-filegroups-portable-5344f113a9f3f14a/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filegroups-portable-5344f113a9f3f14a/score_table.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filegroups-portable-5344f113a9f3f14a/route_policies.json \
	--csv /home/t/collimator/out/models/azoth-candidate-filegroups-portable-5344f113a9f3f14a/route_policies.csv \
	--markdown /home/t/collimator/out/models/azoth-candidate-filegroups-portable-5344f113a9f3f14a/route_policies.md \
	 \
	--previous-bundle out/models/azoth \
	--workers 128
policy_search carry-forward: 1/54 routes changed; 85/86 filetypes can be carried forward from previous bundle
policy_search: processing 1 filetypes serially (85 carried forward)
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-portable-5344f113a9f3f14a/route_policies.json
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-portable-5344f113a9f3f14a/route_policies.csv
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-portable-5344f113a9f3f14a/route_policies.md
.venv/bin/python scripts/azoth_policy_global_metrics.py \
	--config /home/t/collimator/out/models/azoth-candidate-filegroups-portable-5344f113a9f3f14a/config.json \
	--policy /home/t/collimator/out/models/azoth-candidate-filegroups-portable-5344f113a9f3f14a/route_policies.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filegroups-portable-5344f113a9f3f14a/score_table.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filegroups-portable-5344f113a9f3f14a/global_policy_metrics.json \
	--markdown /home/t/collimator/out/models/azoth-candidate-filegroups-portable-5344f113a9f3f14a/global_policy_metrics.md \
	--fail-on-budget --max-budget-multiplier 30
make[2]: *** [Makefile:1286: azoth-validate] Terminated)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9955)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `5344f113a9f3f14a` | `d345ad574d0cfd60` | `3559044eb82a2da6` |
| PR AUC | 0.9955 | 0.9911 | 0.9913 |
| ROC AUC | 0.9992 | 0.9984 | 0.9984 |
| F1 | 0.9602 | 0.9626 | 0.9561 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: signal: terminated (log /home/t/collimator/out/autocollie/runs/2026-06-06T16-31-19_20260606T163111-promote-5344f113a9f3f14a_azoth-validate.log; tail: 2026-06-06 12:33:13,577 INFO azoth_calibrate_ensemble: filetypes/crx: using cached scores
2026-06-06 12:33:13,666 INFO azoth_calibrate_ensemble: filetypes/chrome-manifest: using cached scores
2026-06-06 12:33:14,006 INFO azoth_calibrate_ensemble: L0 on test: hostile recall=58.11% fp=221 (FP/100M=41757.20)
2026-06-06 12:33:14,022 INFO azoth_calibrate_ensemble: L1 on test: hostile recall=58.11% fp=221 (FP/100M=41757.20)
2026-06-06 12:33:14,038 INFO azoth_calibrate_ensemble: L2 on test: hostile recall=58.11% fp=221 (FP/100M=41757.20)
2026-06-06 12:33:14,053 INFO azoth_calibrate_ensemble: L3 on test: hostile recall=58.12% fp=221 (FP/100M=41757.20)
2026-06-06 12:33:14,069 INFO azoth_calibrate_ensemble: L4 on test: hostile recall=58.12% fp=221 (FP/100M=41757.20)
2026-06-06 12:33:14,085 INFO azoth_calibrate_ensemble: L5 on test: hostile recall=58.12% fp=221 (FP/100M=41757.20)
2026-06-06 12:33:14,100 INFO azoth_calibrate_ensemble: L10 on test: hostile recall=58.13% fp=221 (FP/100M=41757.20)
2026-06-06 12:33:14,116 INFO azoth_calibrate_ensemble: L20 on test: hostile recall=58.15% fp=221 (FP/100M=41757.20)
2026-06-06 12:33:14,133 INFO azoth_calibrate_ensemble: L30 on test: hostile recall=58.17% fp=221 (FP/100M=41757.20)
2026-06-06 12:33:14,148 INFO azoth_calibrate_ensemble: L40 on test: hostile recall=58.18% fp=221 (FP/100M=41757.20)
2026-06-06 12:33:14,164 INFO azoth_calibrate_ensemble: L50 on test: hostile recall=58.20% fp=221 (FP/100M=41757.20)
2026-06-06 12:33:14,180 INFO azoth_calibrate_ensemble: L60 on test: hostile recall=58.21% fp=221 (FP/100M=41757.20)
2026-06-06 12:33:14,196 INFO azoth_calibrate_ensemble: L70 on test: hostile recall=58.23% fp=221 (FP/100M=41757.20)
2026-06-06 12:33:14,212 INFO azoth_calibrate_ensemble: L80 on test: hostile recall=58.25% fp=221 (FP/100M=41757.20)
2026-06-06 12:33:14,228 INFO azoth_calibrate_ensemble: L90 on test: hostile recall=58.26% fp=221 (FP/100M=41757.20)
2026-06-06 12:33:14,244 INFO azoth_calibrate_ensemble: L100 on test: hostile recall=58.27% fp=221 (FP/100M=41757.20)
2026-06-06 12:33:14,261 INFO azoth_calibrate_ensemble: L200 on test: hostile recall=58.45% fp=223 (FP/100M=42135.10)
2026-06-06 12:33:14,282 INFO azoth_calibrate_ensemble: L300 on test: hostile recall=58.94% fp=224 (FP/100M=42324.04)
2026-06-06 12:33:14,303 INFO azoth_calibrate_ensemble: L500 on test: hostile recall=59.48% fp=227 (FP/100M=42890.88)
2026-06-06 12:33:14,324 INFO azoth_calibrate_ensemble: L1000 on test: hostile recall=60.81% fp=231 (FP/100M=43646.67)
2026-06-06 12:33:14,346 INFO azoth_calibrate_ensemble: L2000 on test: hostile recall=63.72% fp=246 (FP/100M=46480.87)
2026-06-06 12:33:14,367 INFO azoth_calibrate_ensemble: L5000 on test: hostile recall=67.17% fp=285 (FP/100M=53849.79)
2026-06-06 12:33:14,388 INFO azoth_calibrate_ensemble: L7500 on test: hostile recall=69.45% fp=311 (FP/100M=58762.40)
2026-06-06 12:33:14,410 INFO azoth_calibrate_ensemble: L10000 on test: hostile recall=70.87% fp=345 (FP/100M=65186.58)
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-portable-5344f113a9f3f14a/test_metrics.json
.venv/bin/python scripts/azoth_route_policy_search.py \
	 \
	--config /home/t/collimator/out/models/azoth-candidate-filegroups-portable-5344f113a9f3f14a/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filegroups-portable-5344f113a9f3f14a/score_table.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filegroups-portable-5344f113a9f3f14a/route_policies.json \
	--csv /home/t/collimator/out/models/azoth-candidate-filegroups-portable-5344f113a9f3f14a/route_policies.csv \
	--markdown /home/t/collimator/out/models/azoth-candidate-filegroups-portable-5344f113a9f3f14a/route_policies.md \
	 \
	--previous-bundle out/models/azoth \
	--workers 128
policy_search carry-forward: 1/54 routes changed; 85/86 filetypes can be carried forward from previous bundle
policy_search: processing 1 filetypes serially (85 carried forward)
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-portable-5344f113a9f3f14a/route_policies.json
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-portable-5344f113a9f3f14a/route_policies.csv
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-portable-5344f113a9f3f14a/route_policies.md
.venv/bin/python scripts/azoth_policy_global_metrics.py \
	--config /home/t/collimator/out/models/azoth-candidate-filegroups-portable-5344f113a9f3f14a/config.json \
	--policy /home/t/collimator/out/models/azoth-candidate-filegroups-portable-5344f113a9f3f14a/route_policies.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filegroups-portable-5344f113a9f3f14a/score_table.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filegroups-portable-5344f113a9f3f14a/global_policy_metrics.json \
	--markdown /home/t/collimator/out/models/azoth-candidate-filegroups-portable-5344f113a9f3f14a/global_policy_metrics.md \
	--fail-on-budget --max-budget-multiplier 30
make[2]: *** [Makefile:1286: azoth-validate] Terminated)
