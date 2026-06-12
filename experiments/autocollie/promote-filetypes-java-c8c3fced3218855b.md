# Promote REJECTED — `c8c3fced3218855b` on `filetypes/java`

Generated 2026-06-10T10:34:41Z

azoth-validate failed: signal: terminated (log /home/t/collimator/out/autocollie/runs/2026-06-10T10-33-43_20260610T103342-promote-c8c3fced3218855b_azoth-validate.log; tail: 2026-06-10 06:34:17,599 INFO azoth_calibrate_ensemble: filetypes/python: using cached scores
2026-06-10 06:34:18,318 INFO azoth_calibrate_ensemble: filetypes/xml: using cached scores
2026-06-10 06:34:18,370 INFO azoth_calibrate_ensemble: filetypes/pdf: using cached scores
2026-06-10 06:34:18,692 INFO azoth_calibrate_ensemble: filetypes/python-bytecode: using cached scores
2026-06-10 06:34:18,955 INFO azoth_calibrate_ensemble: filetypes/png: using cached scores
2026-06-10 06:34:19,088 INFO azoth_calibrate_ensemble: filetypes/batch: using cached scores
2026-06-10 06:34:19,301 INFO azoth_calibrate_ensemble: filetypes/php: using cached scores
2026-06-10 06:34:19,531 INFO azoth_calibrate_ensemble: filetypes/go: using cached scores
2026-06-10 06:34:20,284 INFO azoth_calibrate_ensemble: filetypes/text: using cached scores
2026-06-10 06:34:20,921 INFO azoth_calibrate_ensemble: filetypes/rust: using cached scores
2026-06-10 06:34:21,003 INFO azoth_calibrate_ensemble: filetypes/zip: using cached scores
2026-06-10 06:34:22,450 INFO azoth_calibrate_ensemble: filetypes/kotlin: using cached scores
2026-06-10 06:34:22,504 INFO azoth_calibrate_ensemble: filetypes/java: route artifacts changed; refreshing score cache
2026-06-10 06:34:23,019 INFO azoth_calibrate_ensemble: filetypes/csharp: using cached scores
2026-06-10 06:34:23,032 INFO azoth_calibrate_ensemble: filetypes/shell: using cached scores
2026-06-10 06:34:23,220 INFO azoth_calibrate_ensemble: filetypes/xlsx: using cached scores
2026-06-10 06:34:23,478 INFO azoth_calibrate_ensemble: filetypes/xls: using cached scores
2026-06-10 06:34:23,931 INFO azoth_calibrate_ensemble: filetypes/tar: using cached scores
2026-06-10 06:34:24,287 INFO azoth_calibrate_ensemble: filetypes/perl: using cached scores
2026-06-10 06:34:24,560 INFO azoth_calibrate_ensemble: filetypes/package.json: using cached scores
2026-06-10 06:34:24,560 INFO collimator.features: DB-backed feature extraction: 82543 rows, 8 workers, batch_size=1024
2026-06-10 06:34:24,837 INFO azoth_calibrate_ensemble: filetypes/makefile: using cached scores
2026-06-10 06:34:24,879 INFO azoth_calibrate_ensemble: filetypes/ruby: using cached scores
2026-06-10 06:34:24,903 INFO azoth_calibrate_ensemble: filetypes/jpeg: using cached scores
2026-06-10 06:34:25,375 INFO azoth_calibrate_ensemble: filetypes/objc: using cached scores
2026-06-10 06:34:25,570 INFO azoth_calibrate_ensemble: filetypes/lua: using cached scores
2026-06-10 06:34:26,022 INFO azoth_calibrate_ensemble: filetypes/html: using cached scores
2026-06-10 06:34:26,139 INFO azoth_calibrate_ensemble: filetypes/macho: using cached scores
2026-06-10 06:34:26,198 INFO azoth_calibrate_ensemble: filetypes/vbs: using cached scores
2026-06-10 06:34:26,900 INFO azoth_calibrate_ensemble: filetypes/plist: using cached scores
2026-06-10 06:34:27,670 INFO azoth_calibrate_ensemble: filetypes/ole: using cached scores
2026-06-10 06:34:28,111 INFO azoth_calibrate_ensemble: filetypes/powershell: using cached scores
2026-06-10 06:34:28,460 INFO azoth_calibrate_ensemble: filetypes/pkg-info: using cached scores
2026-06-10 06:34:28,729 INFO azoth_calibrate_ensemble: filetypes/deb: using cached scores
2026-06-10 06:34:29,074 INFO azoth_calibrate_ensemble: filetypes/jar: using cached scores
2026-06-10 06:34:29,767 INFO azoth_calibrate_ensemble: filetypes/rtf: using cached scores
2026-06-10 06:34:30,000 INFO azoth_calibrate_ensemble: filetypes/clojure: using cached scores
2026-06-10 06:34:30,206 INFO azoth_calibrate_ensemble: filetypes/groovy: using cached scores
2026-06-10 06:34:30,644 INFO azoth_calibrate_ensemble: filetypes/lnk: using cached scores
2026-06-10 06:34:30,967 INFO azoth_calibrate_ensemble: filetypes/msi: using cached scores
2026-06-10 06:34:31,119 INFO azoth_calibrate_ensemble: filetypes/docx: using cached scores
2026-06-10 06:34:31,808 INFO azoth_calibrate_ensemble: filetypes/dockerfile: using cached scores
2026-06-10 06:34:31,999 INFO azoth_calibrate_ensemble: filetypes/cargo.toml: using cached scores
2026-06-10 06:34:33,395 INFO azoth_calibrate_ensemble: filetypes/chrome-manifest: using cached scores
2026-06-10 06:34:33,518 INFO azoth_calibrate_ensemble: filetypes/crx: using cached scores
2026-06-10 06:34:33,939 INFO azoth_calibrate_ensemble: filetypes/applescript: using cached scores
2026-06-10 06:34:36,104 INFO azoth_calibrate_ensemble: filetypes/whl: using cached scores
2026-06-10 06:34:39,104 INFO azoth_calibrate_ensemble: filetypes/java: saved route feature matrix cache out/cache/azoth-route-features/filetypes_java-1685037226-b61d97fe8165f12a-e4ea48eb4bca8ccc.matrix.npz
2026-06-10 06:34:39,289 INFO azoth_calibrate_ensemble: filetypes/java: refreshed 82543 rows in 16.8s (fetch 1.4s, filter 0.0s, load 0.6s, extract 14.5s, matrix 0.0s, predict 0.1s, write 0.1s; feature_cache_read 0.0s, feature_cache_write 0.0s; features=501 nnz=1917691)
make[1]: *** [Makefile:1201: azoth-calibrate] Terminated)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9705)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `c8c3fced3218855b` | `d7d6e20555c39011` | `e7694075947f7e06` |
| PR AUC | 0.9705 | 0.9769 | 0.9770 |
| ROC AUC | 0.9650 | 0.9666 | 0.9672 |
| F1 | 0.9259 | 0.9825 | 0.9825 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: signal: terminated (log /home/t/collimator/out/autocollie/runs/2026-06-10T10-33-43_20260610T103342-promote-c8c3fced3218855b_azoth-validate.log; tail: 2026-06-10 06:34:17,599 INFO azoth_calibrate_ensemble: filetypes/python: using cached scores
2026-06-10 06:34:18,318 INFO azoth_calibrate_ensemble: filetypes/xml: using cached scores
2026-06-10 06:34:18,370 INFO azoth_calibrate_ensemble: filetypes/pdf: using cached scores
2026-06-10 06:34:18,692 INFO azoth_calibrate_ensemble: filetypes/python-bytecode: using cached scores
2026-06-10 06:34:18,955 INFO azoth_calibrate_ensemble: filetypes/png: using cached scores
2026-06-10 06:34:19,088 INFO azoth_calibrate_ensemble: filetypes/batch: using cached scores
2026-06-10 06:34:19,301 INFO azoth_calibrate_ensemble: filetypes/php: using cached scores
2026-06-10 06:34:19,531 INFO azoth_calibrate_ensemble: filetypes/go: using cached scores
2026-06-10 06:34:20,284 INFO azoth_calibrate_ensemble: filetypes/text: using cached scores
2026-06-10 06:34:20,921 INFO azoth_calibrate_ensemble: filetypes/rust: using cached scores
2026-06-10 06:34:21,003 INFO azoth_calibrate_ensemble: filetypes/zip: using cached scores
2026-06-10 06:34:22,450 INFO azoth_calibrate_ensemble: filetypes/kotlin: using cached scores
2026-06-10 06:34:22,504 INFO azoth_calibrate_ensemble: filetypes/java: route artifacts changed; refreshing score cache
2026-06-10 06:34:23,019 INFO azoth_calibrate_ensemble: filetypes/csharp: using cached scores
2026-06-10 06:34:23,032 INFO azoth_calibrate_ensemble: filetypes/shell: using cached scores
2026-06-10 06:34:23,220 INFO azoth_calibrate_ensemble: filetypes/xlsx: using cached scores
2026-06-10 06:34:23,478 INFO azoth_calibrate_ensemble: filetypes/xls: using cached scores
2026-06-10 06:34:23,931 INFO azoth_calibrate_ensemble: filetypes/tar: using cached scores
2026-06-10 06:34:24,287 INFO azoth_calibrate_ensemble: filetypes/perl: using cached scores
2026-06-10 06:34:24,560 INFO azoth_calibrate_ensemble: filetypes/package.json: using cached scores
2026-06-10 06:34:24,560 INFO collimator.features: DB-backed feature extraction: 82543 rows, 8 workers, batch_size=1024
2026-06-10 06:34:24,837 INFO azoth_calibrate_ensemble: filetypes/makefile: using cached scores
2026-06-10 06:34:24,879 INFO azoth_calibrate_ensemble: filetypes/ruby: using cached scores
2026-06-10 06:34:24,903 INFO azoth_calibrate_ensemble: filetypes/jpeg: using cached scores
2026-06-10 06:34:25,375 INFO azoth_calibrate_ensemble: filetypes/objc: using cached scores
2026-06-10 06:34:25,570 INFO azoth_calibrate_ensemble: filetypes/lua: using cached scores
2026-06-10 06:34:26,022 INFO azoth_calibrate_ensemble: filetypes/html: using cached scores
2026-06-10 06:34:26,139 INFO azoth_calibrate_ensemble: filetypes/macho: using cached scores
2026-06-10 06:34:26,198 INFO azoth_calibrate_ensemble: filetypes/vbs: using cached scores
2026-06-10 06:34:26,900 INFO azoth_calibrate_ensemble: filetypes/plist: using cached scores
2026-06-10 06:34:27,670 INFO azoth_calibrate_ensemble: filetypes/ole: using cached scores
2026-06-10 06:34:28,111 INFO azoth_calibrate_ensemble: filetypes/powershell: using cached scores
2026-06-10 06:34:28,460 INFO azoth_calibrate_ensemble: filetypes/pkg-info: using cached scores
2026-06-10 06:34:28,729 INFO azoth_calibrate_ensemble: filetypes/deb: using cached scores
2026-06-10 06:34:29,074 INFO azoth_calibrate_ensemble: filetypes/jar: using cached scores
2026-06-10 06:34:29,767 INFO azoth_calibrate_ensemble: filetypes/rtf: using cached scores
2026-06-10 06:34:30,000 INFO azoth_calibrate_ensemble: filetypes/clojure: using cached scores
2026-06-10 06:34:30,206 INFO azoth_calibrate_ensemble: filetypes/groovy: using cached scores
2026-06-10 06:34:30,644 INFO azoth_calibrate_ensemble: filetypes/lnk: using cached scores
2026-06-10 06:34:30,967 INFO azoth_calibrate_ensemble: filetypes/msi: using cached scores
2026-06-10 06:34:31,119 INFO azoth_calibrate_ensemble: filetypes/docx: using cached scores
2026-06-10 06:34:31,808 INFO azoth_calibrate_ensemble: filetypes/dockerfile: using cached scores
2026-06-10 06:34:31,999 INFO azoth_calibrate_ensemble: filetypes/cargo.toml: using cached scores
2026-06-10 06:34:33,395 INFO azoth_calibrate_ensemble: filetypes/chrome-manifest: using cached scores
2026-06-10 06:34:33,518 INFO azoth_calibrate_ensemble: filetypes/crx: using cached scores
2026-06-10 06:34:33,939 INFO azoth_calibrate_ensemble: filetypes/applescript: using cached scores
2026-06-10 06:34:36,104 INFO azoth_calibrate_ensemble: filetypes/whl: using cached scores
2026-06-10 06:34:39,104 INFO azoth_calibrate_ensemble: filetypes/java: saved route feature matrix cache out/cache/azoth-route-features/filetypes_java-1685037226-b61d97fe8165f12a-e4ea48eb4bca8ccc.matrix.npz
2026-06-10 06:34:39,289 INFO azoth_calibrate_ensemble: filetypes/java: refreshed 82543 rows in 16.8s (fetch 1.4s, filter 0.0s, load 0.6s, extract 14.5s, matrix 0.0s, predict 0.1s, write 0.1s; feature_cache_read 0.0s, feature_cache_write 0.0s; features=501 nnz=1917691)
make[1]: *** [Makefile:1201: azoth-calibrate] Terminated)
