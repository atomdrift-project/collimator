# Promote REJECTED — `95897481f565eef2` on `filetypes/xml`

Generated 2026-05-20T08:22:35Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-20T08-18-07_20260520T081758-promote-95897481f565eef2_azoth-validate.log; tail: .venv/bin/python scripts/azoth_policy_global_metrics.py \
	--config /home/t/collimator/out/models/azoth-candidate-filetypes-xml-95897481f565eef2/config.json \
	--policy /home/t/collimator/out/models/azoth-candidate-filetypes-xml-95897481f565eef2/route_policies.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-xml-95897481f565eef2/score_table.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-xml-95897481f565eef2/global_policy_metrics.json \
	--markdown /home/t/collimator/out/models/azoth-candidate-filetypes-xml-95897481f565eef2/global_policy_metrics.md \
	--fail-on-budget
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-xml-95897481f565eef2/global_policy_metrics.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-xml-95897481f565eef2/global_policy_metrics.md
.venv/bin/python scripts/compute_routed_metrics.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filetypes-xml-95897481f565eef2 --db postgres://hopper@localhost:5432/hopper --no-ci --no-stacked 
computing test-partition metrics (reporting)
loaded cached test-bucket mask: /home/t/collimator/out/cache/azoth-test-masks/test-5fbe877e32cf00452d21320909bf25270d1a40d7a34297eadbb67b0f69075d35.npz
test bucket: 587975/4725221 rows (12.44%)
fitting per-route isotonic calibrators (5-fold CV) over 587975 rows
calibration complete; computing per-filetype metrics
filetypes/xlsb: 0 rows in score table; skipping
computing dev-partition metrics (strategy selection)
loaded cached dev-bucket mask: /home/t/collimator/out/cache/azoth-test-masks/dev-5fbe877e32cf00452d21320909bf25270d1a40d7a34297eadbb67b0f69075d35.npz
dev bucket: 588763/4725221 rows (12.46%)
fitting per-route isotonic calibrators (5-fold CV) over 588763 rows
calibration complete; computing per-filetype metrics
filetypes/xlsb: 0 rows in score table; skipping
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-xml-95897481f565eef2/per_filetype_metrics.json (filetypes: 78, filegroups: 0)
.venv/bin/python scripts/azoth_route_policy_eval.py \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-xml-95897481f565eef2/score_table.npz \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filetypes-xml-95897481f565eef2/general/threshold_scores.npz \
	--route-policies /home/t/collimator/out/models/azoth-candidate-filetypes-xml-95897481f565eef2/route_policies.json \
	--partition test \
	--output-md /home/t/collimator/out/models/azoth-candidate-filetypes-xml-95897481f565eef2/route_policy_eval_oof.md \
	--output-json /home/t/collimator/out/models/azoth-candidate-filetypes-xml-95897481f565eef2/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-xml-95897481f565eef2/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-xml-95897481f565eef2/route_policy_eval_oof.md
.venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filetypes-xml-95897481f565eef2
staged runtime azoth bundle: /tmp/tmp.TXOdbY5UBT
azoth bundle ok: /tmp/tmp.TXOdbY5UBT

error: 7 regression(s) over tolerance:
  - elf: L3 hostile recall dropped 5.19pp (94.84% → 89.65%; tolerance 1.00pp)
  - package.json: L3 hostile recall dropped 1.71pp (92.65% → 90.94%; tolerance 1.00pp)
  - pe: L3 hostile recall dropped 2.08pp (69.97% → 67.89%; tolerance 1.00pp)
  - php: L3 hostile recall dropped 1.37pp (51.27% → 49.90%; tolerance 1.00pp)
  - python: L3 hostile recall dropped 7.74pp (56.40% → 48.66%; tolerance 1.00pp)
  - tar.gz: L3 hostile recall dropped 3.55pp (58.52% → 54.96%; tolerance 1.00pp)
  - zip: L3 hostile recall dropped 2.08pp (45.25% → 43.18%; tolerance 1.00pp)

compared 16 filetypes (mal≥500, ben≥500); 49 below threshold and skipped.

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run.
make[1]: *** [Makefile:1071: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 1.0000)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `95897481f565eef2` | `1613538c79043b94` | `2cf73f89349fc8cf` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 1.0000 | 1.0000 | 1.0000 |
| F1 | 0.9630 | 1.0000 | 1.0000 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-20T08-18-07_20260520T081758-promote-95897481f565eef2_azoth-validate.log; tail: .venv/bin/python scripts/azoth_policy_global_metrics.py \
	--config /home/t/collimator/out/models/azoth-candidate-filetypes-xml-95897481f565eef2/config.json \
	--policy /home/t/collimator/out/models/azoth-candidate-filetypes-xml-95897481f565eef2/route_policies.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-xml-95897481f565eef2/score_table.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-xml-95897481f565eef2/global_policy_metrics.json \
	--markdown /home/t/collimator/out/models/azoth-candidate-filetypes-xml-95897481f565eef2/global_policy_metrics.md \
	--fail-on-budget
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-xml-95897481f565eef2/global_policy_metrics.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-xml-95897481f565eef2/global_policy_metrics.md
.venv/bin/python scripts/compute_routed_metrics.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filetypes-xml-95897481f565eef2 --db postgres://hopper@localhost:5432/hopper --no-ci --no-stacked 
computing test-partition metrics (reporting)
loaded cached test-bucket mask: /home/t/collimator/out/cache/azoth-test-masks/test-5fbe877e32cf00452d21320909bf25270d1a40d7a34297eadbb67b0f69075d35.npz
test bucket: 587975/4725221 rows (12.44%)
fitting per-route isotonic calibrators (5-fold CV) over 587975 rows
calibration complete; computing per-filetype metrics
filetypes/xlsb: 0 rows in score table; skipping
computing dev-partition metrics (strategy selection)
loaded cached dev-bucket mask: /home/t/collimator/out/cache/azoth-test-masks/dev-5fbe877e32cf00452d21320909bf25270d1a40d7a34297eadbb67b0f69075d35.npz
dev bucket: 588763/4725221 rows (12.46%)
fitting per-route isotonic calibrators (5-fold CV) over 588763 rows
calibration complete; computing per-filetype metrics
filetypes/xlsb: 0 rows in score table; skipping
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-xml-95897481f565eef2/per_filetype_metrics.json (filetypes: 78, filegroups: 0)
.venv/bin/python scripts/azoth_route_policy_eval.py \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-xml-95897481f565eef2/score_table.npz \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filetypes-xml-95897481f565eef2/general/threshold_scores.npz \
	--route-policies /home/t/collimator/out/models/azoth-candidate-filetypes-xml-95897481f565eef2/route_policies.json \
	--partition test \
	--output-md /home/t/collimator/out/models/azoth-candidate-filetypes-xml-95897481f565eef2/route_policy_eval_oof.md \
	--output-json /home/t/collimator/out/models/azoth-candidate-filetypes-xml-95897481f565eef2/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-xml-95897481f565eef2/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-xml-95897481f565eef2/route_policy_eval_oof.md
.venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filetypes-xml-95897481f565eef2
staged runtime azoth bundle: /tmp/tmp.TXOdbY5UBT
azoth bundle ok: /tmp/tmp.TXOdbY5UBT

error: 7 regression(s) over tolerance:
  - elf: L3 hostile recall dropped 5.19pp (94.84% → 89.65%; tolerance 1.00pp)
  - package.json: L3 hostile recall dropped 1.71pp (92.65% → 90.94%; tolerance 1.00pp)
  - pe: L3 hostile recall dropped 2.08pp (69.97% → 67.89%; tolerance 1.00pp)
  - php: L3 hostile recall dropped 1.37pp (51.27% → 49.90%; tolerance 1.00pp)
  - python: L3 hostile recall dropped 7.74pp (56.40% → 48.66%; tolerance 1.00pp)
  - tar.gz: L3 hostile recall dropped 3.55pp (58.52% → 54.96%; tolerance 1.00pp)
  - zip: L3 hostile recall dropped 2.08pp (45.25% → 43.18%; tolerance 1.00pp)

compared 16 filetypes (mal≥500, ben≥500); 49 below threshold and skipped.

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run.
make[1]: *** [Makefile:1071: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')
