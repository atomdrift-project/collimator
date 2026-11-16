"""Renamed signature findings keep the names the deployed model was trained on.

Same cases as scan's `renamed_signature_findings_keep_their_trained_names`
(src/features/tests.rs): training and serving must spell features alike.
"""

import pytest

from collimator.features import finding_id, legacy_finding_id

CASES = [
    ("metadata/signature/verified/platform::apple", "metadata/signed/platform::apple"),
    ("metadata/signature/verified/developer::abcde12345", "metadata/signed/developer::abcde12345"),
    ("metadata/signature/unverified/id::com.apple.ls", "metadata/signed/id::com.apple.ls"),
    ("metadata/signature/self-signed/signer::adobe-inc.", "metadata/signed/leaf::adobe-inc."),
    (
        "metadata/signature/invalid/tampered/subject::microsoft-windows",
        "metadata/signed/unknown::microsoft-windows",
    ),
    (
        "metadata/signature/invalid/bad-signature/signer::valve-corp.",
        "metadata/signed/leaf::valve-corp.",
    ),
    (
        "metadata/signature/invalid/tampered::macho-code-directory",
        "metadata/signed/integrity::macho-code-directory-invalid",
    ),
    (
        "metadata/signature/certificate/integrity::pe-signature-verified",
        "metadata/signed/certificate/signature::pe-signature-verified",
    ),
    (
        "metadata/signature/certificate/issuer/microsoft::microsoft-code-signing-pca-2011",
        "metadata/signed/certificate/issuer/microsoft::microsoft-code-signing-pca-2011",
    ),
    (
        "metadata/signature/certificate/format::phar-signed",
        "metadata/signed/trust-level::phar-signed",
    ),
    ("metadata/signature/absent::unsigned", "metadata/signed/trust-level::unsigned"),
    ("metadata/signature/ad-hoc::adhoc", "metadata/signed/trust-level::adhoc"),
    (
        "metadata/signature/code-directory::apple-identifier-prefix",
        "metadata/signed/code-directory::apple-identifier-prefix",
    ),
    (
        "metadata/signature/code-directory::hardened-runtime-dup",
        "metadata/signed/trust-level::hardened-runtime-dup",
    ),
    (
        "metadata/signature/entitlements::get-task-allow",
        "metadata/signed/entitlements::get-task-allow",
    ),
    (
        "well-known/app/system/microsoft/platform::microsoft-nt-kernel-image",
        "metadata/signed/platform::microsoft-nt-kernel-image",
    ),
    # Not renamed: new concepts and unrelated ids pass through.
    (
        "metadata/signature/claim/signer::microsoft-corporation",
        "metadata/signature/claim/signer::microsoft-corporation",
    ),
    ("metadata/signature/certificates::x", "metadata/signature/certificates::x"),
    (
        "well-known/app/system/microsoft/platform::windows-os-product-name",
        "well-known/app/system/microsoft/platform::windows-os-product-name",
    ),
    ("micro-behaviors/fs/file/open::x", "micro-behaviors/fs/file/open::x"),
]


@pytest.mark.parametrize(("new", "old"), CASES)
def test_legacy_finding_id(new: str, old: str) -> None:
    assert legacy_finding_id(new) == old


def test_finding_id_reads_renamed_ids_under_trained_names() -> None:
    assert (
        finding_id({"id": "metadata/signature/verified/platform::apple"})
        == "metadata/signed/platform::apple"
    )
    assert (
        finding_id({"i": "metadata/signature/absent::unsigned"})
        == "metadata/signed/trust-level::unsigned"
    )
    assert finding_id({}) is None
