FROM ubuntu:24.04

WORKDIR /potos-iso

# Install ISO creation depencies
RUN apt update && apt install -y gfxboot p7zip-full xorriso wget curl libhtml-parser-perl cpio whois python3 python3-pip fdisk squashfs-tools python3-requests python3-jinja2 python3-yaml

# Create config directory
RUN mkdir /config

ADD . /potos-iso

CMD ["/usr/bin/python3", "build-iso.py"]
