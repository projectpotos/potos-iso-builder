"""Configuration for the potos iso builder."""

from dataclasses import dataclass


@dataclass
class ClientName:
    """Client name configuration."""

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
    makes anaconda install systemd-boot instead, via the
    ``inst.bootloader=systemd-boot`` installer boot option.
    """

    type: str  # grub | systemd-boot

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            type=data.get("type", "grub"),
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
class Firstboot:
    """First-boot wizard configuration."""

    extra_roles: list
    role_vars: dict

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            extra_roles=data.get("extra_roles", []),
            role_vars=data.get("role_vars", {}),
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
                "$6$anXOuiWGKciAIFeD$mlYKotVh1phov5oTsOVxj2/L7vGxAy4VojtxXSPa..9q7EdKwK99xoRbcY5UI4DN4kK7r0ODuRgbDvKIiEhMl0",  # potos  # noqa: E501
            ),
        )


@dataclass
class Input:
    """Input ISO configuration."""

    iso_filename: str
    checksum_filename: str

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            iso_filename=data.get("iso_filename", ""),
            checksum_filename=data.get("checksum_filename", ""),
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
                    "SoftwareSelectionSpoke",
                    "SourceSpoke",
                    "PasswordSpoke",
                ],
            ),
        )


@dataclass
class Config:
    client_name: ClientName
    fedora_version: int
    extra_repos: list
    disk_encryption: DiskEncryption
    partitioning: Partitioning
    bootloader: Bootloader
    firewall: Firewall
    locale: Locale
    network: Network
    authselect: Authselect
    packages: Packages
    specs: Specs
    firstboot: Firstboot
    initial_hostname: str
    initial_user: InitialUser
    post_install: str
    input: Input
    output: Output
    anaconda: Anaconda
    collection_source: str = ""

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            client_name=ClientName.from_dict(data.get("client_name", {})),
            fedora_version=data.get("fedora_version", 41),
            extra_repos=data.get("extra_repos", []),
            disk_encryption=DiskEncryption.from_dict(data.get("disk_encryption", {})),
            partitioning=Partitioning.from_dict(data.get("partitioning", {})),
            bootloader=Bootloader.from_dict(data.get("bootloader", {})),
            firewall=Firewall.from_dict(data.get("firewall", {})),
            locale=Locale.from_dict(data.get("locale", {})),
            network=Network.from_dict(data.get("network", {})),
            authselect=Authselect.from_dict(data.get("authselect", {})),
            packages=Packages.from_dict(data.get("packages", {})),
            specs=Specs.from_dict(data.get("specs", {})),
            firstboot=Firstboot.from_dict(data.get("firstboot", {})),
            initial_hostname=data.get("initial_hostname", "potos-bootstrap"),
            initial_user=InitialUser.from_dict(data.get("initial_user", {})),
            post_install=data.get("post_install", "shutdown"),
            input=Input.from_dict(data.get("input", {})),
            output=Output.from_dict(data.get("output", {})),
            anaconda=Anaconda.from_dict(data.get("anaconda", {})),
            collection_source=data.get("collection_source", ""),
        )
