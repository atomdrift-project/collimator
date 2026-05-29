# Promote REJECTED — `06d781a562bc7f81` on `filetypes/lnk`

Generated 2026-05-26T23:26:39Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-26T23-23-28_20260526T232321-promote-06d781a562bc7f81_azoth-validate.log; tail: .venv/bin/python scripts/azoth_route_policy_eval.py \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-lnk-06d781a562bc7f81/score_table.npz \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filetypes-lnk-06d781a562bc7f81/general/threshold_scores.npz \
	--route-policies /home/t/collimator/out/models/azoth-candidate-filetypes-lnk-06d781a562bc7f81/route_policies.json \
	--partition test \
	--output-md /home/t/collimator/out/models/azoth-candidate-filetypes-lnk-06d781a562bc7f81/route_policy_eval_oof.md \
	--output-json /home/t/collimator/out/models/azoth-candidate-filetypes-lnk-06d781a562bc7f81/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-lnk-06d781a562bc7f81/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-lnk-06d781a562bc7f81/route_policy_eval_oof.md
.venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filetypes-lnk-06d781a562bc7f81
staged runtime azoth bundle: /tmp/tmp.jXa5iCOzGK
azoth bundle ok: /tmp/tmp.jXa5iCOzGK
--source-bundle out/models/azoth: 1 routes changed → 1 filetypes impacted, 65 unimpacted (drift treated as pre-existing)

ensemble improvements (≥0.10pp):
  xls: L3 hostile ensemble recall +0.31pp (95.22% → 95.53%)

per-route improvements (≥0.10pp, informational):
  java_class :: filetypes/java_class recall@3FP/M +4.07pp (84.30% → 88.37%)

per-route regressions (informational; does not block deploy):
  lnk :: filetypes/lnk recall@3FP/M dropped 9.23pp (58.85% → 49.62%)
  perl :: filetypes/perl recall@3FP/M dropped 3.70pp (88.89% → 85.19%)
  xml :: filetypes/xml recall@3FP/M dropped 4.45pp (5.82% → 1.37%)

14 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + c: L3 hostile ensemble recall +2.72pp above LWM (10.02% → 12.74%)
  + java_class: L3 hostile ensemble recall +2.89pp above LWM (73.41% → 76.30%)
  + javascript: L3 hostile ensemble recall +8.35pp above LWM (66.20% → 74.55%)
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
  - lnk: L3 hostile ENSEMBLE recall dropped 2.68pp BELOW LOW-WATER-MARK (48.66% → 45.98%; LWM tolerance 0.90pp)

compared 63 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: deployed-tolerance gate (1.70pp), low-water-mark gate (0.90pp vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1136: azoth-validate] Error 1)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9989)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `06d781a562bc7f81` | `0dd4d9bb34b145b3` | `9560b476450bfa1c` |
| PR AUC | 0.9989 | 0.9990 | 0.9990 |
| ROC AUC | 0.9858 | 0.9870 | 0.9863 |
| F1 | 0.9843 | 0.9848 | 0.9848 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-26T23-23-28_20260526T232321-promote-06d781a562bc7f81_azoth-validate.log; tail: .venv/bin/python scripts/azoth_route_policy_eval.py \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-lnk-06d781a562bc7f81/score_table.npz \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filetypes-lnk-06d781a562bc7f81/general/threshold_scores.npz \
	--route-policies /home/t/collimator/out/models/azoth-candidate-filetypes-lnk-06d781a562bc7f81/route_policies.json \
	--partition test \
	--output-md /home/t/collimator/out/models/azoth-candidate-filetypes-lnk-06d781a562bc7f81/route_policy_eval_oof.md \
	--output-json /home/t/collimator/out/models/azoth-candidate-filetypes-lnk-06d781a562bc7f81/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-lnk-06d781a562bc7f81/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-lnk-06d781a562bc7f81/route_policy_eval_oof.md
.venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filetypes-lnk-06d781a562bc7f81
staged runtime azoth bundle: /tmp/tmp.jXa5iCOzGK
azoth bundle ok: /tmp/tmp.jXa5iCOzGK
--source-bundle out/models/azoth: 1 routes changed → 1 filetypes impacted, 65 unimpacted (drift treated as pre-existing)

ensemble improvements (≥0.10pp):
  xls: L3 hostile ensemble recall +0.31pp (95.22% → 95.53%)

per-route improvements (≥0.10pp, informational):
  java_class :: filetypes/java_class recall@3FP/M +4.07pp (84.30% → 88.37%)

per-route regressions (informational; does not block deploy):
  lnk :: filetypes/lnk recall@3FP/M dropped 9.23pp (58.85% → 49.62%)
  perl :: filetypes/perl recall@3FP/M dropped 3.70pp (88.89% → 85.19%)
  xml :: filetypes/xml recall@3FP/M dropped 4.45pp (5.82% → 1.37%)

14 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + c: L3 hostile ensemble recall +2.72pp above LWM (10.02% → 12.74%)
  + java_class: L3 hostile ensemble recall +2.89pp above LWM (73.41% → 76.30%)
  + javascript: L3 hostile ensemble recall +8.35pp above LWM (66.20% → 74.55%)
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
  - lnk: L3 hostile ENSEMBLE recall dropped 2.68pp BELOW LOW-WATER-MARK (48.66% → 45.98%; LWM tolerance 0.90pp)

compared 63 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: deployed-tolerance gate (1.70pp), low-water-mark gate (0.90pp vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1136: azoth-validate] Error 1)
