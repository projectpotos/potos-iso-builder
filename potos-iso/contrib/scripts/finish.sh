#!/bin/bash

# Load all the environment variables
source /setup/.env

#just for debug , schroeffu
mkdir /opt/tmp
cp -R /setup/* /opt/tmp
cp /setup/.env /opt/tmp

ANSIBLE_WORKDIR='/var/lib/ansible/local/work'
ANSIBLE_GIT_URL='https://github.com/projectpotos/ansible-plays-potos.git'
ANSIBLE_GIT_BRANCH='main'

if [[ -d "/etc/potos" ]]; then
  rm -rf "/etc/potos"
fi

mkdir -p "/etc/potos"
mkdir -p "/var/log/potos"

cat > /etc/potos/specs_repo.yml <<EOF
---
client_name: "${POTOS_CLIENT_NAME}"
git_url: "${POTOS_GIT_SPECS_URL}"
git_repo: "${POTOS_GIT_SPECS_REPO}"
git_branch: "${POTOS_GIT_SPECS_BRANCH}"
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
# Apply the ansible prepare.yml
################################################################################

cd "${ANSIBLE_WORKDIR}"
ansible-playbook prepare.yml -vvv | sed -u 's/^/# /'
ansible-playbook playbook.yml -vvv | sed -u 's/^/# /'

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
