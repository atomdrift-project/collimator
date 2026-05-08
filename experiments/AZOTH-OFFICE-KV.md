# Azoth Office KV Experiments

Created: 2026-05-07

Script:

```sh
scripts/run_azoth_office_kv_shape_probe.sh
```

Purpose: test whether Office-like filetypes benefit from filetype-local KV and
metric vocabularies that include key existence, empty/nonempty markers,
collection lengths, string lengths, numeric buckets, and categorical values.

Targets:

- `xlsx`: early manifest run beat deployed sampled F1, but external n is tiny.
- `pptx`: early manifest run was weak; the sampled `ms.office.*` surface is very
  sparse, so shape/existence may be more useful than raw values.

Outcome log:

- 2026-05-07: side probe defined. Not yet summarized.
