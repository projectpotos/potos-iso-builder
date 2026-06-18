#!/usr/bin/bash

set -eo pipefail

# Use QEMU user session
export LIBVIRT_DEFAULT_URI=qemu:///session

VM_NAME="potos-testvm"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ISO_PATH="$(realpath "${SCRIPT_DIR}/../../output/potos-installer.iso")"
DISK_PATH="${HOME}/.local/share/libvirt/images/${VM_NAME}.qcow2"

OS_VARIANT="fedora43"

if [ ! -f "${ISO_PATH}" ]; then
    echo "ERROR: output ISO not found at ${ISO_PATH}" >&2
    exit 1
fi

echo "==> Installing VM '${VM_NAME}' from ${ISO_PATH} (os-variant: ${OS_VARIANT})"

virt-install \
    --name "${VM_NAME}" \
    --ram 4096 \
    --vcpus 2 \
    --disk "path=${DISK_PATH},size=20,format=qcow2" \
    --os-variant "${OS_VARIANT}" \
    --cdrom "${ISO_PATH}" \
    --network user \
    --graphics spice \
    --noautoconsole \
    --boot uefi \
    --tpm backend.type=emulator,backend.version=2.0,model=tpm-crb \
    --wait -1

echo "==> Installation finished. Detaching install ISO..."
# Find and detach the cdrom device so the VM boots from disk on next start
CDROM_DEV=$(virsh domblklist "${VM_NAME}" --details \
    | awk '$2 == "cdrom" && $4 != "-" { print $3 }' | head -n1)
if [ -n "${CDROM_DEV}" ]; then
    virsh change-media "${VM_NAME}" "${CDROM_DEV}" --eject --config
    echo "==> Ejected cdrom device '${CDROM_DEV}'."
fi

echo "==> Booting installed VM..."
if ! start_out=$(virsh start "${VM_NAME}" 2>&1); then
    if ! grep -q "Domain is already active" <<< "${start_out}"; then
        echo "ERROR: Failed to start VM '${VM_NAME}'" >&2
        echo "${start_out}" >&2
        exit 1
    fi
fi

# Poll until running (up to 60 s)
for _ in $(seq 1 12); do
    STATE=$(virsh domstate "${VM_NAME}" 2>/dev/null || true)
    if [ "${STATE}" = "running" ]; then
        echo "==> VM '${VM_NAME}' is running."
        exit 0
    fi
    sleep 5
done

echo "ERROR: VM '${VM_NAME}' did not reach running state in time." >&2
virsh dominfo "${VM_NAME}" >&2
exit 1
