FROM ubuntu:22.04

WORKDIR /potos-iso

# Install ISO creation depencies
RUN apt update && apt install -y gfxboot p7zip-full xorriso wget curl libhtml-parser-perl cpio whois python3 python3-pip fdisk squashfs-tools
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Create config directory
RUN mkdir /config

ADD . /potos-iso

CMD ["/usr/bin/python3", "build-iso.py"]
