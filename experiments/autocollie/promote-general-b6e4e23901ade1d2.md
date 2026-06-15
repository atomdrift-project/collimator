# Promote REJECTED — `b6e4e23901ade1d2` on `general`

Generated 2026-06-15T09:35:31Z

azoth-validate failed: signal: terminated (log /home/t/collimator/out/autocollie/runs/2026-06-15T09-25-12_20260615T091107-promote-b6e4e23901ade1d2_azoth-validate.log; tail: 2026-06-15 05:26:42,741 INFO azoth_calibrate_ensemble: filetypes/xml: using cached scores
2026-06-15 05:26:42,862 INFO azoth_calibrate_ensemble: filetypes/python: using cached scores
2026-06-15 05:26:43,015 INFO azoth_calibrate_ensemble: filetypes/pdf: using cached scores
2026-06-15 05:26:43,151 INFO azoth_calibrate_ensemble: filetypes/png: using cached scores
2026-06-15 05:26:43,286 INFO azoth_calibrate_ensemble: filetypes/batch: using cached scores
2026-06-15 05:26:43,420 INFO azoth_calibrate_ensemble: filetypes/php: using cached scores
2026-06-15 05:26:43,565 INFO azoth_calibrate_ensemble: filetypes/go: using cached scores
2026-06-15 05:26:43,723 INFO azoth_calibrate_ensemble: filetypes/text: using cached scores
2026-06-15 05:26:43,870 INFO azoth_calibrate_ensemble: filetypes/zip: using cached scores
2026-06-15 05:26:44,004 INFO azoth_calibrate_ensemble: filetypes/rust: using cached scores
2026-06-15 05:26:44,142 INFO azoth_calibrate_ensemble: filetypes/kotlin: using cached scores
2026-06-15 05:26:44,293 INFO azoth_calibrate_ensemble: filetypes/java: using cached scores
2026-06-15 05:26:44,433 INFO azoth_calibrate_ensemble: filetypes/shell: using cached scores
2026-06-15 05:26:44,562 INFO azoth_calibrate_ensemble: filetypes/csharp: using cached scores
2026-06-15 05:26:44,690 INFO azoth_calibrate_ensemble: filetypes/tar: using cached scores
2026-06-15 05:26:44,838 INFO azoth_calibrate_ensemble: filetypes/xlsx: using cached scores
2026-06-15 05:26:44,949 INFO azoth_calibrate_ensemble: filetypes/xls: using cached scores
2026-06-15 05:26:45,085 INFO azoth_calibrate_ensemble: filetypes/perl: using cached scores
2026-06-15 05:26:45,211 INFO azoth_calibrate_ensemble: filetypes/package.json: using cached scores
2026-06-15 05:26:45,315 INFO azoth_calibrate_ensemble: filetypes/makefile: using cached scores
2026-06-15 05:26:45,316 WARNING azoth_calibrate_ensemble: filegroups/native: skipped 24 rows absent from general score cache
2026-06-15 05:26:45,482 INFO azoth_calibrate_ensemble: filetypes/jpeg: using cached scores
2026-06-15 05:26:45,602 INFO azoth_calibrate_ensemble: filetypes/ruby: using cached scores
2026-06-15 05:26:45,624 INFO collimator.features: DB-backed feature extraction: 1929026 rows, 8 workers, batch_size=1024
2026-06-15 05:26:45,759 INFO azoth_calibrate_ensemble: filetypes/objc: using cached scores
2026-06-15 05:26:46,035 INFO azoth_calibrate_ensemble: filetypes/lua: using cached scores
2026-06-15 05:26:46,072 INFO azoth_calibrate_ensemble: filetypes/html: using cached scores
2026-06-15 05:26:46,317 INFO azoth_calibrate_ensemble: filetypes/macho: using cached scores
2026-06-15 05:26:46,499 INFO azoth_calibrate_ensemble: filetypes/vbs: using cached scores
2026-06-15 05:26:46,697 INFO azoth_calibrate_ensemble: filetypes/ole: using cached scores
2026-06-15 05:26:46,857 INFO azoth_calibrate_ensemble: filetypes/plist: using cached scores
2026-06-15 05:26:46,995 INFO azoth_calibrate_ensemble: filetypes/pkg-info: using cached scores
2026-06-15 05:26:47,188 INFO azoth_calibrate_ensemble: filetypes/powershell: using cached scores
2026-06-15 05:26:47,310 INFO azoth_calibrate_ensemble: filetypes/deb: using cached scores
2026-06-15 05:26:47,474 INFO azoth_calibrate_ensemble: filetypes/jar: using cached scores
2026-06-15 05:26:47,641 INFO azoth_calibrate_ensemble: filetypes/groovy: using cached scores
2026-06-15 05:26:47,871 INFO azoth_calibrate_ensemble: filetypes/rtf: using cached scores
2026-06-15 05:26:48,006 INFO azoth_calibrate_ensemble: filetypes/clojure: using cached scores
2026-06-15 05:26:48,154 INFO azoth_calibrate_ensemble: filetypes/msi: using cached scores
2026-06-15 05:26:48,277 INFO azoth_calibrate_ensemble: filetypes/lnk: using cached scores
2026-06-15 05:26:48,454 INFO azoth_calibrate_ensemble: filetypes/docx: using cached scores
2026-06-15 05:26:48,619 INFO azoth_calibrate_ensemble: filetypes/whl: using cached scores
2026-06-15 05:26:48,817 INFO azoth_calibrate_ensemble: filetypes/dockerfile: using cached scores
2026-06-15 05:26:49,021 INFO azoth_calibrate_ensemble: filetypes/cargo.toml: using cached scores
2026-06-15 05:26:49,129 INFO azoth_calibrate_ensemble: filetypes/npm: using cached scores
2026-06-15 05:26:49,229 INFO azoth_calibrate_ensemble: filetypes/crx: using cached scores
2026-06-15 05:26:49,423 INFO azoth_calibrate_ensemble: filetypes/gem: using cached scores
2026-06-15 05:26:49,550 INFO azoth_calibrate_ensemble: filetypes/chrome-manifest: using cached scores
2026-06-15 05:26:49,642 INFO azoth_calibrate_ensemble: filetypes/applescript: using cached scores
make[1]: *** [Makefile:1205: azoth-calibrate] Terminated)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9979)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `b6e4e23901ade1d2` | `7c051c49ad19816e` | `91da862f9c7deb64` |
| PR AUC | 0.9979 | 0.9998 | 0.9993 |
| ROC AUC | 0.9978 | 0.9993 | 0.9993 |
| F1 | 0.9806 | 0.9939 | 0.9894 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: signal: terminated (log /home/t/collimator/out/autocollie/runs/2026-06-15T09-25-12_20260615T091107-promote-b6e4e23901ade1d2_azoth-validate.log; tail: 2026-06-15 05:26:42,741 INFO azoth_calibrate_ensemble: filetypes/xml: using cached scores
2026-06-15 05:26:42,862 INFO azoth_calibrate_ensemble: filetypes/python: using cached scores
2026-06-15 05:26:43,015 INFO azoth_calibrate_ensemble: filetypes/pdf: using cached scores
2026-06-15 05:26:43,151 INFO azoth_calibrate_ensemble: filetypes/png: using cached scores
2026-06-15 05:26:43,286 INFO azoth_calibrate_ensemble: filetypes/batch: using cached scores
2026-06-15 05:26:43,420 INFO azoth_calibrate_ensemble: filetypes/php: using cached scores
2026-06-15 05:26:43,565 INFO azoth_calibrate_ensemble: filetypes/go: using cached scores
2026-06-15 05:26:43,723 INFO azoth_calibrate_ensemble: filetypes/text: using cached scores
2026-06-15 05:26:43,870 INFO azoth_calibrate_ensemble: filetypes/zip: using cached scores
2026-06-15 05:26:44,004 INFO azoth_calibrate_ensemble: filetypes/rust: using cached scores
2026-06-15 05:26:44,142 INFO azoth_calibrate_ensemble: filetypes/kotlin: using cached scores
2026-06-15 05:26:44,293 INFO azoth_calibrate_ensemble: filetypes/java: using cached scores
2026-06-15 05:26:44,433 INFO azoth_calibrate_ensemble: filetypes/shell: using cached scores
2026-06-15 05:26:44,562 INFO azoth_calibrate_ensemble: filetypes/csharp: using cached scores
2026-06-15 05:26:44,690 INFO azoth_calibrate_ensemble: filetypes/tar: using cached scores
2026-06-15 05:26:44,838 INFO azoth_calibrate_ensemble: filetypes/xlsx: using cached scores
2026-06-15 05:26:44,949 INFO azoth_calibrate_ensemble: filetypes/xls: using cached scores
2026-06-15 05:26:45,085 INFO azoth_calibrate_ensemble: filetypes/perl: using cached scores
2026-06-15 05:26:45,211 INFO azoth_calibrate_ensemble: filetypes/package.json: using cached scores
2026-06-15 05:26:45,315 INFO azoth_calibrate_ensemble: filetypes/makefile: using cached scores
2026-06-15 05:26:45,316 WARNING azoth_calibrate_ensemble: filegroups/native: skipped 24 rows absent from general score cache
2026-06-15 05:26:45,482 INFO azoth_calibrate_ensemble: filetypes/jpeg: using cached scores
2026-06-15 05:26:45,602 INFO azoth_calibrate_ensemble: filetypes/ruby: using cached scores
2026-06-15 05:26:45,624 INFO collimator.features: DB-backed feature extraction: 1929026 rows, 8 workers, batch_size=1024
2026-06-15 05:26:45,759 INFO azoth_calibrate_ensemble: filetypes/objc: using cached scores
2026-06-15 05:26:46,035 INFO azoth_calibrate_ensemble: filetypes/lua: using cached scores
2026-06-15 05:26:46,072 INFO azoth_calibrate_ensemble: filetypes/html: using cached scores
2026-06-15 05:26:46,317 INFO azoth_calibrate_ensemble: filetypes/macho: using cached scores
2026-06-15 05:26:46,499 INFO azoth_calibrate_ensemble: filetypes/vbs: using cached scores
2026-06-15 05:26:46,697 INFO azoth_calibrate_ensemble: filetypes/ole: using cached scores
2026-06-15 05:26:46,857 INFO azoth_calibrate_ensemble: filetypes/plist: using cached scores
2026-06-15 05:26:46,995 INFO azoth_calibrate_ensemble: filetypes/pkg-info: using cached scores
2026-06-15 05:26:47,188 INFO azoth_calibrate_ensemble: filetypes/powershell: using cached scores
2026-06-15 05:26:47,310 INFO azoth_calibrate_ensemble: filetypes/deb: using cached scores
2026-06-15 05:26:47,474 INFO azoth_calibrate_ensemble: filetypes/jar: using cached scores
2026-06-15 05:26:47,641 INFO azoth_calibrate_ensemble: filetypes/groovy: using cached scores
2026-06-15 05:26:47,871 INFO azoth_calibrate_ensemble: filetypes/rtf: using cached scores
2026-06-15 05:26:48,006 INFO azoth_calibrate_ensemble: filetypes/clojure: using cached scores
2026-06-15 05:26:48,154 INFO azoth_calibrate_ensemble: filetypes/msi: using cached scores
2026-06-15 05:26:48,277 INFO azoth_calibrate_ensemble: filetypes/lnk: using cached scores
2026-06-15 05:26:48,454 INFO azoth_calibrate_ensemble: filetypes/docx: using cached scores
2026-06-15 05:26:48,619 INFO azoth_calibrate_ensemble: filetypes/whl: using cached scores
2026-06-15 05:26:48,817 INFO azoth_calibrate_ensemble: filetypes/dockerfile: using cached scores
2026-06-15 05:26:49,021 INFO azoth_calibrate_ensemble: filetypes/cargo.toml: using cached scores
2026-06-15 05:26:49,129 INFO azoth_calibrate_ensemble: filetypes/npm: using cached scores
2026-06-15 05:26:49,229 INFO azoth_calibrate_ensemble: filetypes/crx: using cached scores
2026-06-15 05:26:49,423 INFO azoth_calibrate_ensemble: filetypes/gem: using cached scores
2026-06-15 05:26:49,550 INFO azoth_calibrate_ensemble: filetypes/chrome-manifest: using cached scores
2026-06-15 05:26:49,642 INFO azoth_calibrate_ensemble: filetypes/applescript: using cached scores
make[1]: *** [Makefile:1205: azoth-calibrate] Terminated)
