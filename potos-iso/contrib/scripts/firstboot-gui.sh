#!/bin/bash

# Load all the environment variables
source /setup/.env

POTOS_VERSION="${POTOS_CLIENT_NAME} (${POTOS_CLIENT_SHORTNAME})"

/setup/change-keyboard-layout

if [[ -f /setup/${POTOS_CLIENT_SHORTNAME}-version ]]; then
  POTOS_VERSION="$(</setup/${POTOS_CLIENT_SHORTNAME}-version)"
fi

if [[ ${POTOS_ENV} == develop ]]; then
  yad --fullscreen --title "${POTOS_CLIENT_NAME} ENV ${POTOS_ENV}" \
    --borders 20 --align center --button OK --image-on-top \
    --image=/setup/potos.png \
    --text \
  "Welcome to the last step of the ${POTOS_CLIENT_NAME} installation

  ENV ${POTOS_ENV} detected. Going to print some more output here and later. Ansible will run in -vvv mode.

  Client: ${POTOS_VERSION}

  Environment Variables:
  POTOS_SPECS_REPOSITORY: ${POTOS_SPECS_REPOSITORY}
  POTOS_ADJOIN: ${POTOS_ADJOIN}
  POTOS_ENV: ${POTOS_ENV}
  POTOS_DISK_ENCRYPTION_INITIAL_PASSWORD: ${POTOS_DISK_ENCRYPTION_INITIAL_PASSWORD}
  POTOS_INITIAL_HOSTNAME: ${POTOS_INITIAL_HOSTNAME}
  POTOS_INITIAL_PASSWORD_HASH: ${POTOS_INITIAL_PASSWORD_HASH}
  POTOS_INITIAL_USERNAME: ${POTOS_INITIAL_USERNAME}
  POTOS_CLIENT_NAME: ${POTOS_CLIENT_NAME}
  POTOS_CLIENT_SHORTNAME: ${POTOS_CLIENT_SHORTNAME}

  POTOS_GIT_SPECS_URL: ${POTOS_GIT_SPECS_URL}
  POTOS_GIT_SPECS_REPO: ${POTOS_GIT_SPECS_REPO}
  POTOS_GIT_SPECS_BRANCH: ${POTOS_GIT_SPECS_BRANCH}


  Click OK to proceed the installation.
  "
fi

yad --fullscreen --title "${POTOS_CLIENT_NAME} Setup" \
  --borders 20 --align center --button OK --image-on-top \
  --image=/setup/potos.png \
  --text \
"Welcome to the last step of the ${POTOS_CLIENT_NAME} installation

Client: ${POTOS_VERSION}

Click OK to proceed the installation.
"

sudo mkdir -m 755 -p /var/log/${POTOS_CLIENT_SHORTNAME}
sudo touch /var/log/${POTOS_CLIENT_SHORTNAME}/setup.log
sudo -E bash -c "/setup/finish.sh &> /var/log/${POTOS_CLIENT_SHORTNAME}/setup.log" &

FINISH_CMD_PID=${!}

sudo chown gnome-initial-setup /dev/tty2

sudo tail -f /var/log/${POTOS_CLIENT_SHORTNAME}/setup.log | tee /dev/tty2 | yad --fullscreen --no-buttons --title "${POTOS_CLIENT_NAME} Setup" \
  --progress --enable-log --log-expanded --log-on-top --log-height 500 \
  --text 'Please wait until the setup is finished' &

# Wait until the finish.sh background process exits and check its return code
wait ${FINISH_CMD_PID}

FINISH_CMD_RC=${?}

if [[ ${FINISH_CMD_RC} -ne 0 ]]; then
  case ${FINISH_CMD_RC} in
    1) ERROR_MSG="General command failure" ;;
    2) ERROR_MSG="Network connectivity issues" ;;
    3) ERROR_MSG="AD join failure" ;;
    4) ERROR_MSG="Ansible failure" ;;
    5) ERROR_MSG="Vault failure" ;;
    6) ERROR_MSG="ISO outdated" ;;
    *) ERROR_MSG="Unknown error code ${FINISH_CMD_RC}" ;;
  esac
fi

sudo cat /var/log/${POTOS_CLIENT_SHORTNAME}/setup.log | yad --fullscreen --title "${POTOS_CLIENT_NAME} Setup" \
  --borders 20 --align center --button gtk-ok \
  --button "Shutdown":"sudo systemctl halt" \
  --text-info --tail \
  --image=/setup/potos.png --image-on-top \
  --text \
"Installation failed

The last step of the installation was not successful.
  Error message: ${ERROR_MSG}
  Return code: ${FINISH_CMD_RC}

Click OK to retry or Shutdown to cancel.
"

sudo systemctl restart gdm.service
