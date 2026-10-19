FROM fedora:44@sha256:6c75d5bf57cb0fa5aa4b92c6a83c86c791644496d9ac230de7711f5b8ec3b898

# hadolint ignore=DL3041
RUN dnf -y update && \
    dnf install -y lorax pykickstart \
    xorriso squashfs-tools && \
    dnf clean all

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.13.1-python3.14-trixie@sha256:6863df3d2e87426f81a136ecb2ae6a7e567b2c413a6bf623af89d75a63a00405 /usr/local/bin/uv /usr/local/bin/uvx /usr/local/bin/

WORKDIR /app

# Install Python dependencies with uv
COPY pyproject.toml ./
RUN uv sync --no-dev --no-install-project

# Copy build script
COPY src/ ./

COPY src/branding ./branding

ENTRYPOINT ["uv", "run", "python", "build.py"]
