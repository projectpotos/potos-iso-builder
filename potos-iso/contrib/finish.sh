#!/bin/bash

################################################################################

ANSIBLE_WORKDIR='/var/lib/ansible/local/work'
ANSIBLE_GIT_URL='https://github.com/projectpotos/ansible-plays-potos.git'
ANSIBLE_GIT_BRANCH='develop'

DOMAIN_JOIN_DOMAIN='REMOVED'
DOMAIN_JOIN_OU='OU=NA,DC=DOMAIN,DC=LOCAL'
DOMAIN_JOIN_USER='na@ad.domain.local'

export DOMAIN_JOIN_DOMAIN DOMAIN_JOIN_OU DOMAIN_JOIN_USER

################################################################################

mkdir -m 755 -p /var/log/potos

################################################################################
# Prepare the git checkout
################################################################################

if [[ ! -d /root/.ssh ]]; then
  mkdir -m 700 /root/.ssh
fi

cat > /etc/ansible/potos_inventory <<EOF
localhost ansible_connection=local
EOF

if [[ -d "${ANSIBLE_WORKDIR}" ]]; then
  rm -rf "${ANSIBLE_WORKDIR}"
fi

mkdir -p "${ANSIBLE_WORKDIR}"

git clone --single-branch --branch "${ANSIBLE_GIT_BRANCH}" "${ANSIBLE_GIT_URL}" "${ANSIBLE_WORKDIR}"

if [[ $? -ne 0 ]]; then
  echo "# ERROR: Failed to clone the git repository"
  exit 1
fi

################################################################################
# Fetch the hostname and prepare the ansible vars
################################################################################

#KEYBOARD_LAYOUT="ch"

#if [[ -f /tmp/keyboard-layout.selected ]]; then
#  KEYBOARD_LAYOUT="$(< /tmp/keyboard-layout.selected)"
#fi

cat > /tmp/potos-setup_ansible-vars.yml <<EOF
client_fqdn: "${POTOS_HOSTNAME}.ad.domain.local"
keyboard_layout: "${KEYBOARD_LAYOUT}"
#domain_join_domain: "${DOMAIN_JOIN_DOMAIN}"
#domain_join_ou: "${DOMAIN_JOIN_OU}"
#domain_join_user: "${DOMAIN_JOIN_USER}"
#domain_join_pass: "${DOMAIN_JOIN_PASS}"
EOF

################################################################################
# Apply the ansible playbook
################################################################################

cd "${ANSIBLE_WORKDIR}"
ansible-playbook -e "@/tmp/potos-setup_ansible-vars.yml" setup.yml | sed -u 's/^/# /'

if [[ ${PIPESTATUS[0]} -ne 0 ]]; then
  echo "# ERROR: Ansible failed with return code ${PIPESTATUS[0]}"
  exit 1
fi

################################################################################
# Finalize the installation
################################################################################

sed -ie 's/GRUB_CMDLINE_LINUX_DEFAULT=.*/GRUB_CMDLINE_LINUX_DEFAULT="quiet splash"/' /etc/default/grub
/usr/sbin/update-grub

cat > /var/lib/AccountsService/users/admin <<EOF
[User]
SystemAccount=true
EOF

echo "# Cleaning up ... please wait"

rm -f /etc/sudoers.d/01_gnome-initial-setup
apt purge -y gnome-initial-setup
userdel -rf gnome-initial-setup

rm -rf /setup

sleep 5s
systemctl reboot

# vim: tabstop=2 shiftwidth=2 expandtab softtabstop=2
