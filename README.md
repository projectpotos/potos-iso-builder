# Potos Fedora ISO Builder

Build customized Fedora installer ISOs with kickstart templating.

## Setup

### Requirements
* libvirt with a qemu user session
  * `virt-manager` is installed
  * You have a QEMU/KVM User-Session (virsh link: `qemu:///session`) configured.
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

### Download ISO and Checksum
```
curl -Lo input/Fedora-Server-dvd-x86_64-43-1.6.iso https://download.fedoraproject.org/pub/fedora/linux/releases/43/Server/x86_64/iso/Fedora-Server-dvd-x86_64-43-1.6.iso
curl -Lo input/Fedora-Server-43-1.6-x86_64-CHECKSUM https://dl.fedoraproject.org/pub/fedora/linux/releases/43/Server/x86_64/iso/Fedora-Server-43-1.6-x86_64-CHECKSUM
```

### Tasks

```bash
go-task build-and-bootstrap # build the iso and test it in a VM

go-task test:teardown # remove the testing VM
```

Alternatively, you can do it more steps:

```bash
go-task build            # build the iso
go-task test:bootstrap   # create a VM in the local libvirt user session with that iso
go-task test:teardown    # remove the testing VM
```

### Notes
* You should set a new disk encryption password (default: `kickstart`)
* You should set a new `admin` user password (default: `password`)

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
