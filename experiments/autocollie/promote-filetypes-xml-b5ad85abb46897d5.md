# Promote REJECTED — `b5ad85abb46897d5` on `filetypes/xml`

Generated 2026-05-19T21:15:32Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-19T20-55-18_20260519T205507-promote-b5ad85abb46897d5_azoth-validate.log; tail: .venv/bin/python scripts/azoth_route_policy_search.py \
	 \
	--config /home/t/collimator/out/models/azoth-candidate-filetypes-xml-b5ad85abb46897d5/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-xml-b5ad85abb46897d5/score_table.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-xml-b5ad85abb46897d5/route_policies.json \
	--csv /home/t/collimator/out/models/azoth-candidate-filetypes-xml-b5ad85abb46897d5/route_policies.csv \
	--markdown /home/t/collimator/out/models/azoth-candidate-filetypes-xml-b5ad85abb46897d5/route_policies.md \
	 \
	--workers 64
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-xml-b5ad85abb46897d5/route_policies.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-xml-b5ad85abb46897d5/route_policies.csv
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-xml-b5ad85abb46897d5/route_policies.md
.venv/bin/python scripts/azoth_policy_global_metrics.py \
	--config /home/t/collimator/out/models/azoth-candidate-filetypes-xml-b5ad85abb46897d5/config.json \
	--policy /home/t/collimator/out/models/azoth-candidate-filetypes-xml-b5ad85abb46897d5/route_policies.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-xml-b5ad85abb46897d5/score_table.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-xml-b5ad85abb46897d5/global_policy_metrics.json \
	--markdown /home/t/collimator/out/models/azoth-candidate-filetypes-xml-b5ad85abb46897d5/global_policy_metrics.md \
	--fail-on-budget
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-xml-b5ad85abb46897d5/global_policy_metrics.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-xml-b5ad85abb46897d5/global_policy_metrics.md
.venv/bin/python scripts/compute_routed_metrics.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filetypes-xml-b5ad85abb46897d5 --db postgres://hopper@localhost:5432/hopper --no-ci --no-stacked 
computing test-partition metrics (reporting)
loading canonical_sha256 for 4724960 rows to apply test bucket filter
test bucket: 587932/4724960 rows (12.44%)
cached test bucket mask: /home/t/collimator/out/cache/azoth-test-masks/test-dd1932bd9cc2c50fd0a869b4ec1aee58b89da8430bb493c48672dc6886b02ad7.npz
fitting per-route isotonic calibrators (5-fold CV) over 587932 rows
calibration complete; computing per-filetype metrics
filetypes/xlsb: 0 rows in score table; skipping
computing dev-partition metrics (strategy selection)
loading canonical_sha256 for 4724960 rows to apply dev bucket filter
dev bucket: 588729/4724960 rows (12.46%)
cached dev bucket mask: /home/t/collimator/out/cache/azoth-test-masks/dev-dd1932bd9cc2c50fd0a869b4ec1aee58b89da8430bb493c48672dc6886b02ad7.npz
fitting per-route isotonic calibrators (5-fold CV) over 588729 rows
calibration complete; computing per-filetype metrics
filetypes/xlsb: 0 rows in score table; skipping
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-xml-b5ad85abb46897d5/per_filetype_metrics.json (filetypes: 78, filegroups: 0)
.venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filetypes-xml-b5ad85abb46897d5
staged runtime azoth bundle: /tmp/tmp.oAkn0wENNs
azoth bundle ok: /tmp/tmp.oAkn0wENNs

error: 2 regression(s) over tolerance:
  - unknown: recall@3FP/M dropped 12.37pp (12.37% → 0.00%; tolerance 1.00pp)
  - unknown: PR AUC dropped 0.0233 (0.8282 → 0.8049; tolerance 0.0050)

compared 16 filetypes (mal≥500, ben≥500); 62 below threshold and skipped.

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run.
make[1]: *** [Makefile:1070: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 1.0000)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `b5ad85abb46897d5` | `0871be1e08c02f05` | `1429bfb9dc8851ad` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 1.0000 | 1.0000 | 1.0000 |
| F1 | 0.9630 | 1.0000 | 1.0000 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-19T20-55-18_20260519T205507-promote-b5ad85abb46897d5_azoth-validate.log; tail: .venv/bin/python scripts/azoth_route_policy_search.py \
	 \
	--config /home/t/collimator/out/models/azoth-candidate-filetypes-xml-b5ad85abb46897d5/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-xml-b5ad85abb46897d5/score_table.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-xml-b5ad85abb46897d5/route_policies.json \
	--csv /home/t/collimator/out/models/azoth-candidate-filetypes-xml-b5ad85abb46897d5/route_policies.csv \
	--markdown /home/t/collimator/out/models/azoth-candidate-filetypes-xml-b5ad85abb46897d5/route_policies.md \
	 \
	--workers 64
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-xml-b5ad85abb46897d5/route_policies.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-xml-b5ad85abb46897d5/route_policies.csv
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-xml-b5ad85abb46897d5/route_policies.md
.venv/bin/python scripts/azoth_policy_global_metrics.py \
	--config /home/t/collimator/out/models/azoth-candidate-filetypes-xml-b5ad85abb46897d5/config.json \
	--policy /home/t/collimator/out/models/azoth-candidate-filetypes-xml-b5ad85abb46897d5/route_policies.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-xml-b5ad85abb46897d5/score_table.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-xml-b5ad85abb46897d5/global_policy_metrics.json \
	--markdown /home/t/collimator/out/models/azoth-candidate-filetypes-xml-b5ad85abb46897d5/global_policy_metrics.md \
	--fail-on-budget
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-xml-b5ad85abb46897d5/global_policy_metrics.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-xml-b5ad85abb46897d5/global_policy_metrics.md
.venv/bin/python scripts/compute_routed_metrics.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filetypes-xml-b5ad85abb46897d5 --db postgres://hopper@localhost:5432/hopper --no-ci --no-stacked 
computing test-partition metrics (reporting)
loading canonical_sha256 for 4724960 rows to apply test bucket filter
test bucket: 587932/4724960 rows (12.44%)
cached test bucket mask: /home/t/collimator/out/cache/azoth-test-masks/test-dd1932bd9cc2c50fd0a869b4ec1aee58b89da8430bb493c48672dc6886b02ad7.npz
fitting per-route isotonic calibrators (5-fold CV) over 587932 rows
calibration complete; computing per-filetype metrics
filetypes/xlsb: 0 rows in score table; skipping
computing dev-partition metrics (strategy selection)
loading canonical_sha256 for 4724960 rows to apply dev bucket filter
dev bucket: 588729/4724960 rows (12.46%)
cached dev bucket mask: /home/t/collimator/out/cache/azoth-test-masks/dev-dd1932bd9cc2c50fd0a869b4ec1aee58b89da8430bb493c48672dc6886b02ad7.npz
fitting per-route isotonic calibrators (5-fold CV) over 588729 rows
calibration complete; computing per-filetype metrics
filetypes/xlsb: 0 rows in score table; skipping
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-xml-b5ad85abb46897d5/per_filetype_metrics.json (filetypes: 78, filegroups: 0)
.venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filetypes-xml-b5ad85abb46897d5
staged runtime azoth bundle: /tmp/tmp.oAkn0wENNs
azoth bundle ok: /tmp/tmp.oAkn0wENNs

error: 2 regression(s) over tolerance:
  - unknown: recall@3FP/M dropped 12.37pp (12.37% → 0.00%; tolerance 1.00pp)
  - unknown: PR AUC dropped 0.0233 (0.8282 → 0.8049; tolerance 0.0050)

compared 16 filetypes (mal≥500, ben≥500); 62 below threshold and skipped.

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run.
make[1]: *** [Makefile:1070: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')
