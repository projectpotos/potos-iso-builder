FROM ubuntu:22.04

WORKDIR /potos-iso
RUN apt update && apt install -y gfxboot p7zip-full xorriso wget curl libhtml-parser-perl cpio
COPY potos-iso .

CMD ["./create-iso", "-p"]
