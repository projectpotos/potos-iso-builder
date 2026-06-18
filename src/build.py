"""Potos Fedora ISO Builder.

Create your customized kickstart file based on a simple YAML config and build a bootable ISO with it.
"""

from __future__ import annotations

import argparse
import hashlib
import logging
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

import jinja2
import yaml

from config import Config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)

log = logging.getLogger("potos-builder")

TEMPLATE_DIR = Path("./templates")


class ISOBuilder:
    """Class to handle the ISO building process."""

    cfg: Config
    args: argparse.Namespace
    log: logging.Logger

    def __init__(self, cfg: Config, args: argparse.Namespace):
        self.cfg = cfg
        self.args = args
        self.log = logging.getLogger("ISOBuilder")

    def build_updates_img(self, addon_dirs: list[Path]) -> Path:
        """Build an updates.img containing anaconda addons and customizations for the installer.

        The updates.img is a cpio+gzip archive mirroring the installer filesystem.
        Anaconda applies it at boot, overlaying files onto the installer environment.
        See: RHEL 10 Customizing Anaconda, Section 5.15 & 6.1
        """
        tmp_dir = tempfile.mkdtemp()
        root = Path(tmp_dir)

        try:
            addons_dest = root / "usr/share/anaconda/addons"
            dbus_confs = root / "usr/share/anaconda/dbus/confs"
            dbus_services = root / "usr/share/anaconda/dbus/services"
            addons_dest.mkdir(parents=True)
            dbus_confs.mkdir(parents=True)
            dbus_services.mkdir(parents=True)

            for addon_dir in addon_dirs:
                # Find the Python package directory (not data/)
                for child in addon_dir.iterdir():
                    if child.is_dir() and child.name != "data":
                        shutil.copytree(child, addons_dest / child.name)

                # Copy D-Bus config files
                data_dir = addon_dir / "data"
                if data_dir.exists():
                    for f in data_dir.iterdir():
                        if f.suffix == ".conf":
                            shutil.copy2(f, dbus_confs / f.name)
                        elif f.suffix == ".service":
                            shutil.copy2(f, dbus_services / f.name)

            self._add_anaconda_customization(root)

            updates_img = Path(self.args.output_dir) / "updates.img"

            find_result = subprocess.run(["find", "."], cwd=root, capture_output=True, check=True)
            cpio_result = subprocess.run(
                ["cpio", "-c", "-o", "--quiet"],
                cwd=root,
                input=find_result.stdout,
                capture_output=True,
                check=True,
            )
            gzip_result = subprocess.run(
                ["gzip", "-9"],
                input=cpio_result.stdout,
                capture_output=True,
                check=True,
            )
            updates_img.write_bytes(gzip_result.stdout)

            self.log.info("updates.img built: %s", updates_img)
            return updates_img
        finally:
            shutil.rmtree(tmp_dir)

    def _add_anaconda_customization(self, root: Path) -> None:
        """Add branding assets to the updates.img filesystem tree."""
        branding_context = {"config": self.cfg}

        pixmaps_src = Path("./branding/pixmaps")
        pixmaps_dest = root / "usr/share/anaconda/pixmaps"
        pixmaps_dest.mkdir(parents=True, exist_ok=True)

        if pixmaps_src.is_dir():
            for f in pixmaps_src.iterdir():
                if f.is_file():
                    shutil.copy2(f, pixmaps_dest / f.name)
                    self.log.info("Anaconda: added pixmaps/%s", f.name)

        # Override with custom assets from input directory if provided
        custom_css = Path(self.args.input_dir) / "potos.css"
        if custom_css.is_file():
            shutil.copy2(custom_css, pixmaps_dest / "potos.css")
            self.log.info("Anaconda: using custom CSS from input/potos.css")

        custom_logo = Path(self.args.input_dir) / "logo.png"
        if custom_logo.is_file():
            shutil.copy2(custom_logo, pixmaps_dest / "sidebar-logo.png")
            self.log.info("Anaconda: using custom logo from input/logo.png")

        anaconda_template_dir = TEMPLATE_DIR / "anaconda"
        rendered = render_template(".buildstamp.j2", branding_context, anaconda_template_dir)
        (root / ".buildstamp").write_text(rendered)
        self.log.info("Anaconda: rendered .buildstamp")

        conf_d_template_dir = anaconda_template_dir / "conf.d"
        conf_d_dest = root / "etc/anaconda/conf.d"
        conf_d_dest.mkdir(parents=True, exist_ok=True)
        if conf_d_template_dir.is_dir():
            for f in conf_d_template_dir.iterdir():
                if f.is_file() and f.suffix == ".j2":
                    rendered = render_template(f.name, branding_context, conf_d_template_dir)
                    out_name = f.stem  # strip .j2
                    (conf_d_dest / out_name).write_text(rendered)
                    self.log.info("Anaconda: rendered conf.d/%s", out_name)

    def verify_iso(self) -> None:
        """Verify the source ISO integrity using Fedora's OpenPGP-signed checksum."""
        input_dir = Path(self.args.input_dir)
        src_iso = input_dir / self.cfg.input.iso_filename
        checksum_file = input_dir / self.cfg.input.checksum_filename

        if not checksum_file.exists():
            self.log.error("Checksum file not found: %s", checksum_file)
            sys.exit(1)

        with tempfile.TemporaryDirectory() as tmp_dir:
            gpg_path = Path(tmp_dir) / "fedora.gpg"

            self.log.info("Downloading Fedora OpenPGP certificate...")
            result = subprocess.run(
                [
                    "curl",
                    "-sSf",
                    "-o",
                    str(gpg_path),
                    "https://fedoraproject.org/fedora.gpg",
                ],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                self.log.error("Failed to download Fedora GPG keyring:\n%s", result.stderr)
                sys.exit(1)

            self.log.info("Verifying checksum file signature and ISO integrity...")
            gpgv = subprocess.run(
                [
                    "gpgv",
                    "--keyring",
                    str(gpg_path),
                    "--output",
                    "-",
                    str(checksum_file),
                ],
                capture_output=True,
            )
            if gpgv.returncode != 0:
                self.log.error(
                    "Checksum file signature verification failed:\n%s",
                    gpgv.stderr.decode(),
                )
                sys.exit(1)

            sha256sum = subprocess.run(
                ["sha256sum", "-c", "--ignore-missing"],
                input=gpgv.stdout,
                capture_output=True,
                cwd=src_iso.parent,
            )
            if sha256sum.returncode != 0:
                self.log.error(
                    "ISO checksum verification failed:\n%s\n%s",
                    sha256sum.stdout.decode(),
                    sha256sum.stderr.decode(),
                )
                sys.exit(1)

        self.log.info("ISO integrity verified successfully.")

    def build_iso(
        self,
        ks_path: Path,
        updates_img: Path | None = None,
        src_iso: Path | None = None,
        setup_dir: Path | None = None,
    ) -> Path:
        """Use mkksiso to embed the kickstart into the source ISO."""
        if src_iso is None:
            src_iso = Path(self.args.input_dir) / self.cfg.input.iso_filename
        if not src_iso.exists():
            self.log.error("Source ISO not found: %s", src_iso)
            sys.exit(1)

        out_iso = Path(self.args.output_dir) / self.cfg.output.iso_filename

        # Back up existing output
        if out_iso.exists():
            bak = out_iso.with_suffix(".iso.bak")
            self.log.info("Backing up existing ISO to %s", bak)
            shutil.move(str(out_iso), str(bak))

        cmd = [
            "mkksiso",
            "--ks",
            str(ks_path),
        ]
        if updates_img:
            cmd.extend(["--updates", str(updates_img)])
        if setup_dir is not None:
            cmd.extend(["--add", str(setup_dir)])
        cmd.extend(
            [
                str(src_iso),
                str(out_iso),
            ]
        )
        self.log.info("Building ISO: %s", " ".join(cmd))
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            self.log.error("mkksiso failed:\n%s\n%s", result.stdout, result.stderr)
            sys.exit(1)

        self.log.info("ISO built: %s", out_iso)
        return out_iso

    def _config_yaml(self) -> str:
        """Return the YAML written to /etc/potos/config.yml during %post."""
        data = {
            "client_name": {
                "short": self.cfg.client_name.short,
                "long": self.cfg.client_name.long,
            },
            "specs": {
                "url": self.cfg.specs.url,
                "branch": self.cfg.specs.branch,
            },
            "role_vars": self.cfg.firstboot.role_vars,
            "firstboot_extra_roles": self.cfg.firstboot.extra_roles,
        }
        return yaml.safe_dump(data, sort_keys=False, default_flow_style=False)

    def prepare_setup_dir(self) -> Path | None:
        """Stage files added to the ISO at /setup/"""
        staging = Path(tempfile.mkdtemp(prefix="potos-setup-"))
        setup = staging / "setup"
        setup.mkdir()

        # Bundle collection tarballs (used only when collection_source is empty)
        collections_src = Path(self.args.input_dir) / "collections"
        collections_dst = setup / "collections"
        added = 0
        if collections_src.is_dir():
            collections_dst.mkdir()
            for tgz in sorted(collections_src.glob("*.tar.gz")):
                shutil.copy2(tgz, collections_dst / tgz.name)
                self.log.info("setup/: bundled collection %s", tgz.name)
                added += 1
        if added == 0 and not self.cfg.collection_source:
            self.log.warning(
                "No collection tarballs found in %s and no collection_source configured; firstboot will fail",
                collections_src,
            )

        # Custom credential script if `potos_firstboot_credentials_source=script`
        script_src = Path(self.args.input_dir) / "credentials.sh"
        if script_src.is_file():
            dst = setup / "credentials.sh"
            shutil.copy2(script_src, dst)
            dst.chmod(0o755)
            self.log.info("setup/: bundled credentials script from %s", script_src)

        # Branding logo shown by the firstboot dialogs (installed persistently
        # by finish.sh; the staging dir itself is removed after install).
        logo_src = Path(self.args.input_dir) / "logo.png"
        if not logo_src.is_file():
            logo_src = Path("./branding/pixmaps/sidebar-logo.png")
        shutil.copy2(logo_src, setup / "logo.png")
        self.log.info("setup/: bundled firstboot logo from %s", logo_src)
        return staging

    def render_kickstart(self) -> str:
        """Render the kickstart file (with finish.sh as %post body)."""
        build_date = datetime.now().strftime("%Y-%m-%d %H:%M")

        post_scripts = render_template(
            "finish.sh.j2",
            {
                "config": self.cfg,
                "build_date": build_date,
                "config_yaml": self._config_yaml(),
            },
        )

        return render_template(
            "kickstart.cfg.j2",
            {
                "config": self.cfg,
                "build_date": build_date,
                "post_scripts": post_scripts,
            },
        )

    def validate_kickstart(self, ks_path: Path) -> None:
        """Run ksvalidator on the generated kickstart file."""
        cmd = ["ksvalidator", str(ks_path)]
        self.log.info("Validating kickstart: %s", " ".join(cmd))
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            self.log.error("ksvalidator stderr:\n%s", result.stderr)
            self.log.error("ksvalidator stdout:\n%s", result.stdout)
            sys.exit(1)
        self.log.info("Kickstart validation passed.")

    def write_kickstart(self, content: str) -> Path:
        # Write rendered kickstart to a temp directory
        tmp_dir = tempfile.TemporaryDirectory()
        ks_path = Path(tmp_dir.name) / "kickstart.cfg"
        ks_path.write_text(content)
        self.log.info("Rendered kickstart written to %s", ks_path)

        # validate temporary kickstart file
        self.validate_kickstart(ks_path)

        # create actual kickstart file if validation passes
        final_ks_path = Path(self.args.output_dir) / "kickstart.cfg"
        shutil.copy(str(ks_path), str(final_ks_path))
        self.log.info("Kickstart copied to output directory: %s", final_ks_path)

        tmp_dir.cleanup()

        return final_ks_path

    def customize_boot_menu(self, iso_path: Path) -> None:
        """Customize boot menu labels to show the configured OS name.

        Extracts boot/grub2/grub.cfg from the ISO to detect the Fedora product
        name, then calls mkksiso --replace so that every boot config file
        (including the embedded efiboot.img read by UEFI) is updated in one
        pass.
        """
        os_name = self.cfg.client_name.long
        version = str(self.cfg.fedora_version)

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            grub_cfg = tmp / "grub.cfg"

            result = subprocess.run(
                [
                    "xorriso",
                    "-osirrox",
                    "on",
                    "-indev",
                    str(iso_path),
                    "-extract",
                    "/boot/grub2/grub.cfg",
                    str(grub_cfg),
                ],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0 or not grub_cfg.exists():
                self.log.warning("Could not extract grub.cfg from ISO; skipping boot menu customization")
                return

            replacements = self._compute_label_replacements(grub_cfg.read_text(), os_name, version)
            if not replacements:
                self.log.warning("No boot menu entries found to customize")
                return

            patched = tmp / "patched.iso"
            cmd = ["mkksiso"]
            for from_str, to_str in replacements:
                cmd.extend(["--replace", from_str, to_str])
            cmd.extend([str(iso_path), str(patched)])

            self.log.info("Customizing boot menu: %s", " ".join(cmd))
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                self.log.error(
                    "Failed to update ISO with custom boot menu:\n%s\n%s",
                    result.stdout,
                    result.stderr,
                )
                sys.exit(1)

            shutil.move(str(patched), str(iso_path))
            self.log.info("Boot menu now shows: %s", os_name)

    def _compute_label_replacements(self, content: str, os_name: str, version: str) -> list[tuple[str, str]]:
        """Return (from, to) pairs for Fedora boot menu label substitution.

        Auto-detects the Fedora variant (e.g. 'Fedora Server') from menuentry
        titles and returns replacements for both the versioned form
        ('Fedora Server 44') and the bare product name used in rescue entries.
        """
        match = re.search(r"menuentry\s+['\"].*?(Fedora\s+\w+)\s+" + re.escape(version), content)
        if match:
            fedora_product = match.group(1)  # e.g. "Fedora Server"
            return [
                (f"{fedora_product} {version}", os_name),
                (fedora_product, os_name),
            ]

        # Fallback: replace "Fedora <version>" generically
        return [(f"Fedora {version}", os_name)]

    def write_checksum(self, iso_path: Path):
        """Generate SHA256 checksum file for the output ISO."""
        sha256 = hashlib.sha256()
        with open(iso_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        checksum = sha256.hexdigest()
        checksum_path = iso_path.with_suffix(".iso.sha256")
        checksum_path.write_text(f"{checksum}  {iso_path.name}\n")
        self.log.info("Checksum written: %s", checksum_path)

    def start(self):
        """Main entry point to start the build process."""
        if not self.args.skip_verify:
            self.verify_iso()
        else:
            self.log.info("Skipping ISO verification (--skip-verify).")

        ks_content = self.render_kickstart()
        ks_path = self.write_kickstart(ks_content)

        # Patch the installer ISO with additional packages if configured
        src_iso = Path(self.args.input_dir) / self.cfg.input.iso_filename

        updates_img = None
        addons_root = Path("./addons")
        addon_dirs = [d for d in sorted(addons_root.iterdir()) if d.is_dir()] if addons_root.is_dir() else []
        self.log.info("Found %d addon(s) in %s", len(addon_dirs), addons_root)
        self.log.info(
            "Building updates.img with custom anaconda config%s",
            " + addons" if addon_dirs else "",
        )
        updates_img = self.build_updates_img(addon_dirs)

        setup_dir = self.prepare_setup_dir()
        try:
            iso_path = self.build_iso(
                ks_path,
                updates_img=updates_img,
                src_iso=src_iso,
                setup_dir=(setup_dir / "setup") if setup_dir else None,
            )
        finally:
            if setup_dir is not None:
                shutil.rmtree(setup_dir, ignore_errors=True)

        self.customize_boot_menu(iso_path)
        self.write_checksum(iso_path)


def render_template(template_name: str, context: dict, template_dir: Path = TEMPLATE_DIR) -> str:
    """Render a Jinja2 template from the given directory."""
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(template_dir)),
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    return env.get_template(template_name).render(**context)


def load_config(path: str) -> Config:
    """Load the config from a YAML file"""
    with open(path) as f:
        data = yaml.safe_load(f)
    return Config.from_dict(data)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Build a customized Fedora ISO with a kickstart file.")
    parser.add_argument(
        "--config",
        type=str,
        action="store",
        default="config.yaml",
        help="Path to the YAML configuration file (default: config.yaml)",
    )
    parser.add_argument(
        "--input-dir",
        type=str,
        action="store",
        default="input",
        help="Directory containing the source ISO and checksum file (default: input/)",
    )
    parser.add_argument(
        "--skip-verify",
        action="store_true",
        default=False,
        help="Skip ISO integrity verification (default: verify)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        action="store",
        default="output",
        help="Directory to save the generated ISO and artifacts (default: output/)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    log.info("=== Starting Potos Fedora ISO Builder ===")

    if not os.path.exists(args.config):
        log.error("Config file not found: %s", args.config)
        sys.exit(1)

    config = load_config(args.config)
    builder = ISOBuilder(config, args)

    log.info(
        "Building ISO for %s (%s)",
        config.client_name.long,
        config.client_name.short,
    )

    builder.start()

    log.info("=== Done! ===")


if __name__ == "__main__":
    main()
