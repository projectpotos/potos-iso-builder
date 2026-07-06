"""Tests for the Config dataclass and its from_dict constructor."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config import UKI, Bootloader, Config, Credentials, Debug, Firstboot, Partitioning, Payload

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
            "firstboot_ask_hostname": False,
            "firstboot_ask_keyboardlayout": False,
        },
        "extra_roles": [{"name": "mycorp.bootstrap.enroll", "src": "git+https://example.com/r.git"}],
    },
    "input": {"iso": "fedora-server-44-1.7"},
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
        "firstboot_ask_hostname": False,
        "firstboot_ask_keyboardlayout": False,
    }
    assert config.firstboot.extra_roles[0]["name"] == "mycorp.bootstrap.enroll"
    assert config.input.iso == "fedora-server-44-1.7"
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
    assert config.input.iso == ""
    assert config.output.iso_filename == "potos-installer.iso"


def test_from_dict_partial_config_uses_defaults_for_missing_keys():
    config = Config.from_dict({"client_name": {"short": "dailyplanetos"}})

    assert config.client_name.short == "dailyplanetos"
    assert config.client_name.long == "Potos Linux Client"  # default
    assert config.disk_encryption.enabled is False  # default
    assert config.initial_hostname == "potos-bootstrap"  # default


# --- Partitioning ----------------------------------------------------------


def test_partitioning_defaults_to_auto_mode():
    p = Partitioning.from_dict({})

    assert p.mode == "auto"
    assert p.type == "lvm"
    # the simple partitions and root still get sensible defaults
    assert p.efi.fstype == "efi"
    assert p.efi.size == 600
    assert p.boot.fstype == "xfs"
    assert p.boot.size == 1024
    assert p.root.layout == "btrfs"
    assert p.root.grow is True
    assert p.root.subvolumes == []


def test_partitioning_auto_mode_preserves_type():
    p = Partitioning.from_dict({"mode": "auto", "type": "btrfs"})

    assert p.mode == "auto"
    assert p.type == "btrfs"


def test_partitioning_custom_btrfs_with_subvolumes():
    p = Partitioning.from_dict(
        {
            "mode": "custom",
            "efi": {"fstype": "efi", "size": 512},
            "boot": {"fstype": "ext4", "size": 2048},
            "root": {
                "layout": "btrfs",
                "label": "potos",
                "grow": True,
                "subvolumes": [
                    {"name": "@", "mountpoint": "/"},
                    {"name": "@home", "mountpoint": "/home"},
                ],
            },
        }
    )

    assert p.mode == "custom"
    assert p.efi.fstype == "efi"
    assert p.efi.size == 512
    assert p.boot.fstype == "ext4"
    assert p.boot.size == 2048
    assert p.root.layout == "btrfs"
    assert p.root.label == "potos"
    assert p.root.grow is True
    assert [(s.name, s.mountpoint) for s in p.root.subvolumes] == [
        ("@", "/"),
        ("@home", "/home"),
    ]


def test_partitioning_custom_lvm_with_per_volume_sizes():
    p = Partitioning.from_dict(
        {
            "mode": "custom",
            "root": {
                "layout": "lvm",
                "label": "vg0",
                "grow": True,
                "subvolumes": [
                    {"name": "root", "mountpoint": "/", "fstype": "xfs", "size": 20480},
                    {"name": "home", "mountpoint": "/home"},
                ],
            },
        }
    )

    assert p.root.layout == "lvm"
    assert p.root.label == "vg0"

    root_lv, home_lv = p.root.subvolumes
    assert root_lv.fstype == "xfs"
    assert root_lv.size == 20480
    # missing fstype/size fall back to defaults (0 == unset)
    assert home_lv.fstype == "ext4"
    assert home_lv.size == 0


def test_partitioning_custom_plain_layout_with_fixed_size():
    p = Partitioning.from_dict(
        {
            "mode": "custom",
            "root": {"layout": "plain", "fstype": "ext4", "grow": False, "size": 51200},
        }
    )

    assert p.root.layout == "plain"
    assert p.root.fstype == "ext4"
    assert p.root.grow is False
    assert p.root.size == 51200
    assert p.root.subvolumes == []


def test_config_from_dict_exposes_partitioning():
    config = Config.from_dict({"partitioning": {"mode": "custom", "root": {"layout": "btrfs"}}})

    assert config.partitioning.mode == "custom"
    assert config.partitioning.root.layout == "btrfs"


# --- Bootloader ------------------------------------------------------------


def test_bootloader_defaults_to_grub():
    assert Bootloader.from_dict({}).type == "grub"
    assert Config.from_dict({}).bootloader.type == "grub"


def test_bootloader_systemd_boot():
    config = Config.from_dict({"bootloader": {"type": "systemd-boot"}})

    assert config.bootloader.type == "systemd-boot"


# --- UKI -------------------------------------------------------------------


def test_uki_defaults_to_disabled():
    uki = UKI.from_dict({})

    assert uki.enabled is False
    assert uki.mok_password == "potos"
    assert uki.cmdline_extra == ""
    assert Config.from_dict({}).uki.enabled is False


def test_uki_enabled_with_overrides():
    config = Config.from_dict(
        {
            "uki": {
                "enabled": True,
                "mok_password": "s3cr3t",
                "cmdline_extra": "audit=1",
            }
        }
    )

    assert config.uki.enabled is True
    assert config.uki.mok_password == "s3cr3t"
    assert config.uki.cmdline_extra == "audit=1"


# --- Debug -----------------------------------------------------------------


def test_debug_defaults_to_off():
    d = Debug.from_dict({})

    assert d.no_log is False
    assert d.verbosity == 0
    assert Config.from_dict({}).debug.no_log is False
    assert Config.from_dict({}).debug.verbosity == 0


def test_debug_enabled_with_overrides():
    config = Config.from_dict({"debug": {"no_log": True, "verbosity": 3}})

    assert config.debug.no_log is True
    assert config.debug.verbosity == 3


def test_debug_clamps_verbosity_to_ansible_range():
    assert Debug.from_dict({"verbosity": 9}).verbosity == 6
    assert Debug.from_dict({"verbosity": -2}).verbosity == 0


def test_debug_invalid_verbosity_falls_back_to_zero():
    assert Debug.from_dict({"verbosity": "loud"}).verbosity == 0


def test_credentials_default_to_plaintext_file_backend():
    creds = Credentials.from_dict({})

    assert creds.specs_token.backend == "file"
    assert creds.specs_token.path == "/etc/potos/specs_token"
    assert creds.specs_token.name == "specs-token"
    assert creds.ansible_vault_key.backend == "file"
    assert creds.ansible_vault_key.path == "/etc/potos/ansible_vault_key"
    # An empty config still yields a usable credentials block.
    assert Config.from_dict({}).credentials.specs_token.backend == "file"


def test_credentials_systemd_creds_overrides_and_round_trip():
    creds = Credentials.from_dict(
        {
            "specs_token": {
                "backend": "systemd-creds",
                "path": "/etc/potos/specs_token.cred",
                "name": "specs-token",
            }
        }
    )

    assert creds.specs_token.backend == "systemd-creds"
    assert creds.specs_token.path == "/etc/potos/specs_token.cred"
    # Unspecified secret keeps its defaults.
    assert creds.ansible_vault_key.backend == "file"
    # to_dict() is what build.py writes into /etc/potos/config.yml.
    assert creds.to_dict()["specs_token"] == {
        "backend": "systemd-creds",
        "path": "/etc/potos/specs_token.cred",
        "name": "specs-token",
    }


# --- Firstboot -------------------------------------------------------------


def test_firstboot_ansible_core_version_defaults_to_empty():
    # Empty means "use the hashed lock bundled on the ISO".
    assert Firstboot.from_dict({}).ansible_core_version == ""
    assert Config.from_dict({}).firstboot.ansible_core_version == ""


def test_firstboot_ansible_core_version_override():
    fb = Firstboot.from_dict({"ansible_core_version": "2.20.6"})

    assert fb.ansible_core_version == "2.20.6"


# --- Payload ---------------------------------------------------------------


def test_payload_updates_disabled_by_default():
    assert Payload.from_dict({}).include_updates is False
    assert Config.from_dict({}).payload.include_updates is False


def test_payload_updates_can_be_enabled():
    assert Payload.from_dict({"include_updates": True}).include_updates is True
