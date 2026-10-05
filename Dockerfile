FROM fedora:44@sha256:43b29f65a41eb9c35e1cd5323e3bdf3b655c2357a9f4f1ff2f9c2798e5045d80

# hadolint ignore=DL3041
RUN dnf -y update && \
    dnf install -y lorax pykickstart \
    xorriso squashfs-tools && \
    dnf clean all

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.12.10-python3.14-trixie@sha256:a3e6118ca6b41a5e5c457fd70eb0fc71f11aea67408fb68e5888ba955ad545c0 /usr/local/bin/uv /usr/local/bin/uvx /usr/local/bin/

WORKDIR /app

# Install Python dependencies with uv
COPY pyproject.toml ./
RUN uv sync --no-dev --no-install-project

# Copy build script
COPY src/ ./

COPY src/branding ./branding

ENTRYPOINT ["uv", "run", "python", "build.py"]
