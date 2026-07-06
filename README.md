# Potos Fedora ISO Builder

Build customized Fedora installer ISOs with kickstart templating.

## Setup

### Requirements
* libvirt with a qemu user session
  * `virt-manager` is installed
  * You have a QEMU/KVM User-Session (virsh link: `qemu:///session`) configured.
  * `virt-firmware` is required to test secure boot features
  * your user is member of the `kvm` group
  * `virt-install --osinfo list` knows about `fedora43`. If not, you will have to edit `tests/scripts/bootstrap.sh` and set `OS_VARIANT` to the highest fedora version you found in this list. Tested with `fedora42` successfully.
* docker and docker-compose are installed
  * see these [install instructions](https://docs.docker.com/engine/install/) and select your OS there.
  * your user is member of the `docker` group (really needed?)
  * the `docker.service` is now required:
    * In order to patch the EFI image we need permission to create loopback devices. That doesn't work with rootless podman, so we are forced to use docker instead.
* go-task is installed.
  * also called `task` in some distros
    * Ubuntu: `snap install task --classic`

### Choose a config

The builder reads `input/config.yml`, which is **not** committed — copy an
example and edit it:

```bash
cp examples/minimal/config.yml input/config.yml          # easy start
# or
cp examples/best-practice/config.yml input/config.yml    # full hardware security
```

### Source ISO

The builder downloads the source Fedora ISO (and its OpenPGP-signed checksum)
for you and caches it under `output/`.

### Build your ISO

```bash
go-task build:all   # build the projectpotos.base collection tarball + the ISO (-> output/)
go-task build       # just the ISO (collection already staged)
```

### Test the reference fixture in a VM

The e2e harness builds and boots the committed fixture at `tests/input/config.yml`
(into `tests/output/`), keeping it decoupled from your own `input/` workspace:

```bash
go-task build-and-bootstrap   # build the fixture ISO and boot it in a VM
go-task test:teardown         # remove the testing VM
```

Or step by step:

```bash
go-task build:test        # build tests/input/config.yml -> tests/output/
go-task test:bootstrap    # create a libvirt VM from the fixture ISO
go-task test:teardown     # remove the testing VM
```

### Notes
* Rotate the bootstrap secrets the examples ship with (the disk
  `init_password` and `uki.mok_password`) and the `admin`
  `password_hash` before any real use — they are intentionally well-known.

## Testing

### KVM with UEFI + Secureboot

The `test:bootstrap` task will create a VM that uses UEFI and configures secureboot with libvirt.
Please make sure you have the required `ovmf` package installed that adds UEFI support to KVM.

In addition we will use `swtpm` to emulate a TPM for the testing VM.

## Links
* https://github.com/erik1066/fedora-setup-guide
* https://oneuptime.com/blog/post/2026-03-04-custom-rhel-9-iso-lorax-kickstart/view
* https://pykickstart.readthedocs.io/en/latest/kickstart-docs.html
* https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/10/html-single/customizing_anaconda/index#deploying-and-testing-an-anaconda-add-on
* https://fedoraproject.org/wiki/InitialSetup
