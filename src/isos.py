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


DEFAULT_ISO = "fedora-server-netinst-45-1.4"

SUPPORTED_ISOS: dict[str, ISOSource] = {
    "fedora-server-netinst-44-1.7": ISOSource(
        id="fedora-server-netinst-44-1.7",
        iso_filename="Fedora-Server-netinst-x86_64-44-1.7.iso",
        iso_url=(
            "https://download.fedoraproject.org/pub/fedora/linux/releases/44/"
            "Server/x86_64/iso/Fedora-Server-netinst-x86_64-44-1.7.iso"
        ),
        checksum_filename="Fedora-Server-44-1.7-x86_64-CHECKSUM",
        checksum_url=(
            "https://dl.fedoraproject.org/pub/fedora/linux/releases/44/"
            "Server/x86_64/iso/Fedora-Server-44-1.7-x86_64-CHECKSUM"
        ),
        sha256="ae20c06bea746913cadea7d80463e13f4bf55bee4df2918111c921c674b70283",
    ),
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
    "fedora-server-netinst-45-1.4": ISOSource(
        id="fedora-server-netinst-45-1.4",
        iso_filename="Fedora-Server-netinst-x86_64-45-1.4.iso",
        iso_url=(
            "https://dl.fedoraproject.org/pub/fedora/linux/releases/45/"
            "Server/x86_64/iso/Fedora-Server-netinst-x86_64-45-1.4.iso"
        ),
        checksum_filename="Fedora-Server-45-1.4-x86_64-CHECKSUM",
        checksum_url=(
            "https://dl.fedoraproject.org/pub/fedora/linux/releases/45/"
            "Server/x86_64/iso/Fedora-Server-45-1.4-x86_64-CHECKSUM"
        ),
        sha256="a1e916f139a05955b943cf183b020780cca9c399b02b8f5ec4354c9e5c1dff1a",
    ),
    "fedora-server-45-1.4": ISOSource(
        id="fedora-server-45-1.4",
        iso_filename="Fedora-Server-dvd-x86_64-45-1.4.iso",
        iso_url=(
            "https://dl.fedoraproject.org/pub/fedora/linux/releases/45/"
            "Server/x86_64/iso/Fedora-Server-dvd-x86_64-45-1.4.iso"
        ),
        checksum_filename="Fedora-Server-45-1.4-x86_64-CHECKSUM",
        checksum_url=(
            "https://dl.fedoraproject.org/pub/fedora/linux/releases/45/"
            "Server/x86_64/iso/Fedora-Server-45-1.4-x86_64-CHECKSUM"
        ),
        sha256="fcc0f623708ddbd7656df152510ba018bad618bfc99879e73809255fb11a48ff",
    ),
}


def resolve_iso(iso_id: str = "") -> ISOSource:
    """Look up a supported ISO by id, falling back to ``DEFAULT_ISO``."""
    key = iso_id or DEFAULT_ISO
    try:
        return SUPPORTED_ISOS[key]
    except KeyError:
        supported = ", ".join(sorted(SUPPORTED_ISOS)) or "(none)"
        raise KeyError(f"unsupported ISO {key!r}; supported ids: {supported}") from None
