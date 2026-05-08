#!/usr/bin/env python3
"""Run the manifest-driven all-filetype Azoth experiment tranche."""

from __future__ import annotations

import os
import re
import subprocess
import sys
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class Template:
    key: str
    note: str
    vars: tuple[str, ...]


def v(*items: str) -> tuple[str, ...]:
    return tuple(items)


TEMPLATES: dict[str, Template] = {
    "doc_kv_textenc_static": Template("doc_kv_textenc_static", "document metadata and text encoding surface", v("EXP_KV_VOCAB=1", "EXP_KV_VOCAB_MAX=10000", "EXP_KV_MIN_FREQ=1", "EXP_TEXT_ENCODING_FEATURES=1", "EXP_FORMAT_HINTS=1", "EXP_TAXONOMY_FEATURES=1", "EXP_EMBER_LITE_FEATURES=1", "COLLIMATOR_METRIC_MIN_FREQ_PCT=0")),
    "doc_metadata_only": Template("doc_metadata_only", "document metadata-only stress test", v("EXP_DISABLE_FEATURE_GROUPS=present,maxcrit,elements,bigrams,trigrams,score,clusters", "EXP_KV_VOCAB=1", "EXP_KV_VOCAB_MAX=14000", "EXP_TEXT_ENCODING_FEATURES=1")),
    "doc_scoreless_hsn8": Template("doc_scoreless_hsn8", "document scoreless deep severity paths", v("EXP_DISABLE_FEATURE_GROUPS=score,clusters", "EXP_TEXT_ENCODING_FEATURES=1", "EXP_TIERED_CRIT_TRIGRAMS=1", "EXP_TIERED_TRIGRAM_PATH_DEPTH=8", "EXP_TIERED_TRIGRAM_MIN_CRIT=0", "EXP_TIERED_TRIGRAM_MAX=10000")),
    "doc_macro_objective": Template("doc_macro_objective", "macro-like objective and ATT&CK signal", v("EXP_KV_VOCAB=1", "EXP_TEXT_ENCODING_FEATURES=1", "COLLIMATOR_OBJECTIVE_TRIGRAMS=1", "COLLIMATOR_ATTACK_NGRAMS=1", "COLLIMATOR_TRIGRAM_MAX=3000")),
    "doc_hardtail_kv": Template("doc_hardtail_kv", "document hard-negative tail", v("EXP_KV_VOCAB=1", "EXP_TEXT_ENCODING_FEATURES=1", "EXP_HARD_NEGATIVE_FRACTION=0.015", "EXP_HARD_NEGATIVE_WEIGHT=18")),
    "doc_precision_regularized": Template("doc_precision_regularized", "low-leaf precision regularization", v("EXP_KV_VOCAB=1", "EXP_TEXT_ENCODING_FEATURES=1", "EXP_NUM_LEAVES=48", "EXP_MIN_CHILD_SAMPLES=80", "EXP_REG_ALPHA=0.5", "EXP_REG_LAMBDA=4.0")),
    "doc_recall_beta2": Template("doc_recall_beta2", "recall-biased document route", v("EXP_KV_VOCAB=1", "EXP_TEXT_ENCODING_FEATURES=1", "EXP_BETA=2.0", "EXP_TIERED_CRIT_TRIGRAMS=1", "EXP_TIERED_TRIGRAM_PATH_DEPTH=8", "EXP_TIERED_TRIGRAM_MIN_CRIT=0")),
    "doc_static_no_score": Template("doc_static_no_score", "static document surface without score", v("EXP_DISABLE_FEATURE_GROUPS=score,clusters", "EXP_KV_VOCAB=1", "EXP_TEXT_ENCODING_FEATURES=1", "EXP_FORMAT_HINTS=1", "EXP_EMBER_LITE_FEATURES=1")),
    "script_kv_objective": Template("script_kv_objective", "script KV/text shape plus objective/attack", v("EXP_KV_VOCAB=1", "EXP_KV_VOCAB_MAX=12000", "EXP_KV_MIN_FREQ=1", "EXP_TEXT_ENCODING_FEATURES=1", "EXP_FORMAT_HINTS=1", "COLLIMATOR_OBJECTIVE_TRIGRAMS=1", "COLLIMATOR_ATTACK_NGRAMS=1", "COLLIMATOR_TRIGRAM_MAX=3500")),
    "script_symbols_kv": Template("script_symbols_kv", "command/import symbols plus KV", v("EXP_SYMBOL_VOCAB=1", "EXP_SYMBOL_VOCAB_MAX=12000", "EXP_SYMBOL_MIN_FREQ=1", "EXP_KV_VOCAB=1", "EXP_KV_VOCAB_MAX=9000", "EXP_TEXT_ENCODING_FEATURES=1")),
    "script_metadata_only": Template("script_metadata_only", "script static surface without traits", v("EXP_DISABLE_FEATURE_GROUPS=present,maxcrit,elements,bigrams,trigrams,score,clusters", "EXP_KV_VOCAB=1", "EXP_KV_VOCAB_MAX=14000", "EXP_TEXT_ENCODING_FEATURES=1")),
    "script_scoreless_hsn10": Template("script_scoreless_hsn10", "script scoreless H/S/N depth 10", v("EXP_DISABLE_FEATURE_GROUPS=score,clusters", "EXP_TEXT_ENCODING_FEATURES=1", "EXP_TIERED_CRIT_TRIGRAMS=1", "EXP_TIERED_TRIGRAM_PATH_DEPTH=10", "EXP_TIERED_TRIGRAM_MIN_CRIT=0", "EXP_TIERED_TRIGRAM_MAX=12000")),
    "script_hardtail_symbols": Template("script_hardtail_symbols", "script hard-negative symbols/KV", v("EXP_SYMBOL_VOCAB=1", "EXP_KV_VOCAB=1", "EXP_TEXT_ENCODING_FEATURES=1", "EXP_HARD_NEGATIVE_FRACTION=0.015", "EXP_HARD_NEGATIVE_WEIGHT=16")),
    "script_precision_regularized": Template("script_precision_regularized", "script precision-regularized KV", v("EXP_KV_VOCAB=1", "EXP_TEXT_ENCODING_FEATURES=1", "EXP_NUM_LEAVES=48", "EXP_MIN_CHILD_SAMPLES=140", "EXP_REG_ALPHA=0.5", "EXP_REG_LAMBDA=4.0")),
    "script_recall_beta2": Template("script_recall_beta2", "script recall-biased H/S/N", v("EXP_KV_VOCAB=1", "EXP_TEXT_ENCODING_FEATURES=1", "EXP_BETA=2.0", "EXP_TIERED_CRIT_TRIGRAMS=1", "EXP_TIERED_TRIGRAM_PATH_DEPTH=8", "EXP_TIERED_TRIGRAM_MIN_CRIT=0")),
    "script_no_presence": Template("script_no_presence", "script no-presence command surface", v("EXP_DISABLE_FEATURE_GROUPS=present,maxcrit,score,clusters", "EXP_SYMBOL_VOCAB=1", "EXP_KV_VOCAB=1", "EXP_TEXT_ENCODING_FEATURES=1", "EXP_FORMAT_HINTS=1")),
    "source_symbols_density": Template("source_symbols_density", "source symbols/KV plus density", v("EXP_SYMBOL_VOCAB=1", "EXP_SYMBOL_VOCAB_MAX=16000", "EXP_SYMBOL_MIN_FREQ=2", "EXP_KV_VOCAB=1", "EXP_KV_VOCAB_MAX=9000", "EXP_TEXT_ENCODING_FEATURES=1", "EXP_HOSTILE_FINDING_DENSITY=1", "EXP_HOSTILE_DEPTH_WEIGHT=1")),
    "source_symbols_static": Template("source_symbols_static", "source symbols/static taxonomy", v("EXP_SYMBOL_VOCAB=1", "EXP_SYMBOL_VOCAB_MAX=16000", "EXP_KV_VOCAB=1", "EXP_TEXT_ENCODING_FEATURES=1", "EXP_FORMAT_HINTS=1", "EXP_TAXONOMY_FEATURES=1")),
    "source_metadata_only": Template("source_metadata_only", "source metadata-only stress test", v("EXP_DISABLE_FEATURE_GROUPS=present,maxcrit,elements,bigrams,trigrams,score,clusters", "EXP_SYMBOL_VOCAB=1", "EXP_SYMBOL_VOCAB_MAX=16000", "EXP_KV_VOCAB=1", "EXP_TEXT_ENCODING_FEATURES=1")),
    "source_scoreless_hsn8": Template("source_scoreless_hsn8", "source scoreless H/S/N depth 8", v("EXP_DISABLE_FEATURE_GROUPS=score,clusters", "EXP_TEXT_ENCODING_FEATURES=1", "EXP_TIERED_CRIT_TRIGRAMS=1", "EXP_TIERED_TRIGRAM_PATH_DEPTH=8", "EXP_TIERED_TRIGRAM_MIN_CRIT=0", "EXP_TIERED_TRIGRAM_MAX=14000")),
    "source_objective_symbols": Template("source_objective_symbols", "source objective/attack symbols", v("EXP_SYMBOL_VOCAB=1", "EXP_SYMBOL_VOCAB_MAX=16000", "EXP_TEXT_ENCODING_FEATURES=1", "COLLIMATOR_OBJECTIVE_TRIGRAMS=1", "COLLIMATOR_ATTACK_NGRAMS=1", "COLLIMATOR_TRIGRAM_MAX=3500")),
    "source_hardtail_kv": Template("source_hardtail_kv", "source hard-tail KV", v("EXP_KV_VOCAB=1", "EXP_TEXT_ENCODING_FEATURES=1", "EXP_HARD_NEGATIVE_FRACTION=0.01", "EXP_HARD_NEGATIVE_WEIGHT=14", "EXP_NUM_LEAVES=160", "EXP_MIN_CHILD_SAMPLES=70")),
    "source_precision_regularized": Template("source_precision_regularized", "source precision-regularized surface", v("EXP_SYMBOL_VOCAB=1", "EXP_KV_VOCAB=1", "EXP_TEXT_ENCODING_FEATURES=1", "EXP_NUM_LEAVES=64", "EXP_MIN_CHILD_SAMPLES=180", "EXP_REG_ALPHA=0.5", "EXP_REG_LAMBDA=4.0")),
    "source_textenc_only": Template("source_textenc_only", "source textenc H/S/N only", v("EXP_DISABLE_FEATURE_GROUPS=score,clusters", "EXP_TEXT_ENCODING_FEATURES=1", "EXP_TIERED_CRIT_TRIGRAMS=1", "EXP_TIERED_TRIGRAM_PATH_DEPTH=6", "EXP_TIERED_TRIGRAM_MIN_CRIT=0")),
    "native_symbol_kv_static": Template("native_symbol_kv_static", "native symbols/KV/static", v("EXP_SYMBOL_VOCAB=1", "EXP_SYMBOL_VOCAB_MAX=18000", "EXP_SYMBOL_MIN_FREQ=2", "EXP_KV_VOCAB=1", "EXP_KV_VOCAB_MAX=10000", "EXP_TEXT_ENCODING_FEATURES=1", "EXP_FORMAT_HINTS=1", "EXP_TAXONOMY_FEATURES=1", "EXP_EMBER_LITE_FEATURES=1")),
    "native_scoreless_symbols": Template("native_scoreless_symbols", "native scoreless symbols/textenc", v("EXP_DISABLE_FEATURE_GROUPS=score,clusters", "EXP_SYMBOL_VOCAB=1", "EXP_SYMBOL_VOCAB_MAX=18000", "EXP_TEXT_ENCODING_FEATURES=1", "EXP_TIERED_CRIT_TRIGRAMS=1", "EXP_TIERED_TRIGRAM_PATH_DEPTH=8", "EXP_TIERED_TRIGRAM_MIN_CRIT=0")),
    "native_kv_static_regularized": Template("native_kv_static_regularized", "native KV/static regularized", v("EXP_KV_VOCAB=1", "EXP_KV_VOCAB_MAX=12000", "EXP_TEXT_ENCODING_FEATURES=1", "EXP_FORMAT_HINTS=1", "EXP_TAXONOMY_FEATURES=1", "EXP_EMBER_LITE_FEATURES=1", "EXP_REG_ALPHA=0.35", "EXP_REG_LAMBDA=3.0", "EXP_COLSAMPLE_BYTREE=0.7")),
    "native_hardtail_symbols": Template("native_hardtail_symbols", "native hard-tail symbols", v("EXP_SYMBOL_VOCAB=1", "EXP_SYMBOL_VOCAB_MAX=18000", "EXP_TEXT_ENCODING_FEATURES=1", "EXP_HARD_NEGATIVE_FRACTION=0.012", "EXP_HARD_NEGATIVE_WEIGHT=18", "EXP_NUM_LEAVES=160", "EXP_MIN_CHILD_SAMPLES=60")),
    "native_metadata_only": Template("native_metadata_only", "native metadata-only static", v("EXP_DISABLE_FEATURE_GROUPS=present,maxcrit,elements,bigrams,trigrams,score,clusters", "EXP_SYMBOL_VOCAB=1", "EXP_SYMBOL_VOCAB_MAX=18000", "EXP_KV_VOCAB=1", "EXP_TEXT_ENCODING_FEATURES=1", "EXP_EMBER_LITE_FEATURES=1")),
    "native_precision_regularized": Template("native_precision_regularized", "native precision regularized", v("EXP_KV_VOCAB=1", "EXP_TEXT_ENCODING_FEATURES=1", "EXP_NUM_LEAVES=64", "EXP_MIN_CHILD_SAMPLES=200", "EXP_REG_ALPHA=0.5", "EXP_REG_LAMBDA=4.0")),
    "native_recall_beta2": Template("native_recall_beta2", "native recall-biased", v("EXP_SYMBOL_VOCAB=1", "EXP_TEXT_ENCODING_FEATURES=1", "EXP_BETA=2.0", "EXP_TIERED_CRIT_TRIGRAMS=1", "EXP_TIERED_TRIGRAM_PATH_DEPTH=8", "EXP_TIERED_TRIGRAM_MIN_CRIT=0")),
    "native_static_no_score": Template("native_static_no_score", "native static without score", v("EXP_DISABLE_FEATURE_GROUPS=score,clusters", "EXP_FORMAT_HINTS=1", "EXP_TAXONOMY_FEATURES=1", "EXP_EMBER_LITE_FEATURES=1", "EXP_KV_VOCAB=1")),
    "archive_kv_manifest": Template("archive_kv_manifest", "archive manifest/KV surface", v("EXP_KV_VOCAB=1", "EXP_KV_VOCAB_MAX=12000", "EXP_KV_MIN_FREQ=1", "EXP_TEXT_ENCODING_FEATURES=1", "EXP_FORMAT_HINTS=1", "EXP_EMBER_LITE_FEATURES=1")),
    "archive_metadata_only": Template("archive_metadata_only", "archive metadata-only", v("EXP_DISABLE_FEATURE_GROUPS=present,maxcrit,elements,bigrams,trigrams,score,clusters", "EXP_KV_VOCAB=1", "EXP_KV_VOCAB_MAX=16000", "EXP_TEXT_ENCODING_FEATURES=1")),
    "archive_scoreless_inner": Template("archive_scoreless_inner", "archive scoreless inner path H/S/N", v("EXP_DISABLE_FEATURE_GROUPS=score,clusters", "EXP_TEXT_ENCODING_FEATURES=1", "EXP_TIERED_CRIT_TRIGRAMS=1", "EXP_TIERED_TRIGRAM_PATH_DEPTH=10", "EXP_TIERED_TRIGRAM_MIN_CRIT=0", "EXP_TIERED_TRIGRAM_MAX=12000")),
    "archive_hardtail_kv": Template("archive_hardtail_kv", "archive hard-tail KV", v("EXP_KV_VOCAB=1", "EXP_TEXT_ENCODING_FEATURES=1", "EXP_HARD_NEGATIVE_FRACTION=0.012", "EXP_HARD_NEGATIVE_WEIGHT=16")),
    "archive_precision_regularized": Template("archive_precision_regularized", "archive precision regularized", v("EXP_KV_VOCAB=1", "EXP_TEXT_ENCODING_FEATURES=1", "EXP_NUM_LEAVES=64", "EXP_MIN_CHILD_SAMPLES=160", "EXP_REG_ALPHA=0.5", "EXP_REG_LAMBDA=4.0")),
    "archive_recall_beta2": Template("archive_recall_beta2", "archive recall-biased", v("EXP_KV_VOCAB=1", "EXP_TEXT_ENCODING_FEATURES=1", "EXP_BETA=2.0", "EXP_TIERED_CRIT_TRIGRAMS=1", "EXP_TIERED_TRIGRAM_PATH_DEPTH=8", "EXP_TIERED_TRIGRAM_MIN_CRIT=0")),
    "archive_no_presence": Template("archive_no_presence", "archive no-presence surface", v("EXP_DISABLE_FEATURE_GROUPS=present,maxcrit,score,clusters", "EXP_KV_VOCAB=1", "EXP_TEXT_ENCODING_FEATURES=1", "EXP_FORMAT_HINTS=1")),
    "archive_textenc_only": Template("archive_textenc_only", "archive textenc-only H/S/N", v("EXP_DISABLE_FEATURE_GROUPS=score,clusters", "EXP_TEXT_ENCODING_FEATURES=1", "EXP_TIERED_CRIT_TRIGRAMS=1", "EXP_TIERED_TRIGRAM_PATH_DEPTH=6", "EXP_TIERED_TRIGRAM_MIN_CRIT=0")),
    "media_kv_textenc": Template("media_kv_textenc", "media metadata/text encoding", v("EXP_KV_VOCAB=1", "EXP_KV_VOCAB_MAX=10000", "EXP_KV_MIN_FREQ=1", "EXP_TEXT_ENCODING_FEATURES=1", "EXP_FORMAT_HINTS=1", "COLLIMATOR_METRIC_MIN_FREQ_PCT=0")),
    "media_metadata_only": Template("media_metadata_only", "media metadata-only", v("EXP_DISABLE_FEATURE_GROUPS=present,maxcrit,elements,bigrams,trigrams,score,clusters", "EXP_KV_VOCAB=1", "EXP_KV_VOCAB_MAX=14000", "EXP_TEXT_ENCODING_FEATURES=1", "EXP_FORMAT_HINTS=1")),
    "media_scoreless_hsn": Template("media_scoreless_hsn", "media scoreless carrier H/S/N", v("EXP_DISABLE_FEATURE_GROUPS=score,clusters", "EXP_KV_VOCAB=1", "EXP_TEXT_ENCODING_FEATURES=1", "EXP_TIERED_CRIT_TRIGRAMS=1", "EXP_TIERED_TRIGRAM_PATH_DEPTH=8", "EXP_TIERED_TRIGRAM_MIN_CRIT=0")),
    "media_hardtail_kv": Template("media_hardtail_kv", "media hard-tail KV", v("EXP_KV_VOCAB=1", "EXP_TEXT_ENCODING_FEATURES=1", "EXP_HARD_NEGATIVE_FRACTION=0.012", "EXP_HARD_NEGATIVE_WEIGHT=16")),
    "media_precision_regularized": Template("media_precision_regularized", "media precision regularized", v("EXP_KV_VOCAB=1", "EXP_TEXT_ENCODING_FEATURES=1", "EXP_NUM_LEAVES=48", "EXP_MIN_CHILD_SAMPLES=120", "EXP_REG_ALPHA=0.5", "EXP_REG_LAMBDA=4.0")),
    "media_recall_beta2": Template("media_recall_beta2", "media recall-biased", v("EXP_KV_VOCAB=1", "EXP_TEXT_ENCODING_FEATURES=1", "EXP_BETA=2.0")),
    "media_no_presence": Template("media_no_presence", "media no-presence metadata", v("EXP_DISABLE_FEATURE_GROUPS=present,maxcrit,score,clusters", "EXP_KV_VOCAB=1", "EXP_TEXT_ENCODING_FEATURES=1", "EXP_FORMAT_HINTS=1")),
    "media_textenc_only": Template("media_textenc_only", "media text encoding only", v("EXP_DISABLE_FEATURE_GROUPS=score,clusters", "EXP_TEXT_ENCODING_FEATURES=1", "EXP_FORMAT_HINTS=1")),
    "metadata_lifecycle": Template("metadata_lifecycle", "metadata lifecycle/KV/symbols", v("EXP_SYMBOL_VOCAB=1", "EXP_SYMBOL_VOCAB_MAX=9000", "EXP_KV_VOCAB=1", "EXP_KV_VOCAB_MAX=16000", "EXP_KV_MIN_FREQ=1", "EXP_TEXT_ENCODING_FEATURES=1", "COLLIMATOR_OBJECTIVE_TRIGRAMS=1")),
    "metadata_only_reg": Template("metadata_only_reg", "metadata-only regularized", v("EXP_DISABLE_FEATURE_GROUPS=present,maxcrit,elements,bigrams,trigrams,score,clusters", "EXP_KV_VOCAB=1", "EXP_KV_VOCAB_MAX=18000", "EXP_KV_MIN_FREQ=1", "EXP_TEXT_ENCODING_FEATURES=1", "EXP_REG_ALPHA=0.25", "EXP_REG_LAMBDA=2.5")),
    "metadata_scoreless_hsn": Template("metadata_scoreless_hsn", "metadata scoreless H/S/N", v("EXP_DISABLE_FEATURE_GROUPS=score,clusters", "EXP_KV_VOCAB=1", "EXP_TEXT_ENCODING_FEATURES=1", "EXP_TIERED_CRIT_TRIGRAMS=1", "EXP_TIERED_TRIGRAM_PATH_DEPTH=8", "EXP_TIERED_TRIGRAM_MIN_CRIT=0", "EXP_TIERED_TRIGRAM_MAX=10000")),
    "metadata_hardtail": Template("metadata_hardtail", "metadata hard-tail precision", v("EXP_KV_VOCAB=1", "EXP_KV_VOCAB_MAX=14000", "EXP_TEXT_ENCODING_FEATURES=1", "EXP_HARD_NEGATIVE_FRACTION=0.015", "EXP_HARD_NEGATIVE_WEIGHT=16", "EXP_NUM_LEAVES=64", "EXP_MIN_CHILD_SAMPLES=120")),
    "metadata_recall_beta2": Template("metadata_recall_beta2", "metadata recall-biased", v("EXP_KV_VOCAB=1", "EXP_TEXT_ENCODING_FEATURES=1", "EXP_BETA=2.0", "COLLIMATOR_OBJECTIVE_TRIGRAMS=1", "COLLIMATOR_ATTACK_NGRAMS=1")),
    "metadata_textenc_only": Template("metadata_textenc_only", "metadata textenc only", v("EXP_DISABLE_FEATURE_GROUPS=score,clusters", "EXP_TEXT_ENCODING_FEATURES=1", "COLLIMATOR_OBJECTIVE_TRIGRAMS=1", "COLLIMATOR_TRIGRAM_MAX=2500")),
    "metadata_kv_no_textenc": Template("metadata_kv_no_textenc", "metadata KV without textenc", v("EXP_KV_VOCAB=1", "EXP_KV_VOCAB_MAX=18000", "EXP_KV_MIN_FREQ=1", "EXP_TEXT_ENCODING_FEATURES=0", "EXP_FORMAT_HINTS=1")),
    "metadata_no_presence": Template("metadata_no_presence", "metadata no-presence KV", v("EXP_DISABLE_FEATURE_GROUPS=present,maxcrit,score,clusters", "EXP_KV_VOCAB=1", "EXP_KV_VOCAB_MAX=18000", "EXP_TEXT_ENCODING_FEATURES=1")),
    "portable_symbol_bytecode": Template("portable_symbol_bytecode", "portable bytecode symbols/KV", v("EXP_SYMBOL_VOCAB=1", "EXP_SYMBOL_VOCAB_MAX=12000", "EXP_KV_VOCAB=1", "EXP_KV_VOCAB_MAX=9000", "EXP_TEXT_ENCODING_FEATURES=1", "EXP_FORMAT_HINTS=1", "EXP_TAXONOMY_FEATURES=1")),
    "portable_metadata_only": Template("portable_metadata_only", "portable metadata-only", v("EXP_DISABLE_FEATURE_GROUPS=present,maxcrit,elements,bigrams,trigrams,score,clusters", "EXP_SYMBOL_VOCAB=1", "EXP_KV_VOCAB=1", "EXP_TEXT_ENCODING_FEATURES=1")),
    "portable_scoreless_hsn8": Template("portable_scoreless_hsn8", "portable scoreless H/S/N", v("EXP_DISABLE_FEATURE_GROUPS=score,clusters", "EXP_TEXT_ENCODING_FEATURES=1", "EXP_TIERED_CRIT_TRIGRAMS=1", "EXP_TIERED_TRIGRAM_PATH_DEPTH=8", "EXP_TIERED_TRIGRAM_MIN_CRIT=0", "EXP_TIERED_TRIGRAM_MAX=12000")),
    "portable_objective_symbols": Template("portable_objective_symbols", "portable objective symbols", v("EXP_SYMBOL_VOCAB=1", "EXP_TEXT_ENCODING_FEATURES=1", "COLLIMATOR_OBJECTIVE_TRIGRAMS=1", "COLLIMATOR_ATTACK_NGRAMS=1", "COLLIMATOR_TRIGRAM_MAX=3500")),
    "portable_hardtail_kv": Template("portable_hardtail_kv", "portable hard-tail KV", v("EXP_KV_VOCAB=1", "EXP_TEXT_ENCODING_FEATURES=1", "EXP_HARD_NEGATIVE_FRACTION=0.012", "EXP_HARD_NEGATIVE_WEIGHT=16")),
    "portable_precision_regularized": Template("portable_precision_regularized", "portable precision regularized", v("EXP_KV_VOCAB=1", "EXP_TEXT_ENCODING_FEATURES=1", "EXP_NUM_LEAVES=64", "EXP_MIN_CHILD_SAMPLES=160", "EXP_REG_ALPHA=0.5", "EXP_REG_LAMBDA=4.0")),
    "portable_recall_beta2": Template("portable_recall_beta2", "portable recall-biased", v("EXP_SYMBOL_VOCAB=1", "EXP_TEXT_ENCODING_FEATURES=1", "EXP_BETA=2.0", "EXP_TIERED_CRIT_TRIGRAMS=1", "EXP_TIERED_TRIGRAM_PATH_DEPTH=8", "EXP_TIERED_TRIGRAM_MIN_CRIT=0")),
    "portable_static_no_score": Template("portable_static_no_score", "portable static no-score", v("EXP_DISABLE_FEATURE_GROUPS=score,clusters", "EXP_KV_VOCAB=1", "EXP_TEXT_ENCODING_FEATURES=1", "EXP_FORMAT_HINTS=1")),
    "generic_kv_textenc": Template("generic_kv_textenc", "generic KV/textenc static", v("EXP_KV_VOCAB=1", "EXP_KV_VOCAB_MAX=12000", "EXP_KV_MIN_FREQ=1", "EXP_TEXT_ENCODING_FEATURES=1", "EXP_FORMAT_HINTS=1", "COLLIMATOR_METRIC_MIN_FREQ_PCT=0")),
    "generic_symbols_kv": Template("generic_symbols_kv", "generic symbols/KV/textenc", v("EXP_SYMBOL_VOCAB=1", "EXP_SYMBOL_VOCAB_MAX=10000", "EXP_KV_VOCAB=1", "EXP_TEXT_ENCODING_FEATURES=1")),
    "generic_metadata_only": Template("generic_metadata_only", "generic metadata-only", v("EXP_DISABLE_FEATURE_GROUPS=present,maxcrit,elements,bigrams,trigrams,score,clusters", "EXP_KV_VOCAB=1", "EXP_KV_VOCAB_MAX=14000", "EXP_TEXT_ENCODING_FEATURES=1")),
    "generic_scoreless_hsn8": Template("generic_scoreless_hsn8", "generic scoreless H/S/N", v("EXP_DISABLE_FEATURE_GROUPS=score,clusters", "EXP_TEXT_ENCODING_FEATURES=1", "EXP_TIERED_CRIT_TRIGRAMS=1", "EXP_TIERED_TRIGRAM_PATH_DEPTH=8", "EXP_TIERED_TRIGRAM_MIN_CRIT=0")),
    "generic_hardtail_kv": Template("generic_hardtail_kv", "generic hard-tail KV", v("EXP_KV_VOCAB=1", "EXP_TEXT_ENCODING_FEATURES=1", "EXP_HARD_NEGATIVE_FRACTION=0.012", "EXP_HARD_NEGATIVE_WEIGHT=16")),
    "generic_precision_regularized": Template("generic_precision_regularized", "generic precision regularized", v("EXP_KV_VOCAB=1", "EXP_TEXT_ENCODING_FEATURES=1", "EXP_NUM_LEAVES=64", "EXP_MIN_CHILD_SAMPLES=160", "EXP_REG_ALPHA=0.5", "EXP_REG_LAMBDA=4.0")),
    "generic_recall_beta2": Template("generic_recall_beta2", "generic recall-biased", v("EXP_KV_VOCAB=1", "EXP_TEXT_ENCODING_FEATURES=1", "EXP_BETA=2.0")),
    "generic_no_presence": Template("generic_no_presence", "generic no-presence surface", v("EXP_DISABLE_FEATURE_GROUPS=present,maxcrit,score,clusters", "EXP_KV_VOCAB=1", "EXP_TEXT_ENCODING_FEATURES=1", "EXP_FORMAT_HINTS=1")),
}


def plan(ft: str, rationale: str, keys: Iterable[str]) -> dict[str, object]:
    key_list = list(keys)
    if len(key_list) != 8:
        raise ValueError(f"{ft} has {len(key_list)} experiments, expected 8")
    return {"filetype": ft, "rationale": rationale, "keys": key_list}


DOC = ["doc_kv_textenc_static", "doc_metadata_only", "doc_scoreless_hsn8", "doc_macro_objective", "doc_hardtail_kv", "doc_precision_regularized", "doc_recall_beta2", "doc_static_no_score"]
SCRIPT = ["script_kv_objective", "script_symbols_kv", "script_metadata_only", "script_scoreless_hsn10", "script_hardtail_symbols", "script_precision_regularized", "script_recall_beta2", "script_no_presence"]
SOURCE = ["source_symbols_density", "source_symbols_static", "source_metadata_only", "source_scoreless_hsn8", "source_objective_symbols", "source_hardtail_kv", "source_precision_regularized", "source_textenc_only"]
NATIVE = ["native_symbol_kv_static", "native_scoreless_symbols", "native_kv_static_regularized", "native_hardtail_symbols", "native_metadata_only", "native_precision_regularized", "native_recall_beta2", "native_static_no_score"]
ARCHIVE = ["archive_kv_manifest", "archive_metadata_only", "archive_scoreless_inner", "archive_hardtail_kv", "archive_precision_regularized", "archive_recall_beta2", "archive_no_presence", "archive_textenc_only"]
MEDIA = ["media_kv_textenc", "media_metadata_only", "media_scoreless_hsn", "media_hardtail_kv", "media_precision_regularized", "media_recall_beta2", "media_no_presence", "media_textenc_only"]
METADATA = ["metadata_lifecycle", "metadata_only_reg", "metadata_scoreless_hsn", "metadata_hardtail", "metadata_recall_beta2", "metadata_textenc_only", "metadata_kv_no_textenc", "metadata_no_presence"]
PORTABLE = ["portable_symbol_bytecode", "portable_metadata_only", "portable_scoreless_hsn8", "portable_objective_symbols", "portable_hardtail_kv", "portable_precision_regularized", "portable_recall_beta2", "portable_static_no_score"]
GENERIC = ["generic_kv_textenc", "generic_symbols_kv", "generic_metadata_only", "generic_scoreless_hsn8", "generic_hardtail_kv", "generic_precision_regularized", "generic_recall_beta2", "generic_no_presence"]


PLANS = [
    plan("chrome-manifest", "small browser manifest route; metadata/document surface is most likely to separate supply-chain abuse", ["metadata_lifecycle", "metadata_only_reg", "doc_kv_textenc_static", "doc_metadata_only", "metadata_scoreless_hsn", "metadata_hardtail", "metadata_recall_beta2", "metadata_no_presence"]),
    plan("pptx", "small OOXML document route; macro-like metadata and text encoding are the useful surfaces", DOC),
    plan("xlsx", "small OOXML spreadsheet route; metadata and macro-like signals matter more than raw traits", DOC),
    plan("msi", "small Windows installer route; native/static plus package metadata should beat generic traits", ["native_symbol_kv_static", "native_kv_static_regularized", "metadata_lifecycle", "archive_kv_manifest", "native_hardtail_symbols", "native_precision_regularized", "native_static_no_score", "metadata_no_presence"]),
    plan("docx", "OOXML document route with enough data for metadata, no-score, and macro-style probes", DOC),
    plan("rtf", "escape-heavy document route; text encoding and no-score H/S/N are the main bets", DOC),
    plan("tar", "archive route; inner path/manifest metadata should dominate", ARCHIVE),
    plan("powershell", "script route with encoded-command and command-surface signals", SCRIPT),
    plan("vbs", "legacy script route; command/objective plus text encoding should carry", SCRIPT),
    plan("jar", "portable bytecode/archive hybrid; symbols, manifests, and bytecode metadata are the bets", ["portable_symbol_bytecode", "archive_kv_manifest", "portable_metadata_only", "portable_scoreless_hsn8", "portable_objective_symbols", "portable_hardtail_kv", "portable_precision_regularized", "portable_static_no_score"]),
    plan("html", "script/document hybrid; objective, symbols, and text/url shape are the bets", SCRIPT),
    plan("batch", "command-script route; command surface and text encoding are more useful than global score", SCRIPT),
    plan("pdf", "document route; metadata/textenc and macro-like objective proxies are most plausible", DOC),
    plan("groovy", "JVM script route with sparse malware; script probes with regularization and hard-tail", SCRIPT),
    plan("github-actions", "CI workflow route; metadata/lifecycle and command-surface probes", ["metadata_lifecycle", "script_kv_objective", "metadata_only_reg", "script_symbols_kv", "script_metadata_only", "metadata_hardtail", "script_precision_regularized", "metadata_no_presence"]),
    plan("deb", "package/archive route; manifests and install-script metadata are key", ["archive_kv_manifest", "metadata_lifecycle", "archive_metadata_only", "archive_scoreless_inner", "archive_hardtail_kv", "metadata_hardtail", "archive_precision_regularized", "archive_no_presence"]),
    plan("ole", "legacy document container; document metadata, macro proxies, and textenc", DOC),
    plan("macho", "native binary route; symbols/static metadata and hard-tail precision", NATIVE),
    plan("data", "mixed opaque data route; generic KV/textenc and conservative regularization", GENERIC),
    plan("lua", "script route; command/objective and text encoding should help low-volume malware", SCRIPT),
    plan("jpeg", "media route; metadata-only may be enough, but test carrier/textenc variants", MEDIA),
    plan("plist", "Apple metadata/config route; lifecycle/KV metadata and textenc", METADATA),
    plan("objc", "source route with very low malware count; symbols and regularization are priority", SOURCE),
    plan("zst", "compressed archive route; manifest/inner-path and metadata-only probes", ARCHIVE),
    plan("pkg-info", "package metadata route; lifecycle/KV probes should dominate", METADATA),
    plan("makefile", "build script route; command/objective and no-presence surfaces", SCRIPT),
    plan("unknown", "mixed unknown route; broad generic probes, hard-tail, and no-presence", GENERIC),
    plan("swift", "source route with sparse malware; symbols plus regularization", SOURCE),
    plan("perl", "script route; command/objective and text encoding", SCRIPT),
    plan("java", "source route; symbol/static and objective probes", SOURCE),
    plan("tar.gz", "archive route; inner paths and manifest/KV", ARCHIVE),
    plan("gz", "compressed archive/data route; archive plus textenc probes", ARCHIVE),
    plan("ruby", "script route; command/objective and lifecycle-like metadata", SCRIPT),
    plan("kotlin", "source route; symbols/static and regularized probes", SOURCE),
    plan("package.json", "supply-chain metadata route; lifecycle/KV field probes", METADATA),
    plan("zip", "archive route; inner path, manifest, and hard-tail probes", ARCHIVE),
    plan("shell", "high-interest script route; previous KV/textenc result was strongest", SCRIPT),
    plan("php", "web script route; command/objective, text/url shape, and hard-tail", SCRIPT),
    plan("csharp", "source/portable-adjacent route; source symbols plus objective probes", SOURCE),
    plan("rust", "source route with very low malware count; regularization and hard-tail are critical", SOURCE),
    plan("text", "generic text route; text encoding and KV/no-presence probes", GENERIC),
    plan("python-bytecode", "portable bytecode route; symbol/KV/static bytecode probes", PORTABLE),
    plan("go", "source route; symbols/import/static and sparse malware regularization", SOURCE),
    plan("elf", "strong native route; symbols/KV/static and no-score probes may squeeze recall", NATIVE),
    plan("python", "high-interest script route; objective, symbols, and hard-tail variants", SCRIPT),
    plan("png", "media route; metadata-only and carrier probes", MEDIA),
    plan("xml", "metadata/config route; KV/schema-like probes and regularization", METADATA),
    plan("java_class", "portable bytecode route; symbols/static/KV and hard-tail probes", PORTABLE),
    plan("c", "large source route; symbols/static and regularized sparse probes", SOURCE),
    plan("javascript", "high-interest script route; objective/attack plus symbols/KV/textenc", SCRIPT),
    plan("pe", "large native route; static/KV/symbol probes, but avoid overcommitting to flat prior ideas", NATIVE),
]


PROFILE_OVERRIDES = {
    "pe": ("EXP_TRAIN_SAMPLES=90000", "EXP_MAX_TEST_SAMPLES=25000", "EXP_ESTIMATORS=130"),
    "javascript": ("EXP_TRAIN_SAMPLES=90000", "EXP_MAX_TEST_SAMPLES=25000", "EXP_ESTIMATORS=130"),
    "c": ("EXP_TRAIN_SAMPLES=90000", "EXP_MAX_TEST_SAMPLES=25000", "EXP_ESTIMATORS=130"),
    "python": ("EXP_TRAIN_SAMPLES=90000", "EXP_MAX_TEST_SAMPLES=25000", "EXP_ESTIMATORS=130"),
    "xml": ("EXP_TRAIN_SAMPLES=90000", "EXP_MAX_TEST_SAMPLES=25000", "EXP_ESTIMATORS=130"),
    "chrome-manifest": ("EXP_ESTIMATORS=120", "EXP_MIN_CHILD_SAMPLES=30"),
    "pptx": ("EXP_ESTIMATORS=120", "EXP_MIN_CHILD_SAMPLES=30"),
    "xlsx": ("EXP_ESTIMATORS=120", "EXP_MIN_CHILD_SAMPLES=30"),
    "msi": ("EXP_ESTIMATORS=120", "EXP_MIN_CHILD_SAMPLES=30"),
    "docx": ("EXP_ESTIMATORS=120", "EXP_MIN_CHILD_SAMPLES=40"),
    "rtf": ("EXP_ESTIMATORS=120", "EXP_MIN_CHILD_SAMPLES=40"),
    "powershell": ("EXP_ESTIMATORS=120", "EXP_MIN_CHILD_SAMPLES=40"),
    "vbs": ("EXP_ESTIMATORS=120", "EXP_MIN_CHILD_SAMPLES=40"),
    "html": ("EXP_ESTIMATORS=120", "EXP_MIN_CHILD_SAMPLES=40"),
    "batch": ("EXP_ESTIMATORS=120", "EXP_MIN_CHILD_SAMPLES=40"),
    "pdf": ("EXP_ESTIMATORS=120", "EXP_MIN_CHILD_SAMPLES=40"),
    "groovy": ("EXP_ESTIMATORS=120", "EXP_MIN_CHILD_SAMPLES=30"),
    "macho": ("EXP_ESTIMATORS=120", "EXP_MIN_CHILD_SAMPLES=40"),
    "objc": ("EXP_ESTIMATORS=120", "EXP_MIN_CHILD_SAMPLES=20"),
    "rust": ("EXP_ESTIMATORS=120", "EXP_MIN_CHILD_SAMPLES=20"),
}


COMMON_DEFAULTS = (
    ("MODEL", "azoth"),
    ("LEARNER", "azoth"),
    ("EXP_WORKERS", "64"),
    ("EXP_TRAIN_SAMPLES", "80000"),
    ("EXP_MAX_TEST_SAMPLES", "22000"),
    ("EXP_FOLDS", "0"),
    ("EXP_HOLDOUT_FRACTION", "0.12"),
    ("EXP_ESTIMATORS", "120"),
    ("EXP_NUM_LEAVES", "96"),
    ("EXP_MIN_CHILD_SAMPLES", "100"),
    ("EXP_REFRESH_CACHE_SNAPSHOT", "0"),
)


def slugify(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_").lower()
    return slug or "unknown"


def apply_defaults(items: Iterable[tuple[str, str]]) -> list[str]:
    return [f"{key}={os.environ.get(key, default)}" for key, default in items]


def command_for(ft: str, template: Template) -> list[str]:
    slug = slugify(ft)
    idea = f"{slug}_{template.key}"
    cmd = ["make", "experiment"]
    cmd.extend(apply_defaults(COMMON_DEFAULTS))
    for item in PROFILE_OVERRIDES.get(ft, ()):
        key, _sep, default = item.partition("=")
        if key not in os.environ:
            cmd.append(item)
    cmd.extend(
        [
            f"EXP_ROUTE=filetypes/{ft}",
            f"EXP_IDEA={idea}",
            f"EXP_TAG=_{idea}",
            "EXP_MIN_SAMPLE_SCORE=0",
        ]
    )
    cmd.extend(template.vars)
    return cmd


def iter_runs():
    for plan_item in PLANS:
        ft = str(plan_item["filetype"])
        for key in plan_item["keys"]:
            yield ft, TEMPLATES[str(key)]


def print_plan() -> None:
    print(f"filetypes={len(PLANS)} experiments={len(PLANS) * 8}")
    for idx, plan_item in enumerate(PLANS, 1):
        print(f"{idx:02d}. {plan_item['filetype']}: {plan_item['rationale']}")
        for key in plan_item["keys"]:
            tmpl = TEMPLATES[str(key)]
            print(f"    - {tmpl.key}: {tmpl.note}")


def main() -> int:
    if "--list" in sys.argv:
        print_plan()
        return 0

    skip = int(os.environ.get("RUN_SKIP", "0") or "0")
    limit = int(os.environ.get("RUN_LIMIT", "0") or "0")
    dry_run = os.environ.get("DRY_RUN", "0").lower() in {"1", "true", "yes"}

    print(
        f"azoth all-filetype manifest tranche started: filetypes={len(PLANS)} "
        f"experiments={len(PLANS) * 8} skip={skip} limit={limit} dry_run={dry_run}",
        flush=True,
    )

    failures: list[str] = []
    successes = 0
    ran = 0
    seen = 0
    for ft, template in iter_runs():
        seen += 1
        slug = slugify(ft)
        idea = f"{slug}_{template.key}"
        if skip and seen <= skip:
            print(f"skip [{seen}] route=filetypes/{ft} idea={idea}", flush=True)
            continue
        if limit and ran >= limit:
            continue
        ran += 1
        print()
        print("=" * 64)
        print(f"[{ran}] route=filetypes/{ft} idea={idea}")
        print(f"note: {template.note}")
        print("=" * 64, flush=True)
        cmd = command_for(ft, template)
        if dry_run:
            print(" ".join(cmd), flush=True)
            successes += 1
            continue
        result = subprocess.run(cmd)
        if result.returncode == 0:
            successes += 1
        else:
            failures.append(f"filetypes/{ft}:{idea}")

    print()
    print(f"azoth all-filetype manifest tranche complete: successes={successes} failures={len(failures)} ran={ran}")
    if failures:
        for failure in failures:
            print(f"failed: {failure}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
