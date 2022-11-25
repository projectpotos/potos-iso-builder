
# Potos .iso building

To create your own Linux Client based on Potos, please follow this steps:

1. Clone this repository with `git clone` or download & unzip it.
2. Edit the environment variables in `.env` to fit your needs. To run the Continuous Configuration of your Potos based Linux Client on your own, don't forget to change the value of `POTOS_GIT_SPECS_*` towards your own git repository, otherwise your Linux Client is going to connect to the Potos Default Repository [ansible-specs-potos](https://github.com/projectpotos/ansible-specs-potos).
3. Build the installation .iso as described below.

## Create your Potos .iso

Make sure you have [Docker](https://docs.docker.com/get-docker) and [Docker-Compose](https://docs.docker.com/compose/install/) installed.

```
docker-compose build
docker-compose up # The container does stop after building the .iso image in /potos-images automatically.
```

Note: The time to generate the .iso image mainly depends on your internet bandwith, since an Ubuntu 22.04 image is downloaded and modified.

###  .env File Variables

| Variable | Comments |
|--|--|
| **POTOS_CLIENT_NAME** <br>*string*| Define the Name of your Linux Client, e.g. "My Linux Client".<br>*Default: "Potos Linux Client"* |
| **POTOS_CLIENT_SHORTNAME** <br>*string, lowercase, short* | Define a short name of your Linux Client. Use lowercase. Will be used for example for the log folder /var/log/$POTOS_CLIENT_SHORTNAME<br>*Default: "potos"*
| **POTOS_DISK_ENCRYPTION_INITIAL_PASSWORD** <br>*string* |  The autoinstall feature with disk encryption (except: /boot) needs a predefined decryption password. You have to enter this password at first boot after the installation.<br>*Default: install*
| **POTOS_INITIAL_HOSTNAME**<br>*string* | Your Linux Client based on Potos will use this predefined hostname at the installation and first boot.<br>Can also be an FQDN.<br>*Default: potoshostname01*
| **POTOS_INITIAL_USERNAME**<br>*string* | An initial username is required. Will have full sudo (root) permission. Can be removed later on.<br>*Default: admin*
| **POTOS_INITIAL_PASSWORD_HASH**<br>*sring* | The password in form of a hash. Create your own with `echo -n yourpasswordhere \| mkpasswd --method=SHA-512 --stdin`.<br>Escape the backslashes with \\/ (for now).<br>*Default unhashed: admin*
| **POTOS_GIT_SPECS_URL**<br>*string, URL, trailing slash* | The URL to your Git Account that holds your own Potos Specs Repository. Make sure you have the trailing slash included. <br>*Default: https://github.com/projectpotos/*
| **POTOS_GIT_SPECS_REPO**<br>*string, part of the URL* | The name of your own Potos Git Specs Repository, without *.git* at the End.<br>*Default: ansible-specs-potos*
| **POTOS_GIT_SPECS_BRANCH**<br>*string* | Define the branch of your POTOS_GIT_SPECS_REPO. Typical values are `main`, `master`, `develop` <br>*Default: main*
| **POTOS_ENV**<br>*string*| Possible values are `production` and `develop`. The installation in `develop` mode is more verbose.<br>*Default: production*

# Potos .iso installation

Boot from the previously generated Potos .iso image in your virtual or physical hardware and follow the instruction.

# PXE and iPXE Boot

Not implemented yet.
