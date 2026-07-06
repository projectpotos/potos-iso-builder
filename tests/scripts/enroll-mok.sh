#!/usr/bin/bash
#
# The installed Potos system signs its boot chain with a per-host MOK that is
# normally enrolled interactively via MokManager on first boot. 
# MokManager times out if left unattended, dropping the firmware to a shim 
# "Security Violation" (0x1A). When that happens, run this to
# enroll the key non-interactively: it reads the cert from the installed root
# and injects it into the VM's UEFI MokList and then boots the VM into the signed system.
#
# It needs sudo for qemu-nbd and LUKS to read the encrypted root.
#
# Important: This script only interacts with the UEFI from the VM
#            and NOT your host system.
#

set -eo pipefail

export LIBVIRT_DEFAULT_URI=qemu:///session

VM_NAME="${1:-potos-testvm}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DISK_PATH="${HOME}/.local/share/libvirt/images/${VM_NAME}.qcow2"
CONFIG_FILE="${SCRIPT_DIR}/../input/config.yml"

for tool in virt-fw-vars qemu-nbd cryptsetup uuidgen virsh; do
    command -v "${tool}" >/dev/null 2>&1 || { echo "ERROR: ${tool} not found" >&2; exit 1; }
done

if ! virsh dominfo "${VM_NAME}" >/dev/null 2>&1; then
    echo "ERROR: VM '${VM_NAME}' is not defined" >&2
    exit 1
fi

if [ "$(virsh domstate "${VM_NAME}" 2>/dev/null)" = "running" ]; then
    echo "==> Stopping '${VM_NAME}' to rewrite its nvram..."
    virsh destroy "${VM_NAME}" >/dev/null
fi

NVRAM=$(virsh dumpxml "${VM_NAME}" | sed -n 's#.*<nvram[^>]*>\(.*\)</nvram>.*#\1#p')
if [ -z "${NVRAM}" ] || [ ! -f "${NVRAM}" ]; then
    echo "ERROR: could not locate the VM nvram file" >&2
    exit 1
fi

LUKS_PASS=$(sed -n 's/^[[:space:]]*init_password:[[:space:]]*"\{0,1\}\([^"]*\)"\{0,1\}[[:space:]]*$/\1/p' \
    "${CONFIG_FILE}" 2>/dev/null | head -n1)

NBD=/dev/nbd0
MAP="${VM_NAME}-mok"
MNT=$(mktemp -d)
CERT="$(mktemp -d)/mok.der"

cleanup() {
    sudo umount "${MNT}" 2>/dev/null || true
    sudo cryptsetup close "${MAP}" 2>/dev/null || true
    sudo qemu-nbd --disconnect "${NBD}" 2>/dev/null || true
    rm -rf "${MNT}" 2>/dev/null || true
    rm -f "${CERT}" 2>/dev/null || true
}
trap cleanup EXIT

echo "==> Reading MOK cert from the installed root..."
sudo modprobe nbd max_part=8
sudo qemu-nbd --connect="${NBD}" --read-only "${DISK_PATH}"
for _ in $(seq 1 10); do [ -e "${NBD}p1" ] && break; sleep 0.5; done

LUKS_PART=$(lsblk -lno NAME,FSTYPE "${NBD}" | awk '$2=="crypto_LUKS"{print "/dev/"$1; exit}')
if [ -n "${LUKS_PART}" ]; then
    printf '%s' "${LUKS_PASS}" | sudo cryptsetup open --readonly "${LUKS_PART}" "${MAP}" -
    ROOT_PART="/dev/mapper/${MAP}"
else
    ROOT_PART=$(lsblk -lno NAME,FSTYPE "${NBD}" | awk '$2=="btrfs"{print "/dev/"$1; exit}')
fi
sudo mount -o ro,subvol=@ "${ROOT_PART}" "${MNT}" 2>/dev/null \
    || sudo mount -o ro "${ROOT_PART}" "${MNT}"

if ! sudo test -f "${MNT}/etc/secureboot/mok.der"; then
    echo "ERROR: /etc/secureboot/mok.der not found on the installed root" >&2
    echo "       Is Secure Boot enabled in tests/input/config.yml and the install complete?" >&2
    exit 1
fi
sudo cp "${MNT}/etc/secureboot/mok.der" "${CERT}"
sudo chown "$(id -u):$(id -g)" "${CERT}"

echo "==> Injecting cert into the VM MokList..."
virt-fw-vars --input "${NVRAM}" --output "${NVRAM}" --add-mok "$(uuidgen)" "${CERT}"

cleanup
trap - EXIT

echo "==> Booting '${VM_NAME}' into the signed system..."
virsh start "${VM_NAME}" >/dev/null
echo "==> Done. MOK enrolled; the signed boot chain should boot unattended now."
