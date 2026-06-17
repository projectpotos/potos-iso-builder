#!/usr/bin/bash

set -eo pipefail

# Use QEMU user session
export LIBVIRT_DEFAULT_URI=qemu:///session

VM_NAME="potos-testvm"

echo "==> Tearing down VM '${VM_NAME}'"

# Destroy the VM if it is still running
STATE=$(virsh domstate "${VM_NAME}" 2>/dev/null || true)
if [ "${STATE}" = "running" ]; then
    echo "==> Destroying running VM..."
    virsh destroy "${VM_NAME}"
fi

# Undefine the domain and remove the disk image
if virsh dominfo "${VM_NAME}" &>/dev/null 2>&1; then
    echo "==> Undefining VM..."
    virsh undefine "${VM_NAME}" --remove-all-storage 2>/dev/null \
        || virsh undefine "${VM_NAME}"
fi


echo "==> Teardown complete."
