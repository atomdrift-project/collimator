# Promote REJECTED — `503e62be90620231` on `filetypes/jar`

Generated 2026-05-26T23:30:19Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-26T23-27-07_20260526T232651-promote-503e62be90620231_azoth-validate.log; tail: .venv/bin/python scripts/azoth_route_policy_eval.py \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-jar-503e62be90620231/score_table.npz \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filetypes-jar-503e62be90620231/general/threshold_scores.npz \
	--route-policies /home/t/collimator/out/models/azoth-candidate-filetypes-jar-503e62be90620231/route_policies.json \
	--partition test \
	--output-md /home/t/collimator/out/models/azoth-candidate-filetypes-jar-503e62be90620231/route_policy_eval_oof.md \
	--output-json /home/t/collimator/out/models/azoth-candidate-filetypes-jar-503e62be90620231/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-jar-503e62be90620231/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-jar-503e62be90620231/route_policy_eval_oof.md
.venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filetypes-jar-503e62be90620231
staged runtime azoth bundle: /tmp/tmp.Pe8B5jr5QK
azoth bundle ok: /tmp/tmp.Pe8B5jr5QK
--source-bundle out/models/azoth: 1 routes changed → 1 filetypes impacted, 65 unimpacted (drift treated as pre-existing)

ensemble improvements (≥0.10pp):
  xls: L3 hostile ensemble recall +0.31pp (95.22% → 95.53%)

per-route improvements (≥0.10pp, informational):
  java_class :: filetypes/java_class recall@3FP/M +4.07pp (84.30% → 88.37%)

per-route regressions (informational; does not block deploy):
  perl :: filetypes/perl recall@3FP/M dropped 3.70pp (88.89% → 85.19%)
  xml :: filetypes/xml recall@3FP/M dropped 4.45pp (5.82% → 1.37%)

15 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + c: L3 hostile ensemble recall +2.72pp above LWM (10.02% → 12.74%)
  + java_class: L3 hostile ensemble recall +2.89pp above LWM (73.41% → 76.30%)
  + javascript: L3 hostile ensemble recall +8.35pp above LWM (66.20% → 74.55%)
  + lnk: L3 hostile ensemble recall +13.03pp above LWM (48.66% → 61.69%)
  + package.json: L3 hostile ensemble recall +3.79pp above LWM (86.78% → 90.57%)
  + pdf: L3 hostile ensemble recall +1.09pp above LWM (6.41% → 7.50%)
  + pe: L3 hostile ensemble recall +2.21pp above LWM (61.96% → 64.17%)
  + perl: L3 hostile ensemble recall +3.70pp above LWM (77.78% → 81.48%)
  + plist: L3 hostile ensemble recall +1.47pp above LWM (2.94% → 4.41%)
  + png: L3 hostile ensemble recall +3.20pp above LWM (1.07% → 4.26%)
  + powershell: L3 hostile ensemble recall +1.54pp above LWM (29.62% → 31.15%)
  + pptx: L3 hostile ensemble recall +9.09pp above LWM (9.09% → 18.18%)
  + python: L3 hostile ensemble recall +2.05pp above LWM (64.28% → 66.33%)
  + xls: L3 hostile ensemble recall +3.08pp above LWM (92.44% → 95.53%)
  + xml: L3 hostile ensemble recall +4.11pp above LWM (2.74% → 6.85%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - jar: L3 hostile ENSEMBLE recall dropped 5.21pp BELOW LOW-WATER-MARK (57.29% → 52.08%; LWM tolerance 0.90pp)

compared 63 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: low-water-mark gate (0.90pp vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1136: azoth-validate] Error 1)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9986)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `503e62be90620231` | `5f1d5dbe3b1e5ddc` | `58dd188496d1b0a3` |
| PR AUC | 0.9986 | 0.9980 | 0.9983 |
| ROC AUC | 0.9973 | 0.9963 | 0.9967 |
| F1 | 0.9792 | 0.9886 | 0.9722 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-26T23-27-07_20260526T232651-promote-503e62be90620231_azoth-validate.log; tail: .venv/bin/python scripts/azoth_route_policy_eval.py \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-jar-503e62be90620231/score_table.npz \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filetypes-jar-503e62be90620231/general/threshold_scores.npz \
	--route-policies /home/t/collimator/out/models/azoth-candidate-filetypes-jar-503e62be90620231/route_policies.json \
	--partition test \
	--output-md /home/t/collimator/out/models/azoth-candidate-filetypes-jar-503e62be90620231/route_policy_eval_oof.md \
	--output-json /home/t/collimator/out/models/azoth-candidate-filetypes-jar-503e62be90620231/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-jar-503e62be90620231/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-jar-503e62be90620231/route_policy_eval_oof.md
.venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filetypes-jar-503e62be90620231
staged runtime azoth bundle: /tmp/tmp.Pe8B5jr5QK
azoth bundle ok: /tmp/tmp.Pe8B5jr5QK
--source-bundle out/models/azoth: 1 routes changed → 1 filetypes impacted, 65 unimpacted (drift treated as pre-existing)

ensemble improvements (≥0.10pp):
  xls: L3 hostile ensemble recall +0.31pp (95.22% → 95.53%)

per-route improvements (≥0.10pp, informational):
  java_class :: filetypes/java_class recall@3FP/M +4.07pp (84.30% → 88.37%)

per-route regressions (informational; does not block deploy):
  perl :: filetypes/perl recall@3FP/M dropped 3.70pp (88.89% → 85.19%)
  xml :: filetypes/xml recall@3FP/M dropped 4.45pp (5.82% → 1.37%)

15 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + c: L3 hostile ensemble recall +2.72pp above LWM (10.02% → 12.74%)
  + java_class: L3 hostile ensemble recall +2.89pp above LWM (73.41% → 76.30%)
  + javascript: L3 hostile ensemble recall +8.35pp above LWM (66.20% → 74.55%)
  + lnk: L3 hostile ensemble recall +13.03pp above LWM (48.66% → 61.69%)
  + package.json: L3 hostile ensemble recall +3.79pp above LWM (86.78% → 90.57%)
  + pdf: L3 hostile ensemble recall +1.09pp above LWM (6.41% → 7.50%)
  + pe: L3 hostile ensemble recall +2.21pp above LWM (61.96% → 64.17%)
  + perl: L3 hostile ensemble recall +3.70pp above LWM (77.78% → 81.48%)
  + plist: L3 hostile ensemble recall +1.47pp above LWM (2.94% → 4.41%)
  + png: L3 hostile ensemble recall +3.20pp above LWM (1.07% → 4.26%)
  + powershell: L3 hostile ensemble recall +1.54pp above LWM (29.62% → 31.15%)
  + pptx: L3 hostile ensemble recall +9.09pp above LWM (9.09% → 18.18%)
  + python: L3 hostile ensemble recall +2.05pp above LWM (64.28% → 66.33%)
  + xls: L3 hostile ensemble recall +3.08pp above LWM (92.44% → 95.53%)
  + xml: L3 hostile ensemble recall +4.11pp above LWM (2.74% → 6.85%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - jar: L3 hostile ENSEMBLE recall dropped 5.21pp BELOW LOW-WATER-MARK (57.29% → 52.08%; LWM tolerance 0.90pp)

compared 63 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: low-water-mark gate (0.90pp vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1136: azoth-validate] Error 1)
