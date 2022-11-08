# Potos .iso building

Make sure you have [Docker](https://docs.docker.com/get-docker) and [Docker-Compose](https://docs.docker.com/compose/install/) installed.

```
git clone ${{ github.repositoryUrl }}
cd potos-iso
docker-compose build
docker-compose up # The container does stop after building the .iso image in /potos-images automatically.
```

The time to generate the .iso image mainly depends on the internet speed, since an Ubuntu 22.04 image is downloaded and modified.

# Potos .iso installation

Boot from the previously generated Potos .iso image in your virtual or physical hardware to start the installation.

# PXE and iPXE Boot

Not implemented yet.
