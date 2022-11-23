FROM ubuntu:22.04

# ARGs used during docker-compose build, from .env
ARG POTOS_DISK_ENCRYPTION_INITIAL_PASSWORD
ARG POTOS_INITIAL_HOSTNAME
ARG POTOS_INITIAL_USERNAME
ARG POTOS_INITIAL_PASSWORD_HASH
ARG POTOS_CLIENT_NAME
ARG POTOS_CLIENT_SHORTNAME

# ENVs used inside of the container at start docker-compose up, from potos_env file
ENV POTOS_SPECS_REPOSITORY=$POTOS_SPECS_REPOSITORY
ENV POTOS_ADJOIN=$POTOS_ADJOIN
ENV POTOS_ENV=$POTOS_ENV
ENV POTOS_GIT_SPECS_URL=$POTOS_GIT_SPECS_URL
ENV POTOS_GIT_SPECS_REPO=$POTOS_GIT_SPECS_REPO
ENV POTOS_GIT_SPECS_BRANCH=$POTOS_GIT_SPECS_BRANCH

WORKDIR /potos-iso

# Install ISO creation depencies
RUN apt update && apt install -y gfxboot p7zip-full xorriso wget curl libhtml-parser-perl cpio whois

COPY potos-iso .

# Copy all the ARGs and ENVs, to make them available the Potos ISO at boot.
COPY .env contrib/scripts/.env

# Overwrite Potos Linux Client Name, according .env
RUN sed -i "s/Install Potos Linux Client/Install $POTOS_CLIENT_NAME/g" "bootmenu/grub/grub.cfg"

# Overwrite LUKS Install Key according .env
RUN sed -i "s/key: .*/key: $POTOS_DISK_ENCRYPTION_INITIAL_PASSWORD/g" "autoinstall/desktop-bios/user-data"
RUN sed -i "s/key: .*/key: $POTOS_DISK_ENCRYPTION_INITIAL_PASSWORD/g" "autoinstall/desktop-uefi/user-data"

# Overwrite Initial Hostname, according .env
RUN sed -i "s/hostname: .*/hostname: $POTOS_INITIAL_HOSTNAME/g" "autoinstall/desktop-bios/user-data"
RUN sed -i "s/hostname: .*/hostname: $POTOS_INITIAL_HOSTNAME/g" "autoinstall/desktop-uefi/user-data"

# Overwrite Initial User, according .env
RUN sed -i "s/username: .*/username: $POTOS_INITIAL_USERNAME/g" "autoinstall/desktop-bios/user-data"
RUN sed -i "s/username: .*/username: $POTOS_INITIAL_USERNAME/g" "autoinstall/desktop-uefi/user-data"

# Overwrite Initla User Password, according .env
RUN sed -i -e "s/password: .*/password: ${POTOS_INITIAL_PASSWORD_HASH}/g" "autoinstall/desktop-bios/user-data"
RUN sed -i -e "s/password: .*/password: ${POTOS_INITIAL_PASSWORD_HASH}/g" "autoinstall/desktop-uefi/user-data"

CMD ["./create-iso", "-p"]
