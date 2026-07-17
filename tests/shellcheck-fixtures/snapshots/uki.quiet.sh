#!/bin/bash
# Potos Linux Client Secure Boot / signed-UKI setup.
#
# use projectpotos.base.uki to set up secure boot with self-signed UKI images.
#

set -euo pipefail

export LANG=C.UTF-8
export LC_ALL=C.UTF-8
export ANSIBLE_COLLECTIONS_PATH=/usr/share/ansible/collections

VENV=/opt/potos-firstboot/venv
COLLECTION_ROOT=/usr/share/ansible/collections/ansible_collections/projectpotos/base

dnf install -y  python3-libdnf5

if [ ! -x "${VENV}/bin/ansible-playbook" ] || [ ! -d "${COLLECTION_ROOT}" ]; then
  echo "ERROR: ansible venv or projectpotos.base collection missing;" >&2
  exit 1
fi

# The uki role takes its settings as extra vars; the system config written
# by firstboot only serves as fallback for periodic runs without specs-provided uki settings.
"${VENV}/bin/ansible-playbook" \
  -i localhost, -c local \
  -e uki_enabled=false \
  -e uki_mok_password=potos \
  -e uki_cmdline_extra='' \
  -e uki_mok_label='Potos Linux Client' \
  projectpotos.base.uki

echo "Secure Boot setup complete."
