FROM fedora:44@sha256:6c75d5bf57cb0fa5aa4b92c6a83c86c791644496d9ac230de7711f5b8ec3b898

# hadolint ignore=DL3041
RUN dnf -y update && \
    dnf install -y lorax pykickstart \
    xorriso squashfs-tools && \
    dnf clean all

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.12.17-python3.14-trixie@sha256:9f68650ccb8aee38b7cb6f22cfb6592a1e2e7f05fa3858fdf0bff7fd0acda73d /usr/local/bin/uv /usr/local/bin/uvx /usr/local/bin/

WORKDIR /app

# Install Python dependencies with uv
COPY pyproject.toml ./
RUN uv sync --no-dev --no-install-project

# Copy build script
COPY src/ ./

COPY src/branding ./branding

ENTRYPOINT ["uv", "run", "python", "build.py"]
