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
class Partitioning:
    """Partitioning configuration."""

    type: str

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            type=data.get("type", "lvm"),
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
                "$6$anXOuiWGKciAIFeD$mlYKotVh1phov5oTsOVxj2/L7vGxAy4VojtxXSPa..9q7EdKwK99xoRbcY5UI4DN4kK7r0ODuRgbDvKIiEhMl0",  # potos
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
