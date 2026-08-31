FROM fedora:44@sha256:43b29f65a41eb9c35e1cd5323e3bdf3b655c2357a9f4f1ff2f9c2798e5045d80

# hadolint ignore=DL3041
RUN dnf -y update && \
    dnf install -y lorax pykickstart \
    xorriso squashfs-tools && \
    dnf clean all

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.11.29-python3.14-trixie@sha256:cd22b8ef1b9a27e285a0e8ee3416db1c955d7d14c33bb39ec2a41306c68a5500 /usr/local/bin/uv /usr/local/bin/uvx /usr/local/bin/

WORKDIR /app

# Install Python dependencies with uv
COPY pyproject.toml ./
RUN uv sync --no-dev --no-install-project

# Copy build script
COPY src/ ./

COPY src/branding ./branding

ENTRYPOINT ["uv", "run", "python", "build.py"]
