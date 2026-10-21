"""Shared filegroup membership for experiments and deployment."""

# Multi-file containers, application packages, and filesystem images share
# layout/member-name signals even when their contents have their own models.
# Include stored legacy labels and compressed TAR variants so older rows join
# the same training pool. Bare compression wrappers have no container layout;
# Office/OLE containers keep their document group instead.
ARCHIVE_FILETYPES: tuple[str, ...] = (
    "7z", "apk", "apk_alpine", "apk_android", "cab", "chm", "conda",
    "cpio", "crate", "crx", "deb", "dmg", "ear", "egg", "gem", "ipa",
    "iso", "jar", "npm", "nupkg", "oci_image", "pkg_arch", "pkg_freebsd",
    "pkg_macos", "python_sdist", "rar", "rpa", "rpm", "snap", "squashfs",
    "tar", "tar.bz2", "tar.gz", "tar.xz", "tar.zst", "tgz", "vsix",
    "war", "whl", "xbps", "xpi", "zip",
)
