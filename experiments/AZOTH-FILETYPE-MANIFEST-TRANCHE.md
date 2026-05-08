# Azoth Filetype Manifest Tranche

Stopped after the local DB replica was truncated. Results below use completed, content-addressed experiment summaries only; failed tail entries are excluded from candidate selection.

## Summary

- Planned entries: 408
- Completed/available entries: 395
- Failed entries: 13
- Missing entries: 0
- Routes with completed candidates: 50
- Verdicts: below_history=8, candidate=28, near=6, winner=8
- CSV: `out/experiments/azoth/filetype_manifest_tranche_summary.csv`
- JSON: `out/experiments/azoth/filetype_manifest_tranche_summary.json`

## Recommended Retrain Set

These are the tranche winners/near-winners that beat or matched prior route history and have usable sampled F1. Use these first for the next candidate model-set train.

| route | idea | key | verdict | F1 | delta vs hist | AUC | AP |
|---|---|---|---|---:|---:|---:|---:|
| `filetypes/html` | `html_script_precision_regularized` | `5c049288c53b4c7f` | winner | 1.0000 | 0.3333 | 1.0000 | 1.0000 |
| `filetypes/rtf` | `rtf_doc_kv_textenc_static` | `62453ad0789b7662` | winner | 0.9565 | 0.0765 | 1.0000 | 1.0000 |
| `filetypes/powershell` | `powershell_script_kv_objective` | `a1631fc7b720c45a` | winner | 0.9752 | 0.0165 | 0.9996 | 0.9988 |
| `filetypes/batch` | `batch_script_no_presence` | `e980d96334bdcc5f` | winner | 0.9421 | 0.0153 | 0.9955 | 0.9854 |
| `filetypes/docx` | `docx_doc_metadata_only` | `d373780c950bf616` | winner | 0.9773 | 0.0102 | 0.9989 | 0.9990 |
| `filetypes/jpeg` | `jpeg_media_metadata_only` | `c3ba1b6ce802c11e` | winner | 0.9778 | 0.0057 | 0.9993 | 0.9905 |
| `filetypes/go` | `go_source_symbols_static` | `9238b5c0f9bc10df` | winner | 0.9744 | 0.0044 | 0.9999 | 0.9885 |
| `filetypes/pkg-info` | `pkg_info_metadata_scoreless_hsn` | `4d86b8621c779c26` | winner | 1.0000 | 0.0011 | 1.0000 | 1.0000 |
| `filetypes/elf` | `elf_native_hardtail_symbols` | `cefdeacf342cd958` | near | 0.9982 | 0.0007 | 1.0000 | 1.0000 |
| `filetypes/javascript` | `javascript_script_kv_objective` | `d05e794df7e683ce` | near | 0.9977 | 0.0006 | 0.9999 | 0.9999 |
| `filetypes/python` | `python_script_kv_objective` | `ed8fc17af0279b85` | near | 0.9899 | -0.0004 | 0.9999 | 0.9992 |
| `filetypes/package.json` | `package_json_metadata_lifecycle` | `b5579ff9d162f624` | near | 0.9984 | 0.0000 | 0.9998 | 0.9999 |
| `filetypes/xlsx` | `xlsx_doc_metadata_only` | `d83c80018e866336` | near | 0.9286 | 0.0000 | 1.0000 | 1.0000 |

## Candidate Winners

| verdict | route | best tranche idea | key | F1 | delta vs hist | AUC | AP | deployed L3 recall |
|---|---|---|---|---:|---:|---:|---:|---:|
| winner | `filetypes/html` | `html_script_precision_regularized` | `5c049288c53b4c7f` | 1.0000 | 0.3333 | 1.0000 | 1.0000 | - |
| winner | `filetypes/rtf` | `rtf_doc_kv_textenc_static` | `62453ad0789b7662` | 0.9565 | 0.0765 | 1.0000 | 1.0000 | - |
| winner | `filetypes/powershell` | `powershell_script_kv_objective` | `a1631fc7b720c45a` | 0.9752 | 0.0165 | 0.9996 | 0.9988 | 0.9149 |
| winner | `filetypes/batch` | `batch_script_no_presence` | `e980d96334bdcc5f` | 0.9421 | 0.0153 | 0.9955 | 0.9854 | 0.8864 |
| winner | `filetypes/docx` | `docx_doc_metadata_only` | `d373780c950bf616` | 0.9773 | 0.0102 | 0.9989 | 0.9990 | 0.8235 |
| winner | `filetypes/jpeg` | `jpeg_media_metadata_only` | `c3ba1b6ce802c11e` | 0.9778 | 0.0057 | 0.9993 | 0.9905 | 0.2308 |
| winner | `filetypes/go` | `go_source_symbols_static` | `9238b5c0f9bc10df` | 0.9744 | 0.0044 | 0.9999 | 0.9885 | 0.4174 |
| winner | `filetypes/pkg-info` | `pkg_info_metadata_scoreless_hsn` | `4d86b8621c779c26` | 1.0000 | 0.0011 | 1.0000 | 1.0000 | 1.0000 |
| near | `filetypes/elf` | `elf_native_hardtail_symbols` | `cefdeacf342cd958` | 0.9982 | 0.0007 | 1.0000 | 1.0000 | 0.9861 |
| near | `filetypes/javascript` | `javascript_script_kv_objective` | `d05e794df7e683ce` | 0.9977 | 0.0006 | 0.9999 | 0.9999 | 0.9309 |
| near | `filetypes/python` | `python_script_kv_objective` | `ed8fc17af0279b85` | 0.9899 | -0.0004 | 0.9999 | 0.9992 | 0.8708 |
| near | `filetypes/package.json` | `package_json_metadata_lifecycle` | `b5579ff9d162f624` | 0.9984 | 0.0000 | 0.9998 | 0.9999 | 0.9084 |
| near | `filetypes/pptx` | `pptx_doc_kv_textenc_static` | `623d582fd7cb7051` | 0.1600 | 0.0000 | 0.5000 | 0.0870 | - |
| near | `filetypes/xlsx` | `xlsx_doc_metadata_only` | `d83c80018e866336` | 0.9286 | 0.0000 | 1.0000 | 1.0000 | - |
| candidate | `filetypes/chrome-manifest` | `chrome_manifest_metadata_lifecycle` | `a09d92deaae8b8a2` | 0.6667 | - | 0.8889 | 0.7500 | - |
| candidate | `filetypes/csharp` | `csharp_source_symbols_static` | `12f27911d5142a37` | 0.9856 | - | 1.0000 | 0.9991 | 0.7386 |
| candidate | `filetypes/data` | `data_generic_precision_regularized` | `030b1d130e639185` | 0.9149 | - | 0.9999 | 0.9988 | 0.9070 |
| candidate | `filetypes/deb` | `deb_archive_kv_manifest` | `1d136e9420dc5a4f` | 0.0073 | - | 0.5000 | 0.0036 | - |
| candidate | `filetypes/github-actions` | `github_actions_metadata_lifecycle` | `9196fba2372a18a7` | 0.0035 | - | 0.5000 | 0.0018 | - |
| candidate | `filetypes/groovy` | `groovy_script_kv_objective` | `2ca4f2116d82283a` | 0.0033 | - | 0.5000 | 0.0016 | - |
| candidate | `filetypes/gz` | `gz_archive_kv_manifest` | `269b994b10931423` | 0.8780 | - | 0.9998 | 0.9722 | - |
| candidate | `filetypes/jar` | `jar_portable_symbol_bytecode` | `b23e538b9adef820` | 0.9815 | - | 0.9935 | 0.9855 | 0.9703 |
| candidate | `filetypes/java` | `java_source_metadata_only` | `9ec582d7b50bfe1f` | 0.3333 | - | 1.0000 | 1.0000 | - |
| candidate | `filetypes/java_class` | `java_class_portable_hardtail_kv` | `871e9d94cd0a3386` | 0.9353 | - | 0.9879 | 0.8770 | 0.9756 |
| candidate | `filetypes/kotlin` | `kotlin_source_symbols_static` | `3612ea770ffb3a9d` | 0.9655 | - | 0.9992 | 0.9896 | 0.9221 |
| candidate | `filetypes/lua` | `lua_script_symbols_kv` | `629987845a25de85` | 0.5000 | - | 0.8063 | 0.4179 | - |
| candidate | `filetypes/makefile` | `makefile_script_no_presence` | `67dfd6a853c2e501` | 0.5000 | - | 0.9764 | 0.6452 | 0.2500 |
| candidate | `filetypes/msi` | `msi_native_symbol_kv_static` | `b3edcac05d2d07bc` | 0.9655 | - | 1.0000 | 1.0000 | - |
| candidate | `filetypes/objc` | `objc_source_symbols_density` | `5b170aaa9f23bdec` | 0.0009 | - | 0.5000 | 0.0004 | - |
| candidate | `filetypes/ole` | `ole_doc_metadata_only` | `ebc952bc6b5c9632` | 0.9474 | - | 0.9999 | 0.9979 | 0.9574 |
| candidate | `filetypes/perl` | `perl_script_precision_regularized` | `402fa12beb5fd195` | 0.9714 | - | 0.9585 | 0.9448 | 0.9444 |
| candidate | `filetypes/php` | `php_script_kv_objective` | `e50ccc5699dabea6` | 0.9972 | - | 1.0000 | 0.9999 | 0.9812 |
| candidate | `filetypes/plist` | `plist_metadata_kv_no_textenc` | `91101e7d76bb55cf` | 0.8475 | - | 0.9927 | 0.9121 | 0.6379 |
| candidate | `filetypes/python-bytecode` | `python_bytecode_portable_symbol_bytecode` | `547d6c3899e3da4f` | 1.0000 | - | 1.0000 | 1.0000 | 0.8889 |
| candidate | `filetypes/ruby` | `ruby_script_scoreless_hsn10` | `fdedd620da3aae18` | 0.9231 | - | 0.9999 | 0.9821 | 1.0000 |
| candidate | `filetypes/tar` | `tar_archive_kv_manifest` | `87260f136cb2dbca` | 0.9910 | - | 0.9989 | 0.9996 | 0.9725 |
| candidate | `filetypes/tar.gz` | `tar_gz_archive_recall_beta2` | `043e883b8b948f9e` | 0.9939 | - | 0.9994 | 0.9995 | 0.9690 |
| candidate | `filetypes/text` | `text_generic_scoreless_hsn8` | `6b511d2fbb657a6b` | 0.2884 | - | 0.9007 | 0.1631 | - |
| candidate | `filetypes/unknown` | `unknown_generic_kv_textenc` | `a2df8f35de6792e0` | 0.5833 | - | 0.9943 | 0.6364 | - |
| candidate | `filetypes/vbs` | `vbs_script_kv_objective` | `aa49dc29fa75150d` | 0.9942 | - | 0.9968 | 0.9972 | 0.6714 |
| candidate | `filetypes/zip` | `zip_archive_recall_beta2` | `7e4f43e76fc59725` | 0.9936 | - | 0.9986 | 0.9998 | 0.7931 |
| candidate | `filetypes/zst` | `zst_archive_kv_manifest` | `08e5a2b1442738e6` | 1.0000 | - | 1.0000 | 1.0000 | 1.0000 |

## No Historical Baseline

These routes had no non-tranche historical comparison in the experiment DB. Strong rows may be worth confirming; weak rows should be treated as diagnostics, not winners.

| bucket | route | best tranche idea | key | F1 | AUC | AP |
|---|---|---|---|---:|---:|---:|
| strong | `filetypes/csharp` | `csharp_source_symbols_static` | `12f27911d5142a37` | 0.9856 | 1.0000 | 0.9991 |
| strong | `filetypes/data` | `data_generic_precision_regularized` | `030b1d130e639185` | 0.9149 | 0.9999 | 0.9988 |
| strong | `filetypes/jar` | `jar_portable_symbol_bytecode` | `b23e538b9adef820` | 0.9815 | 0.9935 | 0.9855 |
| strong | `filetypes/java_class` | `java_class_portable_hardtail_kv` | `871e9d94cd0a3386` | 0.9353 | 0.9879 | 0.8770 |
| strong | `filetypes/kotlin` | `kotlin_source_symbols_static` | `3612ea770ffb3a9d` | 0.9655 | 0.9992 | 0.9896 |
| strong | `filetypes/msi` | `msi_native_symbol_kv_static` | `b3edcac05d2d07bc` | 0.9655 | 1.0000 | 1.0000 |
| strong | `filetypes/ole` | `ole_doc_metadata_only` | `ebc952bc6b5c9632` | 0.9474 | 0.9999 | 0.9979 |
| strong | `filetypes/perl` | `perl_script_precision_regularized` | `402fa12beb5fd195` | 0.9714 | 0.9585 | 0.9448 |
| strong | `filetypes/php` | `php_script_kv_objective` | `e50ccc5699dabea6` | 0.9972 | 1.0000 | 0.9999 |
| strong | `filetypes/python-bytecode` | `python_bytecode_portable_symbol_bytecode` | `547d6c3899e3da4f` | 1.0000 | 1.0000 | 1.0000 |
| strong | `filetypes/ruby` | `ruby_script_scoreless_hsn10` | `fdedd620da3aae18` | 0.9231 | 0.9999 | 0.9821 |
| strong | `filetypes/tar` | `tar_archive_kv_manifest` | `87260f136cb2dbca` | 0.9910 | 0.9989 | 0.9996 |
| strong | `filetypes/tar.gz` | `tar_gz_archive_recall_beta2` | `043e883b8b948f9e` | 0.9939 | 0.9994 | 0.9995 |
| strong | `filetypes/vbs` | `vbs_script_kv_objective` | `aa49dc29fa75150d` | 0.9942 | 0.9968 | 0.9972 |
| strong | `filetypes/zip` | `zip_archive_recall_beta2` | `7e4f43e76fc59725` | 0.9936 | 0.9986 | 0.9998 |
| strong | `filetypes/zst` | `zst_archive_kv_manifest` | `08e5a2b1442738e6` | 1.0000 | 1.0000 | 1.0000 |
| weak | `filetypes/chrome-manifest` | `chrome_manifest_metadata_lifecycle` | `a09d92deaae8b8a2` | 0.6667 | 0.8889 | 0.7500 |
| weak | `filetypes/deb` | `deb_archive_kv_manifest` | `1d136e9420dc5a4f` | 0.0073 | 0.5000 | 0.0036 |
| weak | `filetypes/github-actions` | `github_actions_metadata_lifecycle` | `9196fba2372a18a7` | 0.0035 | 0.5000 | 0.0018 |
| weak | `filetypes/groovy` | `groovy_script_kv_objective` | `2ca4f2116d82283a` | 0.0033 | 0.5000 | 0.0016 |
| weak | `filetypes/gz` | `gz_archive_kv_manifest` | `269b994b10931423` | 0.8780 | 0.9998 | 0.9722 |
| weak | `filetypes/java` | `java_source_metadata_only` | `9ec582d7b50bfe1f` | 0.3333 | 1.0000 | 1.0000 |
| weak | `filetypes/lua` | `lua_script_symbols_kv` | `629987845a25de85` | 0.5000 | 0.8063 | 0.4179 |
| weak | `filetypes/makefile` | `makefile_script_no_presence` | `67dfd6a853c2e501` | 0.5000 | 0.9764 | 0.6452 |
| weak | `filetypes/objc` | `objc_source_symbols_density` | `5b170aaa9f23bdec` | 0.0009 | 0.5000 | 0.0004 |
| weak | `filetypes/plist` | `plist_metadata_kv_no_textenc` | `91101e7d76bb55cf` | 0.8475 | 0.9927 | 0.9121 |
| weak | `filetypes/text` | `text_generic_scoreless_hsn8` | `6b511d2fbb657a6b` | 0.2884 | 0.9007 | 0.1631 |
| weak | `filetypes/unknown` | `unknown_generic_kv_textenc` | `a2df8f35de6792e0` | 0.5833 | 0.9943 | 0.6364 |

## Below Historical Best

| route | best tranche idea | F1 | historical best | hist F1 | delta |
|---|---|---:|---|---:|---:|
| `filetypes/rust` | `rust_source_scoreless_hsn8` | 0.4444 | `rust_training_capacity_boost` | 1.0000 | -0.5556 |
| `filetypes/xml` | `xml_metadata_kv_no_textenc` | 0.6430 | `xml_kv_schema_textenc` | 0.7507 | -0.1076 |
| `filetypes/pdf` | `pdf_doc_kv_textenc_static` | 0.9474 | `pdf_textenc_kv_deep_paths` | 1.0000 | -0.0526 |
| `filetypes/shell` | `shell_script_no_presence` | 0.9689 | `shell_kv_metric_vocab_wide` | 0.9859 | -0.0170 |
| `filetypes/png` | `png_media_metadata_only` | 0.9837 | `png_kv_chunk_textenc` | 0.9881 | -0.0045 |
| `filetypes/macho` | `macho_native_hardtail_symbols` | 0.9868 | `macho_scoreless_hsn8` | 0.9900 | -0.0031 |
| `filetypes/pe` | `pe_native_symbol_kv_static` | 0.9952 | `pe_route_tail_static` | 0.9969 | -0.0016 |
| `filetypes/c` | `c_source_symbols_static` | 0.9958 | `c_symbol_static_kv` | 0.9968 | -0.0011 |

## Failed Entries

- `filetypes/pe:pe_native_hardtail_symbols`
- `filetypes/pe:pe_native_metadata_only`
- `filetypes/pe:pe_native_precision_regularized`
- `filetypes/pe:pe_native_recall_beta2`
- `filetypes/pe:pe_native_static_no_score`
- `filetypes/swift:swift_source_hardtail_kv`
- `filetypes/swift:swift_source_metadata_only`
- `filetypes/swift:swift_source_objective_symbols`
- `filetypes/swift:swift_source_precision_regularized`
- `filetypes/swift:swift_source_scoreless_hsn8`
- `filetypes/swift:swift_source_symbols_density`
- `filetypes/swift:swift_source_symbols_static`
- `filetypes/swift:swift_source_textenc_only`

## Next Use

Use `winner` and `near` rows as the first candidate set for a full model-set retrain. For routes marked `below_history`, keep the historical/default recipe unless a full-corpus route policy result says otherwise.
