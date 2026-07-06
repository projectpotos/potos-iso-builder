"""Tests for the supported-ISO catalog and its resolver."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from isos import DEFAULT_ISO, SUPPORTED_ISOS, resolve_iso


def test_default_iso_is_in_catalog():
    assert DEFAULT_ISO in SUPPORTED_ISOS


def test_resolve_empty_id_returns_default():
    assert resolve_iso("").id == DEFAULT_ISO
    assert resolve_iso().id == DEFAULT_ISO


def test_resolve_known_id():
    source = resolve_iso("fedora-server-44-1.7")
    assert source.iso_filename == "Fedora-Server-dvd-x86_64-44-1.7.iso"
    assert source.checksum_filename == "Fedora-Server-44-1.7-x86_64-CHECKSUM"
    assert len(source.sha256) == 64
    assert source.iso_url.endswith(source.iso_filename)


def test_resolve_unknown_id_raises_with_supported_ids():
    with pytest.raises(KeyError) as exc:
        resolve_iso("nope")
    assert "nope" in str(exc.value)
    assert DEFAULT_ISO in str(exc.value)
