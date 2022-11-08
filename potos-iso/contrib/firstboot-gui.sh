#!/bin/bash

POTOS_VERSION="Potos Linux Client"

if [[ -f /setup/potos-version ]]; then
  POTOS_VERSION="$(</setup/potos-version)"
fi

/setup/change-keyboard-layout

sudo mkdir -m 755 -p /var/log/potos
sudo touch /var/log/potos/setup.log
sudo -E bash -c '/setup/finish.sh &>> /var/log/potos/setup.log' &

FINISH_CMD_PID=${!}

sudo chown gnome-initial-setup /dev/tty2

sudo tail -f /var/log/potos/setup.log | tee /dev/tty2 | yad --fullscreen --no-buttons --title 'Potos Linux Client Setup' \
  --progress --enable-log --log-expanded --log-on-top --log-height 500 \
  --text 'Please wait until the setup is finished' &

# Wait until the finish.sh background process exits and check its return code
wait ${FINISH_CMD_PID}

FINISH_CMD_RC=${?}

if [[ ${FINISH_CMD_RC} -ne 0 ]]; then
  case ${FINISH_CMD_RC} in
    1) ERROR_MSG="General command failure" ;;
    *) ERROR_MSG="Unknown error code ${FINISH_CMD_RC}" ;;
  esac
fi

sudo cat /var/log/potos/setup.log | yad --fullscreen --title 'Potos Linux Client Setup' \
  --borders 20 --button gtk-ok \
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

# vim: tabstop=2 shiftwidth=2 expandtab softtabstop=2
