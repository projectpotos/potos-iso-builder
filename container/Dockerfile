FROM ubuntu:22.04

WORKDIR /potos-iso

# Install ISO creation depencies
RUN apt update && apt install -y gfxboot p7zip-full xorriso wget curl libhtml-parser-perl cpio whois python3 python3-pip fdisk
RUN pip3 install j2cli
RUN wget -qO /usr/local/bin/yq https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64 && chmod +x /usr/local/bin/yq

# Create config directory
RUN mkdir /config

ADD . /potos-iso

CMD ["./build-iso"]
