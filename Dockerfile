FROM fedora:45@sha256:a7d72ba2745b100a3351087472e5ee7b2450af7cf331e7673007e3817612839c

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
