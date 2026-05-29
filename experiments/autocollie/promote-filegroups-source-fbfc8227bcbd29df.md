# Promote REJECTED — `fbfc8227bcbd29df` on `filegroups/source`

Generated 2026-05-26T03:39:12Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-26T03-32-49_20260526T033135-promote-fbfc8227bcbd29df_azoth-validate.log; tail: 	--output-md /home/t/collimator/out/models/azoth-candidate-filegroups-source-fbfc8227bcbd29df/route_policy_eval_oof.md \
	--output-json /home/t/collimator/out/models/azoth-candidate-filegroups-source-fbfc8227bcbd29df/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-source-fbfc8227bcbd29df/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-source-fbfc8227bcbd29df/route_policy_eval_oof.md
.venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filegroups-source-fbfc8227bcbd29df
staged runtime azoth bundle: /tmp/tmp.8UwvsTklZO
azoth bundle ok: /tmp/tmp.8UwvsTklZO
--source-bundle out/models/azoth: 1 routes changed → 7 filetypes impacted, 59 unimpacted (drift treated as pre-existing)

ensemble improvements (≥0.10pp):
  c: L3 hostile ensemble recall +0.68pp (11.33% → 12.00%)
  csharp: L3 hostile ensemble recall +0.43pp (25.21% → 25.64%)
  go: L3 hostile ensemble recall +0.17pp (1.27% → 1.44%)
  kotlin: L3 hostile ensemble recall +6.06pp (52.67% → 58.73%)
  rust: L3 hostile ensemble recall +0.61pp (1.22% → 1.83%)

per-route improvements (≥0.10pp, informational):
  c :: filegroups/source recall@3FP/M +0.11pp (13.36% → 13.48%)
  go :: filegroups/source recall@3FP/M +0.42pp (2.29% → 2.72%)
  rust :: filegroups/source recall@3FP/M +0.61pp (3.05% → 3.66%)

per-route regressions (informational; does not block deploy):
  csharp :: filegroups/source recall@3FP/M dropped 3.42pp (32.05% → 28.63%)
  kotlin :: filegroups/source recall@3FP/M dropped 7.03pp (72.06% → 65.04%)

14 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + c: L3 hostile ensemble recall +1.98pp above LWM (10.02% → 12.00%)
  + java_class: L3 hostile ensemble recall +2.89pp above LWM (73.41% → 76.30%)
  + javascript: L3 hostile ensemble recall +5.92pp above LWM (66.20% → 72.12%)
  + kotlin: L3 hostile ensemble recall +6.06pp above LWM (52.67% → 58.73%)
  + lnk: L3 hostile ensemble recall +13.03pp above LWM (48.66% → 61.69%)
  + package.json: L3 hostile ensemble recall +4.35pp above LWM (86.78% → 91.12%)
  + pdf: L3 hostile ensemble recall +1.09pp above LWM (6.41% → 7.50%)
  + perl: L3 hostile ensemble recall +7.41pp above LWM (77.78% → 85.19%)
  + png: L3 hostile ensemble recall +3.20pp above LWM (1.07% → 4.26%)
  + powershell: L3 hostile ensemble recall +1.54pp above LWM (29.62% → 31.15%)
  + pptx: L3 hostile ensemble recall +9.09pp above LWM (9.09% → 18.18%)
  + python: L3 hostile ensemble recall +2.05pp above LWM (64.28% → 66.33%)
  + xls: L3 hostile ensemble recall +2.78pp above LWM (92.44% → 95.22%)
  + xml: L3 hostile ensemble recall +8.22pp above LWM (2.74% → 10.96%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - java: L3 hostile ENSEMBLE recall dropped 25.00pp BELOW LOW-WATER-MARK (50.00% → 25.00%; LWM tolerance 0.90pp)

compared 63 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: low-water-mark gate (0.90pp vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1136: azoth-validate] Error 1)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9988)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `fbfc8227bcbd29df` | `67e067b1490da1f1` | `5091314d10ee3059` |
| PR AUC | 0.9988 | 0.9993 | 0.9993 |
| ROC AUC | 0.9982 | 0.9986 | 0.9986 |
| F1 | 0.9828 | 0.9823 | 0.9817 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-26T03-32-49_20260526T033135-promote-fbfc8227bcbd29df_azoth-validate.log; tail: 	--output-md /home/t/collimator/out/models/azoth-candidate-filegroups-source-fbfc8227bcbd29df/route_policy_eval_oof.md \
	--output-json /home/t/collimator/out/models/azoth-candidate-filegroups-source-fbfc8227bcbd29df/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-source-fbfc8227bcbd29df/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-source-fbfc8227bcbd29df/route_policy_eval_oof.md
.venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filegroups-source-fbfc8227bcbd29df
staged runtime azoth bundle: /tmp/tmp.8UwvsTklZO
azoth bundle ok: /tmp/tmp.8UwvsTklZO
--source-bundle out/models/azoth: 1 routes changed → 7 filetypes impacted, 59 unimpacted (drift treated as pre-existing)

ensemble improvements (≥0.10pp):
  c: L3 hostile ensemble recall +0.68pp (11.33% → 12.00%)
  csharp: L3 hostile ensemble recall +0.43pp (25.21% → 25.64%)
  go: L3 hostile ensemble recall +0.17pp (1.27% → 1.44%)
  kotlin: L3 hostile ensemble recall +6.06pp (52.67% → 58.73%)
  rust: L3 hostile ensemble recall +0.61pp (1.22% → 1.83%)

per-route improvements (≥0.10pp, informational):
  c :: filegroups/source recall@3FP/M +0.11pp (13.36% → 13.48%)
  go :: filegroups/source recall@3FP/M +0.42pp (2.29% → 2.72%)
  rust :: filegroups/source recall@3FP/M +0.61pp (3.05% → 3.66%)

per-route regressions (informational; does not block deploy):
  csharp :: filegroups/source recall@3FP/M dropped 3.42pp (32.05% → 28.63%)
  kotlin :: filegroups/source recall@3FP/M dropped 7.03pp (72.06% → 65.04%)

14 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + c: L3 hostile ensemble recall +1.98pp above LWM (10.02% → 12.00%)
  + java_class: L3 hostile ensemble recall +2.89pp above LWM (73.41% → 76.30%)
  + javascript: L3 hostile ensemble recall +5.92pp above LWM (66.20% → 72.12%)
  + kotlin: L3 hostile ensemble recall +6.06pp above LWM (52.67% → 58.73%)
  + lnk: L3 hostile ensemble recall +13.03pp above LWM (48.66% → 61.69%)
  + package.json: L3 hostile ensemble recall +4.35pp above LWM (86.78% → 91.12%)
  + pdf: L3 hostile ensemble recall +1.09pp above LWM (6.41% → 7.50%)
  + perl: L3 hostile ensemble recall +7.41pp above LWM (77.78% → 85.19%)
  + png: L3 hostile ensemble recall +3.20pp above LWM (1.07% → 4.26%)
  + powershell: L3 hostile ensemble recall +1.54pp above LWM (29.62% → 31.15%)
  + pptx: L3 hostile ensemble recall +9.09pp above LWM (9.09% → 18.18%)
  + python: L3 hostile ensemble recall +2.05pp above LWM (64.28% → 66.33%)
  + xls: L3 hostile ensemble recall +2.78pp above LWM (92.44% → 95.22%)
  + xml: L3 hostile ensemble recall +8.22pp above LWM (2.74% → 10.96%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - java: L3 hostile ENSEMBLE recall dropped 25.00pp BELOW LOW-WATER-MARK (50.00% → 25.00%; LWM tolerance 0.90pp)

compared 63 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: low-water-mark gate (0.90pp vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1136: azoth-validate] Error 1)
