# Promote REJECTED — `8304c75900f902c0` on `filetypes/pe`

Generated 2026-06-07T02:26:22Z

azoth-validate failed: signal: terminated (log /home/t/collimator/out/autocollie/runs/2026-06-07T02-10-44_20260607T015021-promote-8304c75900f902c0_azoth-validate.log; tail: 2026-06-06 22:26:12,797 INFO azoth_calibrate_ensemble: filetypes/ole: using cached scores
2026-06-06 22:26:12,938 INFO azoth_calibrate_ensemble: filetypes/pkg-info: using cached scores
2026-06-06 22:26:13,089 INFO azoth_calibrate_ensemble: filetypes/html: using cached scores
2026-06-06 22:26:13,293 INFO azoth_calibrate_ensemble: filetypes/powershell: using cached scores
2026-06-06 22:26:13,409 INFO azoth_calibrate_ensemble: filetypes/deb: using cached scores
2026-06-06 22:26:13,446 INFO azoth_calibrate_ensemble: filetypes/jar: using cached scores
2026-06-06 22:26:13,609 INFO azoth_calibrate_ensemble: filetypes/rtf: using cached scores
2026-06-06 22:26:13,735 INFO azoth_calibrate_ensemble: filetypes/groovy: using cached scores
2026-06-06 22:26:13,910 INFO azoth_calibrate_ensemble: filetypes/msi: using cached scores
2026-06-06 22:26:14,047 INFO azoth_calibrate_ensemble: filetypes/lnk: using cached scores
2026-06-06 22:26:14,157 INFO azoth_calibrate_ensemble: filetypes/clojure: using cached scores
2026-06-06 22:26:14,267 INFO azoth_calibrate_ensemble: filetypes/docx: using cached scores
2026-06-06 22:26:14,345 INFO azoth_calibrate_ensemble: filetypes/crx: using cached scores
2026-06-06 22:26:14,432 INFO azoth_calibrate_ensemble: filetypes/chrome-manifest: using cached scores
2026-06-06 22:26:14,789 INFO azoth_calibrate_ensemble: L0 on test: hostile recall=57.10% fp=90490 (FP/100M=17097779.88)
2026-06-06 22:26:14,810 INFO azoth_calibrate_ensemble: L1 on test: hostile recall=57.10% fp=90490 (FP/100M=17097779.88)
2026-06-06 22:26:14,831 INFO azoth_calibrate_ensemble: L2 on test: hostile recall=57.10% fp=90490 (FP/100M=17097779.88)
2026-06-06 22:26:14,852 INFO azoth_calibrate_ensemble: L3 on test: hostile recall=57.10% fp=90490 (FP/100M=17097779.88)
2026-06-06 22:26:14,873 INFO azoth_calibrate_ensemble: L4 on test: hostile recall=57.10% fp=90490 (FP/100M=17097779.88)
2026-06-06 22:26:14,894 INFO azoth_calibrate_ensemble: L5 on test: hostile recall=57.10% fp=90490 (FP/100M=17097779.88)
2026-06-06 22:26:14,915 INFO azoth_calibrate_ensemble: L10 on test: hostile recall=57.65% fp=91338 (FP/100M=17258006.61)
2026-06-06 22:26:14,936 INFO azoth_calibrate_ensemble: L20 on test: hostile recall=65.08% fp=91419 (FP/100M=17273311.29)
2026-06-06 22:26:14,959 INFO azoth_calibrate_ensemble: L30 on test: hostile recall=68.30% fp=92845 (FP/100M=17542749.17)
2026-06-06 22:26:14,980 INFO azoth_calibrate_ensemble: L40 on test: hostile recall=76.37% fp=93021 (FP/100M=17576003.78)
2026-06-06 22:26:15,001 INFO azoth_calibrate_ensemble: L50 on test: hostile recall=76.51% fp=93076 (FP/100M=17586395.84)
2026-06-06 22:26:15,022 INFO azoth_calibrate_ensemble: L60 on test: hostile recall=76.98% fp=93130 (FP/100M=17596598.96)
2026-06-06 22:26:15,043 INFO azoth_calibrate_ensemble: L70 on test: hostile recall=77.45% fp=93191 (FP/100M=17608124.70)
2026-06-06 22:26:15,064 INFO azoth_calibrate_ensemble: L80 on test: hostile recall=78.91% fp=93246 (FP/100M=17618516.77)
2026-06-06 22:26:15,085 INFO azoth_calibrate_ensemble: L90 on test: hostile recall=79.00% fp=93396 (FP/100M=17646858.76)
2026-06-06 22:26:15,106 INFO azoth_calibrate_ensemble: L100 on test: hostile recall=79.81% fp=93445 (FP/100M=17656117.15)
2026-06-06 22:26:15,127 INFO azoth_calibrate_ensemble: L200 on test: hostile recall=82.67% fp=95268 (FP/100M=18000566.84)
2026-06-06 22:26:15,149 INFO azoth_calibrate_ensemble: L300 on test: hostile recall=84.83% fp=95675 (FP/100M=18077468.12)
2026-06-06 22:26:15,170 INFO azoth_calibrate_ensemble: L500 on test: hostile recall=86.15% fp=96566 (FP/100M=18245819.56)
2026-06-06 22:26:15,192 INFO azoth_calibrate_ensemble: L1000 on test: hostile recall=88.07% fp=108984 (FP/100M=20592158.72)
2026-06-06 22:26:15,213 INFO azoth_calibrate_ensemble: L2000 on test: hostile recall=89.29% fp=111659 (FP/100M=21097590.93)
2026-06-06 22:26:15,235 INFO azoth_calibrate_ensemble: L5000 on test: hostile recall=90.08% fp=110802 (FP/100M=20935663.68)
2026-06-06 22:26:15,257 INFO azoth_calibrate_ensemble: L7500 on test: hostile recall=80.59% fp=108129 (FP/100M=20430609.35)
2026-06-06 22:26:15,279 INFO azoth_calibrate_ensemble: L10000 on test: hostile recall=82.23% fp=97114 (FP/100M=18349362.31)
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-pe-8304c75900f902c0/test_metrics.json
.venv/bin/python scripts/azoth_route_policy_search.py \
	 \
	--config /home/t/collimator/out/models/azoth-candidate-filetypes-pe-8304c75900f902c0/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-pe-8304c75900f902c0/score_table.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-pe-8304c75900f902c0/route_policies.json \
	--csv /home/t/collimator/out/models/azoth-candidate-filetypes-pe-8304c75900f902c0/route_policies.csv \
	--markdown /home/t/collimator/out/models/azoth-candidate-filetypes-pe-8304c75900f902c0/route_policies.md \
	 \
	--previous-bundle out/models/azoth \
	--workers 128
make[1]: *** [Makefile:1298: azoth-validate] Terminated)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9995)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `8304c75900f902c0` | `1f71bf544d788800` | `a4ef4dc463a1daa0` |
| PR AUC | 0.9995 | 1.0000 | 1.0000 |
| ROC AUC | 0.9995 | 0.9999 | 0.9999 |
| F1 | 0.9883 | 0.9987 | 0.9975 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: signal: terminated (log /home/t/collimator/out/autocollie/runs/2026-06-07T02-10-44_20260607T015021-promote-8304c75900f902c0_azoth-validate.log; tail: 2026-06-06 22:26:12,797 INFO azoth_calibrate_ensemble: filetypes/ole: using cached scores
2026-06-06 22:26:12,938 INFO azoth_calibrate_ensemble: filetypes/pkg-info: using cached scores
2026-06-06 22:26:13,089 INFO azoth_calibrate_ensemble: filetypes/html: using cached scores
2026-06-06 22:26:13,293 INFO azoth_calibrate_ensemble: filetypes/powershell: using cached scores
2026-06-06 22:26:13,409 INFO azoth_calibrate_ensemble: filetypes/deb: using cached scores
2026-06-06 22:26:13,446 INFO azoth_calibrate_ensemble: filetypes/jar: using cached scores
2026-06-06 22:26:13,609 INFO azoth_calibrate_ensemble: filetypes/rtf: using cached scores
2026-06-06 22:26:13,735 INFO azoth_calibrate_ensemble: filetypes/groovy: using cached scores
2026-06-06 22:26:13,910 INFO azoth_calibrate_ensemble: filetypes/msi: using cached scores
2026-06-06 22:26:14,047 INFO azoth_calibrate_ensemble: filetypes/lnk: using cached scores
2026-06-06 22:26:14,157 INFO azoth_calibrate_ensemble: filetypes/clojure: using cached scores
2026-06-06 22:26:14,267 INFO azoth_calibrate_ensemble: filetypes/docx: using cached scores
2026-06-06 22:26:14,345 INFO azoth_calibrate_ensemble: filetypes/crx: using cached scores
2026-06-06 22:26:14,432 INFO azoth_calibrate_ensemble: filetypes/chrome-manifest: using cached scores
2026-06-06 22:26:14,789 INFO azoth_calibrate_ensemble: L0 on test: hostile recall=57.10% fp=90490 (FP/100M=17097779.88)
2026-06-06 22:26:14,810 INFO azoth_calibrate_ensemble: L1 on test: hostile recall=57.10% fp=90490 (FP/100M=17097779.88)
2026-06-06 22:26:14,831 INFO azoth_calibrate_ensemble: L2 on test: hostile recall=57.10% fp=90490 (FP/100M=17097779.88)
2026-06-06 22:26:14,852 INFO azoth_calibrate_ensemble: L3 on test: hostile recall=57.10% fp=90490 (FP/100M=17097779.88)
2026-06-06 22:26:14,873 INFO azoth_calibrate_ensemble: L4 on test: hostile recall=57.10% fp=90490 (FP/100M=17097779.88)
2026-06-06 22:26:14,894 INFO azoth_calibrate_ensemble: L5 on test: hostile recall=57.10% fp=90490 (FP/100M=17097779.88)
2026-06-06 22:26:14,915 INFO azoth_calibrate_ensemble: L10 on test: hostile recall=57.65% fp=91338 (FP/100M=17258006.61)
2026-06-06 22:26:14,936 INFO azoth_calibrate_ensemble: L20 on test: hostile recall=65.08% fp=91419 (FP/100M=17273311.29)
2026-06-06 22:26:14,959 INFO azoth_calibrate_ensemble: L30 on test: hostile recall=68.30% fp=92845 (FP/100M=17542749.17)
2026-06-06 22:26:14,980 INFO azoth_calibrate_ensemble: L40 on test: hostile recall=76.37% fp=93021 (FP/100M=17576003.78)
2026-06-06 22:26:15,001 INFO azoth_calibrate_ensemble: L50 on test: hostile recall=76.51% fp=93076 (FP/100M=17586395.84)
2026-06-06 22:26:15,022 INFO azoth_calibrate_ensemble: L60 on test: hostile recall=76.98% fp=93130 (FP/100M=17596598.96)
2026-06-06 22:26:15,043 INFO azoth_calibrate_ensemble: L70 on test: hostile recall=77.45% fp=93191 (FP/100M=17608124.70)
2026-06-06 22:26:15,064 INFO azoth_calibrate_ensemble: L80 on test: hostile recall=78.91% fp=93246 (FP/100M=17618516.77)
2026-06-06 22:26:15,085 INFO azoth_calibrate_ensemble: L90 on test: hostile recall=79.00% fp=93396 (FP/100M=17646858.76)
2026-06-06 22:26:15,106 INFO azoth_calibrate_ensemble: L100 on test: hostile recall=79.81% fp=93445 (FP/100M=17656117.15)
2026-06-06 22:26:15,127 INFO azoth_calibrate_ensemble: L200 on test: hostile recall=82.67% fp=95268 (FP/100M=18000566.84)
2026-06-06 22:26:15,149 INFO azoth_calibrate_ensemble: L300 on test: hostile recall=84.83% fp=95675 (FP/100M=18077468.12)
2026-06-06 22:26:15,170 INFO azoth_calibrate_ensemble: L500 on test: hostile recall=86.15% fp=96566 (FP/100M=18245819.56)
2026-06-06 22:26:15,192 INFO azoth_calibrate_ensemble: L1000 on test: hostile recall=88.07% fp=108984 (FP/100M=20592158.72)
2026-06-06 22:26:15,213 INFO azoth_calibrate_ensemble: L2000 on test: hostile recall=89.29% fp=111659 (FP/100M=21097590.93)
2026-06-06 22:26:15,235 INFO azoth_calibrate_ensemble: L5000 on test: hostile recall=90.08% fp=110802 (FP/100M=20935663.68)
2026-06-06 22:26:15,257 INFO azoth_calibrate_ensemble: L7500 on test: hostile recall=80.59% fp=108129 (FP/100M=20430609.35)
2026-06-06 22:26:15,279 INFO azoth_calibrate_ensemble: L10000 on test: hostile recall=82.23% fp=97114 (FP/100M=18349362.31)
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-pe-8304c75900f902c0/test_metrics.json
.venv/bin/python scripts/azoth_route_policy_search.py \
	 \
	--config /home/t/collimator/out/models/azoth-candidate-filetypes-pe-8304c75900f902c0/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-pe-8304c75900f902c0/score_table.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-pe-8304c75900f902c0/route_policies.json \
	--csv /home/t/collimator/out/models/azoth-candidate-filetypes-pe-8304c75900f902c0/route_policies.csv \
	--markdown /home/t/collimator/out/models/azoth-candidate-filetypes-pe-8304c75900f902c0/route_policies.md \
	 \
	--previous-bundle out/models/azoth \
	--workers 128
make[1]: *** [Makefile:1298: azoth-validate] Terminated)
