"""Configuration for the potos iso builder."""

from dataclasses import dataclass


@dataclass
class ClientName:
    """Client name configuration.

    Both names are display labels (installer title, dialog titles, version
    stamp). All filenames, paths and systemd units use literal "potos".
    """

    short: str
    long: str

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            short=data.get("short", "potos"),
            long=data.get("long", "Potos Linux Client"),
        )


@dataclass
class DiskEncryption:
    """Disk encryption configuration."""

    enabled: bool
    init_password: str

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            enabled=data.get("enabled", False),
            init_password=data.get("init_password", "potos"),
        )


@dataclass
class PartitionSpec:
    """A simple, fixed-size partition (e.g. /boot or /boot/efi)."""

    fstype: str
    size: int  # in MiB
    enabled: bool

    @classmethod
    def from_dict(cls, data: dict, default_fstype: str, default_size: int):
        return cls(
            fstype=data.get("fstype", default_fstype),
            size=data.get("size", default_size),
            enabled=data.get("enabled", True),
        )


@dataclass
class Subvolume:
    """A btrfs subvolume (or, for the lvm layout, a logical volume)."""

    name: str
    mountpoint: str
    fstype: str  # only used for the lvm layout; ignored for btrfs
    size: int  # in MiB, only used for the lvm layout (0 == unset); ignored for btrfs

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            name=data["name"],
            mountpoint=data["mountpoint"],
            fstype=data.get("fstype", "ext4"),
            size=data.get("size", 0),
        )


@dataclass
class RootPartition:
    """The root (data) partition layout for custom partitioning."""

    layout: str  # btrfs | lvm | plain
    fstype: str  # for the 'plain' layout, the fstype of the single / partition
    grow: bool
    size: int  # in MiB, only meaningful when grow is False (0 == unset)
    label: str  # btrfs volume label / lvm volume group name
    subvolumes: list

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            layout=data.get("layout", "btrfs"),
            fstype=data.get("fstype", "ext4"),
            grow=data.get("grow", True),
            size=data.get("size", 0),
            label=data.get("label", "fedora"),
            subvolumes=[Subvolume.from_dict(s) for s in data.get("subvolumes", [])],
        )


@dataclass
class Partitioning:
    """Partitioning configuration.

    Two modes are supported:
      * "auto"   - delegate to anaconda's ``autopart`` (uses ``type``).
      * "custom" - lay out efi/boot/root partitions explicitly, with support
                   for choosing the /boot fstype and btrfs subvolumes.
    """

    mode: str  # auto | custom
    type: str  # autopart type (lvm | btrfs | plain), used in "auto" mode
    efi: PartitionSpec
    boot: PartitionSpec
    root: RootPartition

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            mode=data.get("mode", "auto"),
            type=data.get("type", "lvm"),
            efi=PartitionSpec.from_dict(data.get("efi", {}), "efi", 600),
            boot=PartitionSpec.from_dict(data.get("boot", {}), "xfs", 1024),
            root=RootPartition.from_dict(data.get("root", {})),
        )


@dataclass
class Bootloader:
    """Bootloader selection for the installed system.

    Fedora installs grub2 by default. Setting ``type`` to ``systemd-boot``
    makes anaconda install systemd-boot instead.
    """

    type: str  # grub | systemd-boot

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            type=data.get("type", "grub"),
        )


@dataclass
class UKI:
    """Signed UKI + shim + per-host MOK configuration for measured boot.

    When enabled, the installed system is converted from the shimless
    ``systemd-boot`` layout to a measured, signed boot chain:
    ``shim`` -> ``systemd-boot`` (signed, placed as ``grubx64.efi``) -> signed UKI.
    Each host generates and enrolls its own key as a MOK; the firmware
    Secure Boot databases (PK/KEK/db/dbx) are left untouched.

    Requires ``bootloader.type == 'systemd-boot'``. TPM2 LUKS auto-unlock and
    the post-reboot verification/cleanup are handled later by the firstboot
    role, not here.
    """

    enabled: bool
    mok_password: str
    cmdline_extra: str

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            enabled=data.get("enabled", False),
            mok_password=data.get("mok_password", "potos"),
            cmdline_extra=data.get("cmdline_extra", ""),
        )


@dataclass
class Firewall:
    """Firewall configuration."""

    enabled: bool

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            enabled=data.get("enabled", True),
        )


@dataclass
class Locale:
    """Locale configuration."""

    lang: str
    keyboard: str
    timezone: str

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            lang=data.get("lang", ""),
            keyboard=data.get("keyboard", ""),
            timezone=data.get("timezone", ""),
        )


@dataclass
class Network:
    """Network configuration."""

    bootproto: str
    device: str
    activate: bool

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            bootproto=data.get("bootproto", "dhcp"),
            device=data.get("device", "link"),
            activate=data.get("activate", True),
        )


@dataclass
class Authselect:
    """Authselect configuration."""

    features: list

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            features=data.get("features", []),
        )


@dataclass
class Packages:
    """Package selection configuration."""

    exclude: list
    groups: list
    install: list

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            exclude=data.get("exclude", []),
            groups=data.get("groups", []),
            install=data.get("install", []),
        )


@dataclass
class Specs:
    """Specs repository configuration."""

    url: str
    branch: str

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            url=data.get("url", ""),
            branch=data.get("branch", "main"),
        )


@dataclass
class CredentialBackend:
    """How a single on-disk runtime secret is stored.

    Written to /etc/potos/config.yml under credentials.<secret>; consumed at run
    time by the projectpotos.base periodic runtime (not at install time).
    """

    backend: str
    path: str
    name: str

    @classmethod
    def from_dict(cls, data: dict, *, default_path: str, default_name: str):
        return cls(
            backend=data.get("backend", "file"),
            path=data.get("path", default_path),
            name=data.get("name", default_name),
        )

    def to_dict(self) -> dict:
        return {"backend": self.backend, "path": self.path, "name": self.name}


@dataclass
class Credentials:
    """Storage backends for the two runtime secrets (specs token, vault key).

    Optional; the defaults reproduce the historical plaintext-file behavior, so a
    config without a `credentials:` block is unchanged.
    """

    specs_token: CredentialBackend
    ansible_vault_key: CredentialBackend

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            specs_token=CredentialBackend.from_dict(
                data.get("specs_token", {}),
                default_path="/etc/potos/specs_token",
                default_name="specs-token",
            ),
            ansible_vault_key=CredentialBackend.from_dict(
                data.get("ansible_vault_key", {}),
                default_path="/etc/potos/ansible_vault_key",
                default_name="ansible-vault-key",
            ),
        )

    def to_dict(self) -> dict:
        return {
            "specs_token": self.specs_token.to_dict(),
            "ansible_vault_key": self.ansible_vault_key.to_dict(),
        }


@dataclass
class Firstboot:
    """First-boot wizard configuration."""

    extra_roles: list
    role_vars: dict
    firstboot: dict
    ansible_core_version: str

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            extra_roles=data.get("extra_roles", []),
            role_vars=data.get("role_vars", {}),
            firstboot=data.get("firstboot", {}),
            # defaults to the hashed lock bundled in the ISO
            ansible_core_version=data.get("ansible_core_version", ""),
        )


@dataclass
class InitialUser:
    """Initial user configuration."""

    username: str
    password_hash: str

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            username=data.get("username", "potos"),
            password_hash=data.get(
                "password_hash",
                "$6$IZK1CvlO/NanonNV$pRCahbiFxbB9yxTjFo8rlivzDxycsFpk88omqA92gwoJ90yBB97MAhjVBInkC7GBSiHtlv1WhRo2fQPPRmLmF0",  # potos  # noqa: E501
            ),
        )


@dataclass
class Input:
    """Source ISO selection.

    The builder ships a catalog of supported source ISOs and
    downloads the selected one into the output directory itself.
    """

    iso: str

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            iso=data.get("iso", ""),
        )


@dataclass
class Output:
    """Output configuration."""

    version: str
    iso_filename: str

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            version=data.get("version", "1.0"),
            iso_filename=data.get("iso_filename", "potos-installer.iso"),
        )


@dataclass
class Anaconda:
    """Anaconda installer branding configuration."""

    bug_url: str
    hidden_spokes: list

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            bug_url=data.get("bug_url", "https://github.com/projectpotos"),
            hidden_spokes=data.get(
                "hidden_spokes",
                [
                    "SourceSpoke",
                    "PasswordSpoke",
                ],
            ),
        )


@dataclass
class Debug:
    """Runtime debug controls written to /etc/potos/config.yml.

    Read from disk at run time by the firstboot and basics roles / wrappers, so
    they can be flipped on a deployed machine to troubleshoot without rebuilding.
    """

    no_log: bool
    verbosity: int

    @classmethod
    def from_dict(cls, data: dict):
        # Clamp verbosity to ansible's 0-6 range so a bad value can't break the run.
        verbosity = data.get("verbosity", 0)
        try:
            verbosity = max(0, min(int(verbosity), 6))
        except (TypeError, ValueError):
            verbosity = 0
        return cls(
            no_log=bool(data.get("no_log", False)),
            verbosity=verbosity,
        )


@dataclass
class Payload:
    """Installer package source configuration.

    The GA release repo is immutable, so resolving the payload from it alone
    yields a reproducible package set. The rolling updates repo is therefore off
    by default; enable it to track the latest packages at install time instead.
    """

    include_updates: bool

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            include_updates=data.get("include_updates", False),
        )


@dataclass
class Config:
    client_name: ClientName
    fedora_version: int
    extra_repos: list
    payload: Payload
    disk_encryption: DiskEncryption
    partitioning: Partitioning
    bootloader: Bootloader
    uki: UKI
    firewall: Firewall
    locale: Locale
    network: Network
    authselect: Authselect
    packages: Packages
    specs: Specs
    credentials: Credentials
    firstboot: Firstboot
    initial_hostname: str
    initial_user: InitialUser
    post_install: str
    input: Input
    output: Output
    anaconda: Anaconda
    debug: Debug
    collection_source: str = ""

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            client_name=ClientName.from_dict(data.get("client_name", {})),
            fedora_version=data.get("fedora_version", 41),
            extra_repos=data.get("extra_repos", []),
            payload=Payload.from_dict(data.get("payload", {})),
            disk_encryption=DiskEncryption.from_dict(data.get("disk_encryption", {})),
            partitioning=Partitioning.from_dict(data.get("partitioning", {})),
            bootloader=Bootloader.from_dict(data.get("bootloader", {})),
            uki=UKI.from_dict(data.get("uki", {})),
            firewall=Firewall.from_dict(data.get("firewall", {})),
            locale=Locale.from_dict(data.get("locale", {})),
            network=Network.from_dict(data.get("network", {})),
            authselect=Authselect.from_dict(data.get("authselect", {})),
            packages=Packages.from_dict(data.get("packages", {})),
            specs=Specs.from_dict(data.get("specs", {})),
            credentials=Credentials.from_dict(data.get("credentials", {})),
            firstboot=Firstboot.from_dict(data.get("firstboot", {})),
            initial_hostname=data.get("initial_hostname", "potos-bootstrap"),
            initial_user=InitialUser.from_dict(data.get("initial_user", {})),
            post_install=data.get("post_install", "shutdown"),
            input=Input.from_dict(data.get("input", {})),
            output=Output.from_dict(data.get("output", {})),
            anaconda=Anaconda.from_dict(data.get("anaconda", {})),
            debug=Debug.from_dict(data.get("debug", {})),
            collection_source=data.get("collection_source", ""),
        )
