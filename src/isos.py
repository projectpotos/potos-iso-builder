"""Catalog of source ISOs the builder knows how to fetch and verify."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ISOSource:
    """A downloadable source ISO."""

    id: str
    iso_filename: str
    iso_url: str
    checksum_filename: str
    checksum_url: str
    sha256: str


SUPPORTED_ISOS: dict[str, ISOSource] = {
    "fedora-server-44-1.7": ISOSource(
        id="fedora-server-44-1.7",
        iso_filename="Fedora-Server-dvd-x86_64-44-1.7.iso",
        iso_url=(
            "https://download.fedoraproject.org/pub/fedora/linux/releases/44/"
            "Server/x86_64/iso/Fedora-Server-dvd-x86_64-44-1.7.iso"
        ),
        checksum_filename="Fedora-Server-44-1.7-x86_64-CHECKSUM",
        checksum_url=(
            "https://dl.fedoraproject.org/pub/fedora/linux/releases/44/"
            "Server/x86_64/iso/Fedora-Server-44-1.7-x86_64-CHECKSUM"
        ),
        sha256="85837793bfa36db6bc709b4cecd2ec116951b87d9c53c3d95eb2fac8dcf7cf1f",
    ),
}

DEFAULT_ISO = "fedora-server-44-1.7"


def resolve_iso(iso_id: str = "") -> ISOSource:
    """Look up a supported ISO by id, falling back to ``DEFAULT_ISO``."""
    key = iso_id or DEFAULT_ISO
    try:
        return SUPPORTED_ISOS[key]
    except KeyError:
        supported = ", ".join(sorted(SUPPORTED_ISOS)) or "(none)"
        raise KeyError(f"unsupported ISO {key!r}; supported ids: {supported}") from None
