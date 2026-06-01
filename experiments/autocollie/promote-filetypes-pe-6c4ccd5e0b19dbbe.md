# Promote REJECTED — `6c4ccd5e0b19dbbe` on `filetypes/pe`

Generated 2026-06-01T01:54:58Z

azoth-validate failed: signal: terminated (log /home/t/collimator/out/autocollie/runs/2026-05-31T22-52-12_20260531T223125-promote-6c4ccd5e0b19dbbe_azoth-validate.log; tail: 2026-05-31 18:53:23,339 INFO azoth_calibrate_ensemble: filetypes/c: using cached scores
2026-05-31 18:53:23,964 INFO azoth_calibrate_ensemble: filetypes/elf: using cached scores
2026-05-31 18:53:24,208 WARNING azoth_calibrate_ensemble: filetypes/pe: skipped 15884 rows absent from general score cache
2026-05-31 18:53:24,596 INFO azoth_calibrate_ensemble: filetypes/pdf: using cached scores
2026-05-31 18:53:25,252 INFO azoth_calibrate_ensemble: filetypes/batch: using cached scores
2026-05-31 18:53:25,929 INFO azoth_calibrate_ensemble: filetypes/python: using cached scores
2026-05-31 18:53:26,608 INFO azoth_calibrate_ensemble: filetypes/xml: using cached scores
2026-05-31 18:53:27,288 INFO azoth_calibrate_ensemble: filetypes/png: using cached scores
2026-05-31 18:53:27,958 INFO azoth_calibrate_ensemble: filetypes/php: using cached scores
2026-05-31 18:53:28,615 INFO azoth_calibrate_ensemble: filetypes/go: using cached scores
2026-05-31 18:53:29,271 INFO azoth_calibrate_ensemble: filetypes/zip: using cached scores
2026-05-31 18:53:29,946 INFO azoth_calibrate_ensemble: filetypes/rust: using cached scores
2026-05-31 18:53:30,568 INFO azoth_calibrate_ensemble: filetypes/kotlin: using cached scores
2026-05-31 18:53:31,217 INFO azoth_calibrate_ensemble: filetypes/python-bytecode: using cached scores
2026-05-31 18:53:31,806 INFO azoth_calibrate_ensemble: filetypes/text: using cached scores
2026-05-31 18:53:32,383 INFO azoth_calibrate_ensemble: filetypes/shell: using cached scores
2026-05-31 18:53:32,988 INFO azoth_calibrate_ensemble: filetypes/csharp: using cached scores
2026-05-31 18:53:33,582 INFO azoth_calibrate_ensemble: filetypes/markdown: using cached scores
2026-05-31 18:53:34,166 INFO azoth_calibrate_ensemble: filetypes/xls: using cached scores
2026-05-31 18:53:34,756 INFO azoth_calibrate_ensemble: filetypes/xlsx: using cached scores
2026-05-31 18:53:35,322 INFO azoth_calibrate_ensemble: filetypes/tar.gz: using cached scores
2026-05-31 18:53:35,909 INFO azoth_calibrate_ensemble: filetypes/java: using cached scores
2026-05-31 18:53:36,475 INFO azoth_calibrate_ensemble: filetypes/package.json: using cached scores
2026-05-31 18:53:37,046 INFO azoth_calibrate_ensemble: filetypes/perl: using cached scores
2026-05-31 18:53:37,634 INFO azoth_calibrate_ensemble: filetypes/json: using cached scores
2026-05-31 18:53:38,220 INFO azoth_calibrate_ensemble: filetypes/jpeg: using cached scores
2026-05-31 18:53:38,821 INFO azoth_calibrate_ensemble: filetypes/html: using cached scores
2026-05-31 18:53:39,392 INFO azoth_calibrate_ensemble: filetypes/ruby: using cached scores
2026-05-31 18:53:39,984 INFO azoth_calibrate_ensemble: filetypes/makefile: using cached scores
2026-05-31 18:53:40,556 INFO azoth_calibrate_ensemble: filetypes/lua: using cached scores
2026-05-31 18:53:41,168 INFO azoth_calibrate_ensemble: filetypes/macho: using cached scores
2026-05-31 18:53:41,846 INFO azoth_calibrate_ensemble: filetypes/plist: using cached scores
2026-05-31 18:53:42,506 INFO azoth_calibrate_ensemble: filetypes/vbs: using cached scores
2026-05-31 18:53:43,166 INFO azoth_calibrate_ensemble: filetypes/pkg-info: using cached scores
2026-05-31 18:53:43,824 INFO azoth_calibrate_ensemble: filetypes/ole: using cached scores
2026-05-31 18:53:44,479 INFO azoth_calibrate_ensemble: filetypes/powershell: using cached scores
2026-05-31 18:53:45,121 INFO azoth_calibrate_ensemble: filetypes/deb: using cached scores
2026-05-31 18:53:45,749 INFO azoth_calibrate_ensemble: filetypes/jar: using cached scores
2026-05-31 18:53:46,412 INFO azoth_calibrate_ensemble: filetypes/groovy: using cached scores
2026-05-31 18:53:47,068 INFO azoth_calibrate_ensemble: filetypes/rtf: using cached scores
2026-05-31 18:53:47,751 INFO azoth_calibrate_ensemble: filetypes/lnk: using cached scores
2026-05-31 18:53:48,329 INFO azoth_calibrate_ensemble: filetypes/docx: using cached scores
2026-05-31 18:53:48,903 INFO azoth_calibrate_ensemble: filetypes/clojure: using cached scores
2026-05-31 18:53:49,501 INFO azoth_calibrate_ensemble: filetypes/tar: using cached scores
2026-05-31 18:53:50,110 INFO azoth_calibrate_ensemble: filetypes/dockerfile: using cached scores
2026-05-31 18:53:50,682 INFO azoth_calibrate_ensemble: filetypes/package-lock.json: using cached scores
2026-05-31 18:53:51,259 INFO azoth_calibrate_ensemble: filetypes/pptx: using cached scores
2026-05-31 18:53:51,836 INFO azoth_calibrate_ensemble: filetypes/chrome-manifest: using cached scores
2026-05-31 18:53:52,419 INFO azoth_calibrate_ensemble: filetypes/crx: using cached scores
make[1]: *** [Makefile:1048: azoth-calibrate] Terminated)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9995)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `6c4ccd5e0b19dbbe` | `1ba9deb45187c4c8` | `59d50761915f26b7` |
| PR AUC | 0.9995 | 1.0000 | 1.0000 |
| ROC AUC | 0.9995 | 0.9999 | 0.9999 |
| F1 | 0.9911 | 0.9989 | 0.9974 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: signal: terminated (log /home/t/collimator/out/autocollie/runs/2026-05-31T22-52-12_20260531T223125-promote-6c4ccd5e0b19dbbe_azoth-validate.log; tail: 2026-05-31 18:53:23,339 INFO azoth_calibrate_ensemble: filetypes/c: using cached scores
2026-05-31 18:53:23,964 INFO azoth_calibrate_ensemble: filetypes/elf: using cached scores
2026-05-31 18:53:24,208 WARNING azoth_calibrate_ensemble: filetypes/pe: skipped 15884 rows absent from general score cache
2026-05-31 18:53:24,596 INFO azoth_calibrate_ensemble: filetypes/pdf: using cached scores
2026-05-31 18:53:25,252 INFO azoth_calibrate_ensemble: filetypes/batch: using cached scores
2026-05-31 18:53:25,929 INFO azoth_calibrate_ensemble: filetypes/python: using cached scores
2026-05-31 18:53:26,608 INFO azoth_calibrate_ensemble: filetypes/xml: using cached scores
2026-05-31 18:53:27,288 INFO azoth_calibrate_ensemble: filetypes/png: using cached scores
2026-05-31 18:53:27,958 INFO azoth_calibrate_ensemble: filetypes/php: using cached scores
2026-05-31 18:53:28,615 INFO azoth_calibrate_ensemble: filetypes/go: using cached scores
2026-05-31 18:53:29,271 INFO azoth_calibrate_ensemble: filetypes/zip: using cached scores
2026-05-31 18:53:29,946 INFO azoth_calibrate_ensemble: filetypes/rust: using cached scores
2026-05-31 18:53:30,568 INFO azoth_calibrate_ensemble: filetypes/kotlin: using cached scores
2026-05-31 18:53:31,217 INFO azoth_calibrate_ensemble: filetypes/python-bytecode: using cached scores
2026-05-31 18:53:31,806 INFO azoth_calibrate_ensemble: filetypes/text: using cached scores
2026-05-31 18:53:32,383 INFO azoth_calibrate_ensemble: filetypes/shell: using cached scores
2026-05-31 18:53:32,988 INFO azoth_calibrate_ensemble: filetypes/csharp: using cached scores
2026-05-31 18:53:33,582 INFO azoth_calibrate_ensemble: filetypes/markdown: using cached scores
2026-05-31 18:53:34,166 INFO azoth_calibrate_ensemble: filetypes/xls: using cached scores
2026-05-31 18:53:34,756 INFO azoth_calibrate_ensemble: filetypes/xlsx: using cached scores
2026-05-31 18:53:35,322 INFO azoth_calibrate_ensemble: filetypes/tar.gz: using cached scores
2026-05-31 18:53:35,909 INFO azoth_calibrate_ensemble: filetypes/java: using cached scores
2026-05-31 18:53:36,475 INFO azoth_calibrate_ensemble: filetypes/package.json: using cached scores
2026-05-31 18:53:37,046 INFO azoth_calibrate_ensemble: filetypes/perl: using cached scores
2026-05-31 18:53:37,634 INFO azoth_calibrate_ensemble: filetypes/json: using cached scores
2026-05-31 18:53:38,220 INFO azoth_calibrate_ensemble: filetypes/jpeg: using cached scores
2026-05-31 18:53:38,821 INFO azoth_calibrate_ensemble: filetypes/html: using cached scores
2026-05-31 18:53:39,392 INFO azoth_calibrate_ensemble: filetypes/ruby: using cached scores
2026-05-31 18:53:39,984 INFO azoth_calibrate_ensemble: filetypes/makefile: using cached scores
2026-05-31 18:53:40,556 INFO azoth_calibrate_ensemble: filetypes/lua: using cached scores
2026-05-31 18:53:41,168 INFO azoth_calibrate_ensemble: filetypes/macho: using cached scores
2026-05-31 18:53:41,846 INFO azoth_calibrate_ensemble: filetypes/plist: using cached scores
2026-05-31 18:53:42,506 INFO azoth_calibrate_ensemble: filetypes/vbs: using cached scores
2026-05-31 18:53:43,166 INFO azoth_calibrate_ensemble: filetypes/pkg-info: using cached scores
2026-05-31 18:53:43,824 INFO azoth_calibrate_ensemble: filetypes/ole: using cached scores
2026-05-31 18:53:44,479 INFO azoth_calibrate_ensemble: filetypes/powershell: using cached scores
2026-05-31 18:53:45,121 INFO azoth_calibrate_ensemble: filetypes/deb: using cached scores
2026-05-31 18:53:45,749 INFO azoth_calibrate_ensemble: filetypes/jar: using cached scores
2026-05-31 18:53:46,412 INFO azoth_calibrate_ensemble: filetypes/groovy: using cached scores
2026-05-31 18:53:47,068 INFO azoth_calibrate_ensemble: filetypes/rtf: using cached scores
2026-05-31 18:53:47,751 INFO azoth_calibrate_ensemble: filetypes/lnk: using cached scores
2026-05-31 18:53:48,329 INFO azoth_calibrate_ensemble: filetypes/docx: using cached scores
2026-05-31 18:53:48,903 INFO azoth_calibrate_ensemble: filetypes/clojure: using cached scores
2026-05-31 18:53:49,501 INFO azoth_calibrate_ensemble: filetypes/tar: using cached scores
2026-05-31 18:53:50,110 INFO azoth_calibrate_ensemble: filetypes/dockerfile: using cached scores
2026-05-31 18:53:50,682 INFO azoth_calibrate_ensemble: filetypes/package-lock.json: using cached scores
2026-05-31 18:53:51,259 INFO azoth_calibrate_ensemble: filetypes/pptx: using cached scores
2026-05-31 18:53:51,836 INFO azoth_calibrate_ensemble: filetypes/chrome-manifest: using cached scores
2026-05-31 18:53:52,419 INFO azoth_calibrate_ensemble: filetypes/crx: using cached scores
make[1]: *** [Makefile:1048: azoth-calibrate] Terminated)
