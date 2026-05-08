# Azoth Wild Experiments

Created: 2026-05-06

Script:

```sh
scripts/run_azoth_wild_tranche.sh
```

Purpose: test new data-processing surfaces across general, filegroup, and
filetype models. These are screening runs, not promotion evidence. Promote only
after routed full-corpus confirmation under the active FP budget.

Profile:

- Serial execution.
- Default probe: 120k train / 30k external / 150 trees / 64 workers.
- General probe cap: 100k train / 30k external / 140 trees unless overridden.
- PE/native probe cap: 90k train / 25k external / 130 trees unless overridden.
- Large script/source/XML/C probes cap to 110k train / 30k external / 150 trees.
- Filetype and filegroup routes train with score filter disabled.
- New feature families here are experimental: `symbols`, `kv`, and `textenc`.
  Winners need litmus feature parity before deployment.

Resume controls:

```sh
RUN_LIMIT=4 scripts/run_azoth_wild_tranche.sh
RUN_SKIP=4 RUN_LIMIT=4 scripts/run_azoth_wild_tranche.sh
```

The 40 wild ideas:

1. `general_scoreless_symbol_kv_textenc`: global scoreless symbol/KV/text shape.
2. `documents_textenc_kv_static`: document group metadata and encoding shape.
3. `documents_scoreless_textenc_deep_paths`: document scoreless H/S/N deep paths.
4. `pdf_textenc_kv_deep_paths`: PDF metadata, text shape, deep severity paths.
5. `docx_kv_textenc_package_surface`: DOCX package metadata and text shape.
6. `rtf_escape_textenc_hsn`: RTF escape-heavy text shape plus H/S/N paths.
7. `html_script_url_textenc_symbols`: HTML script/url text shape and symbols.
8. `xml_kv_schema_textenc`: XML schema-like KV surface and text shape.
9. `media_textenc_kv_carrier`: media carrier metadata and embedded text shape.
10. `png_kv_chunk_textenc`: PNG chunk/metric KV and text shape.
11. `jpeg_exif_kv_textenc`: JPEG EXIF-like KV and text shape.
12. `media_metadata_only_no_traits`: media metadata-only stress test.
13. `applescript_tiny_textenc_symbols`: tiny AppleScript specialist probe.
14. `batch_cmd_symbol_textenc`: batch command surface and text encoding.
15. `batch_scoreless_deep_shell_paths`: batch scoreless deep severity paths.
16. `shell_command_textenc_symbols`: shell command symbols and text shape.
17. `shell_kv_metric_vocab_wide`: shell wide metric/KV vocabulary.
18. `shell_no_presence_command_surface`: shell static surface without traits.
19. `powershell_encoded_command_textenc`: PowerShell encoded-command shape.
20. `powershell_kv_symbols_tail`: PowerShell symbols/KV with hard negatives.
21. `scripts_symbol_kv_textenc_combo`: scripts group symbol/KV/text combo.
22. `scripts_no_trait_command_surface`: scripts command surface without traits.
23. `c_symbol_static_kv`: C source symbol/KV/static surface.
24. `c_no_score_symbols_only`: C scoreless symbol-only stress test.
25. `go_import_symbol_kv`: Go import/symbol/KV surface.
26. `go_static_textenc_scoreless`: Go scoreless static text surface.
27. `rust_crate_symbol_kv`: Rust crate/symbol/KV surface.
28. `rust_sparse_bad_tail`: Rust low-malware hard-tail stress test.
29. `source_symbol_kv_textenc_combo`: source group symbols/KV/text+density.
30. `source_static_surface_no_traits`: source group static surface without traits.
31. `package_json_kv_lifecycle_textenc`: package.json lifecycle metadata.
32. `package_json_metadata_only`: package.json metadata-only stress test.
33. `pkg_info_kv_textenc_supply_chain`: pkg-info supply-chain metadata.
34. `pkg_info_scoreless_metadata_only`: pkg-info metadata-only scoreless test.
35. `elf_symbol_vocab_kv_static`: ELF symbols/KV/static combo.
36. `elf_no_score_symbols_textenc`: ELF scoreless symbols plus text shape.
37. `macho_symbol_kv_textenc`: Mach-O symbols/KV/text shape with hard tail.
38. `pe_symbol_kv_import_surface`: PE scoreless import/symbol/KV surface.
39. `pe_textenc_kv_static_regularized`: PE static/KV/text regularized model.
40. `native_symbol_kv_textenc_combo`: native group symbols/KV/text/static combo.

Outcome log:

- 2026-05-06: tranche defined. Run command:
  `scripts/run_azoth_wild_tranche.sh`. Use `RUN_LIMIT`/`RUN_SKIP` to run or
  resume in chunks.
- 2026-05-07: full tranche completed: 40 successes, 0 failures. These are
  sampled screening metrics from snapshot `663343929`; winners still need
  routed full-corpus confirmation and litmus feature parity for `symbols`,
  `kv`, and `textenc`.

Strongest follow-ups:

- `shell_kv_metric_vocab_wide` (`409805a4e6219218`): shell F1 0.9859,
  precision 0.9872, recall 0.9847, AUC/AP 0.9999/0.9987. Deployed shell card
  is F1 0.9465; confirm this first.
- `package_json_kv_lifecycle_textenc` (`0f85c7e43d7ff625`): package.json F1
  0.9984, precision 0.9979, recall 0.9989. Small but real sampled lift over
  deployed F1 0.9967.
- `elf_symbol_vocab_kv_static` (`24bf8f38f56cfc88`) and
  `elf_no_score_symbols_textenc` (`50e82d59038166f4`): both ELF F1 0.9974,
  above deployed sampled F1 0.9958. Confirm only if ELF route recall is still
  worth squeezing.
- `general_scoreless_symbol_kv_textenc` (`62b7038fc9d5a8a4`): global sampled F1
  0.9960, AUC/AP 0.9998/0.9998. Good enough to route-confirm, but previous
  global sampled wins failed under FP-budget calibration.
- `documents_textenc_kv_static` (`c8ece36bb498112a`): documents group F1
  0.9920, AUC/AP 0.9999/0.9996. Worth confirming if documents are high-volume.
- `media_textenc_kv_carrier` (`2a27e207e4f656b0`) and
  `media_metadata_only_no_traits` (`feb398ef253385e6`): media group F1
  0.9867/0.9859. Metadata-only is nearly tied, so media may not need trait
  features.

Reject or deprioritize:

- `source_symbol_kv_textenc_combo` and `source_static_surface_no_traits` reached
  F1 0.9354/0.9246, better than the deployed source model card but far weaker
  than the earlier `source_formula_density_tax` result. Confirm that older
  source candidate instead.
- `pe_symbol_kv_import_surface` and `pe_textenc_kv_static_regularized` were flat
  against deployed PE sampled F1 0.9948.
- `native_symbol_kv_textenc_combo` was weaker than deployed native sampled F1
  0.9984.
- Tiny/awkward routes need better pools or different objectives:
  AppleScript F1 0.3636, Rust sparse-tail F1 0.0146, HTML F1 0.6667, XML F1
  0.7507, Go scoreless F1 0.7938.
