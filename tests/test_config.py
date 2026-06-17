"""Tests for the Config dataclass and its from_dict constructor."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config import Config

EXAMPLE_CONFIG = {
    "client_name": {"short": "dailyplanetos", "long": "DailyPlanet Linux Client"},
    "disk_encryption": {"enabled": True, "init_password": "s3cr3t"},
    "specs": {
        "url": "https://github.com/dailyplanetos/ansible-specs-dailyplanetos.git",
        "branch": "v4.2.0",
    },
    "initial_hostname": "dailyplanetos-bootstrap",
    "initial_user": {"username": "clarkkent", "password_hash": "$6$abc"},
    "firstboot": {
        "role_vars": {
            "potos_firstboot_ask_hostname": False,
            "potos_firstboot_credentials_source": "openbao",
            "potos_firstboot_credentials_openbao": {
                "url": "https://bao.example.com",
                "role": "potos",
                "mount": "oidc",
                "secret_path": "kv/potos/specs",
                "field": "specs_token",
            },
        },
        "extra_roles": [{"name": "mycorp.bootstrap.enroll", "src": "git+https://example.com/r.git"}],
    },
    "input": {
        "iso_filename": "Fedora-Server-dvd-x86_64-43-1.6.iso",
        "checksum_filename": "Fedora-Server-43-1.6-x86_64-CHECKSUM",
    },
    "output": {"version": "20260415", "iso_filename": "dailyplanetos-installer.iso"},
}


def test_from_dict_with_full_config():
    config = Config.from_dict(EXAMPLE_CONFIG)

    assert config.client_name.short == "dailyplanetos"
    assert config.client_name.long == "DailyPlanet Linux Client"
    assert config.disk_encryption.enabled is True
    assert config.disk_encryption.init_password == "s3cr3t"
    assert config.specs.url.endswith("dailyplanetos.git")
    assert config.specs.branch == "v4.2.0"
    assert config.initial_hostname == "dailyplanetos-bootstrap"
    assert config.initial_user.username == "clarkkent"
    assert config.initial_user.password_hash == "$6$abc"
    assert config.firstboot.role_vars == {
        "potos_firstboot_ask_hostname": False,
        "potos_firstboot_credentials_source": "openbao",
        "potos_firstboot_credentials_openbao": {
            "url": "https://bao.example.com",
            "role": "potos",
            "mount": "oidc",
            "secret_path": "kv/potos/specs",
            "field": "specs_token",
        },
    }
    assert config.firstboot.extra_roles[0]["name"] == "mycorp.bootstrap.enroll"
    assert config.input.iso_filename == "Fedora-Server-dvd-x86_64-43-1.6.iso"
    assert config.input.checksum_filename == "Fedora-Server-43-1.6-x86_64-CHECKSUM"
    assert config.output.iso_filename == "dailyplanetos-installer.iso"
    assert config.output.version == "20260415"


def test_from_dict_defaults_applied_for_empty_dict():
    config = Config.from_dict({})

    assert config.client_name.short == "potos"
    assert config.client_name.long == "Potos Linux Client"
    assert config.disk_encryption.enabled is False
    assert config.disk_encryption.init_password == "potos"
    assert config.specs.url == ""
    assert config.specs.branch == "main"
    assert config.initial_hostname == "potos-bootstrap"
    assert config.initial_user.username == "potos"
    assert config.firstboot.role_vars == {}
    assert config.firstboot.extra_roles == []
    assert config.input.iso_filename == ""
    assert config.input.checksum_filename == ""
    assert config.output.iso_filename == "potos-installer.iso"


def test_from_dict_partial_config_uses_defaults_for_missing_keys():
    config = Config.from_dict({"client_name": {"short": "dailyplanetos"}})

    assert config.client_name.short == "dailyplanetos"
    assert config.client_name.long == "Potos Linux Client"  # default
    assert config.disk_encryption.enabled is False  # default
    assert config.initial_hostname == "potos-bootstrap"  # default
