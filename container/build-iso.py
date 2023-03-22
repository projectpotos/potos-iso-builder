#!/usr/bin/python3

import yaml
import os
import shutil
import jinja2
from datetime import date
import subprocess
from pprint import pprint

# define jinja2 environment
j2 = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(os.path.abspath(__file__)))
)

# get config inkl default values
config = {}
with open("/config/config.yml", "r") as f:
    try:
        ymlconfig = yaml.safe_load(f)
        config['client_name'] = {}
        config['client_name']['long'] = ymlconfig.get("client_name",{}).get('long',"Potos Linux Client")
        config['client_name']['short'] = ymlconfig.get("client_name",{}).get('short',"potos")
        config['disk_encryption'] = {}
        config['disk_encryption']['enable'] = ymlconfig.get("disk_encryption",{}).get('enable',False)
        config['disk_encryption']['init_password'] = ymlconfig.get("disk_encryption",{}).get('init_password',"install")
        config['specs'] = {}
        config['specs']['url'] = ymlconfig.get("specs",{}).get('url',"https://github.com/projectpotos/")
        config['specs']['repo'] = ymlconfig.get("specs",{}).get('repo',"ansible-specs-potos")
        config['specs']['branch'] = ymlconfig.get("specs",{}).get('branch',"main")
        config['specs']['ssh_key'] = ymlconfig.get("specs",{}).get('ssh_key',"")
        config['specs']['ansible_vault_key_file'] = ymlconfig.get("specs",{}).get('ansible_vault_key_file',"")
        config['initial_hostname'] = ymlconfig.get("initial_hostname","potoshostname01")
        config['initial_user'] = {}
        config['initial_user']['username'] = ymlconfig.get("initial_user",{}).get('username',"admin")
        config['initial_user']['password'] = ymlconfig.get("initial_user",{}).get('password',"$6$L36BiUuVCSipvlO8$oGI0C.LXZegkbftFkVDXXaasTM6zs9LM71BkqZToKw5aOZ7Yr70pkzH3P9Xz5R.n0ULJ0Zf8v5ZQ/eH8flDR7/")
        config['environment'] = ymlconfig.get("environment","production")
        config['first_boot_ansible'] = {}
        config['first_boot_ansible']['runtype'] = ymlconfig.get("first_boot_ansible",{}).get('runtype',"setup")
        config['full_unattended_install'] = ymlconfig.get("full_unattended_install", False)
        config['os'] = ymlconfig.get("os","jammy")
        config['output'] = {}
        config['output']['version'] = date.today().strftime(ymlconfig.get("output",{}).get('version',"%Y%m%d"))
        config['output']['iso_filename'] = ymlconfig.get("output",{}).get('iso_filename',"%s-installer.iso"%(config['client_name']['short']))
        config['isolinux'] = {}
        config['isolinux']['txtBackgroundColor'] = ymlconfig.get("isolinux",{}).get('txtBackgroundColor', "0xCCCCCC")
        config['isolinux']['txtForegroundColor'] = ymlconfig.get("isolinux",{}).get('txtForegroundColor', "0xFFFFFF")
        config['isolinux']['screenColor'] = ymlconfig.get("isolinux",{}).get('screenColor', "0x161B21")
    except yaml.YAMLError as e:
        print(e)
        exit(1)

TMP_DIR = "iso"
REQIREMENTS = ["7z", "gfxboot", "xorriso", "wget", "curl", "sha256sum"]

# switch iso by selected os
if config['os'] == "jammy":
    config['input'] = {}
    config['input']['iso_filename'] = "ubuntu-22.04.2-live-server-amd64.iso"
    config['input']['iso_url'] = (
        "https://releases.ubuntu.com/22.04/ubuntu-22.04.2-live-server-amd64.iso"
    )
    config['input']['sha256_filename'] = "SHA256SUMS"
    config['input']['sha256_url'] = "https://releases.ubuntu.com/22.04/SHA256SUMS"
    config['packages'] = {}
    config['packages']['preinstall'] = [
        "python3-virtualenv",
        "linux-generic-hwe-22.04",
        "ubuntu-desktop",
        "plymouth-theme-ubuntu-logo",
        "ldap-utils",
        "yad",
    ]
elif config['os'] == "focal":
    config['input'] = {}
    config['input']['iso_filename'] = "ubuntu-20.04.5-live-server-amd64.iso"
    config['input']['iso_url'] = (
        "https://releases.ubuntu.com/20.04/ubuntu-20.04.5-live-server-amd64.iso"
    )
    config['input']['sha256_filename'] = "SHA256SUMS"
    config['input']['sha256_url'] = "https://releases.ubuntu.com/20.04/SHA256SUMS"
    config['packages'] = {}
    config['packages']['preinstall'] = [
        "linux-generic-hwe-20.04",
        "ubuntu-desktop",
        "plymouth-theme-ubuntu-logo",
        "ldap-utils",
        "yad",
        "python3-virtualenv",
    ]
else:
    print("Invalid base os: %s"%(config['os']))
    print("Currently supported os are:")
    print(" * Ubuntu: 'jammy', 'focal'")
    exit(1)

######
# Start with iso build
######

# Print config info
if config['environment'] == "develop":
    print(
        "*** config.environment is %s, going to print some more informations for you:"%(
            config['environment'],
        )
    )
    pprint(config)

print(
    "*** Going to build an ISO for %s (%s)"%(config['client_name']['long'], config['environment'])
)

# Check if required software is installed else install
for r in REQIREMENTS:
    if os.system("which %s > /dev/null"%(r)) != 0:
        print("%s is missing!"%(r))
        exit(1)

# If iso dir somehow exists, remove it
if os.path.exists(TMP_DIR) and os.path.isdir(TMP_DIR):
    shutil.rmtree(TMP_DIR)
elif os.path.exists(TMP_DIR):
    print("ERROR: %s exists but is not a directory"%(TMP_DIR))
    exit(1)

# If iso and checksum not exist, download them
if not os.path.exists(config['input']['iso_filename']):
    if (
        os.system(
            "wget -nv --output-document='%s' %s"%(
                config['input']['iso_filename'],
                config['input']['iso_url'],
            )
        )
        != 0
    ):
        print("ERROR: %s could not be downloaded!"%(config['input']['iso_url']))

if not os.path.exists(config['input']['sha256_filename']):
    if (
        os.system(
            "wget -nv --output-document='%s' %s"%(
                config['input']['sha256_filename'],
                config['input']['sha256_url'],
            )
        )
        != 0
    ):
        print("ERROR: %s could not be downloaded!"%(config['input']['sha256_url']))

# Fail if no checksum exists
if (
    os.system("sha256sum --ignore-missing --quiet -c %s"%(config['input']['sha256_filename']))
    != 0
):
    print("ERROR: sha256sum check failed!")
    exit(1)

# extract iso into temporary directory
if os.system("7z x '%s' -o'%s'"%(config['input']['iso_filename'], TMP_DIR)) != 0:
    print("ERROR: could not extract iso file")
    exit(2)

# remove no longer needed stuff
if os.path.exists(os.path.join(TMP_DIR, "preseed")):
    shutil.rmtree(os.path.join(TMP_DIR, "preseed"))

# make directory for files during autoinstall
os.mkdir(os.path.join(TMP_DIR, "setup"))

# copy Netplan into iso
shutil.copy("default-netplan.yml", os.path.join(TMP_DIR, "setup/default-netplan.yml"))

# copy Gnome initial setup sudoers rule into iso
shutil.copy("gnome-sudo", os.path.join(TMP_DIR, "setup/gnome-sudo"))

# template autoinstall files
os.mkdir(os.path.join(TMP_DIR, "nocloud-uefi"))
with open(os.path.join(TMP_DIR, "nocloud-uefi/meta-data"), "w") as f:
    f.write(
        j2.get_template("autoinstall-meta-data.j2").render(
            config=config, autoinstall_type="uefi"
        )
    )
with open(os.path.join(TMP_DIR, "nocloud-uefi/user-data"), "w") as f:
    f.write(
        j2.get_template("autoinstall-user-data.j2").render(
            config=config, autoinstall_type="uefi"
        )
    )

os.mkdir(os.path.join(TMP_DIR, "nocloud-bios"))
with open(os.path.join(TMP_DIR, "nocloud-bios/meta-data"), "w") as f:
    f.write(
        j2.get_template("autoinstall-meta-data.j2").render(
            config=config, autoinstall_type="bios"
        )
    )
with open(os.path.join(TMP_DIR, "nocloud-bios/user-data"), "w") as f:
    f.write(
        j2.get_template("autoinstall-user-data.j2").render(
            config=config, autoinstall_type="bios"
        )
    )

# create version file
with open(
    os.path.join(TMP_DIR, "setup/%s-version" % (config['client_name']['short'])), "w"
) as f:
    f.write(
        "%s %s (%s)\n"%(
            config['client_name']['short'],
            config['output']['version'] ,
            date.today().strftime("%Y%m%d-%H%M"),
        )
    )

# remove boot config
shutil.rmtree(os.path.join(TMP_DIR, "[BOOT]"))

# template grub config
if not os.path.exists(os.path.join(TMP_DIR, "boot/grub")):
    os.makedir(os.path.join(TMP_DIR, "boot/grub"))
with open(os.path.join(TMP_DIR, "boot/grub/grub.cfg"), "w") as f:
    f.write(j2.get_template("grub.cfg.j2").render(config=config))

# copy logo into iso
if os.path.exists("/config/logo.png"):
    shutil.copy("/config/logo.png", os.path.join(TMP_DIR, "setup/logo.png"))
else:
    shutil.copy("default/logo.png", os.path.join(TMP_DIR, "setup/logo.png"))

# copy ssh deploy key for specs repo into image
if config['specs']['ssh_key'] != "" and os.path.exists(os.path.join("/config/", config['specs']['ssh_key'])):
    shutil.copy(
        os.path.join("/config/", config['specs']['ssh_key']),
        os.path.join(TMP_DIR, "setup/specs_key"),
    )

# copy ansible-vault key for specs repo into image
if config['specs']['ansible_vault_key_file'] != "" and os.path.exists(
    os.path.join("/config/", config['specs']['ansible_vault_key_file'])
):
    shutil.copy(
        os.path.join("/config/", config['specs']['ansible_vault_key_file']),
        os.path.join(TMP_DIR, "setup/ansible_vault_key"),
    )

# template diverse files for firstboot

with open(os.path.join(TMP_DIR, "setup/firstboot-gui.sh"), 'w') as f:
    f.write(j2.get_template("firstboot-gui.sh.j2").render(config=config))
os.chmod(os.path.join(TMP_DIR, "setup/firstboot-gui.sh"), 0o555)
with open(os.path.join(TMP_DIR, "setup/finish.sh"), 'w') as f:
    f.write(j2.get_template("finish.sh.j2").render(config=config))
os.chmod(os.path.join(TMP_DIR, "setup/finish.sh"), 0o555)
with open(os.path.join(TMP_DIR, "setup/change-keyboard-layout"), 'w') as f:
    f.write(j2.get_template("change-keyboard-layout.j2").render(config=config))
os.chmod(os.path.join(TMP_DIR, "setup/change-keyboard-layout"), 0o555)



# adjust md5sum checks
os.system("sed -i 's|$%s/|./|g' '%s/md5sum.txt'" % (TMP_DIR, TMP_DIR))

# Get efi partition infos
iso_bs = subprocess.check_output(
    "fdisk -l '%s' | grep 'Sector size' | tr -s ' ' | cut -d ' ' -f4"
    % (config['input']['iso_filename']), shell=True
).decode("utf-8").rstrip()
iso_efi_skip = subprocess.check_output(
    "fdisk -l '%s' | grep 'EFI' | tr -s ' ' | cut -d ' ' -f2" % (config['input']['iso_filename']), shell=True
).decode("utf-8").rstrip()
iso_efi_size = subprocess.check_output(
    "fdisk -l '%s' | grep 'EFI' | tr -s ' ' | cut -d ' ' -f4" % (config['input']['iso_filename']), shell=True
).decode("utf-8").rstrip()

# define MBR
MBR_FILE = "boot_hybrid.img"

# write original MBR to MBR file
os.system("dd if='%s' bs=1 count=432 of='%s'" % (config['input']['iso_filename'], MBR_FILE))

# write original efi.img to file
os.system(
    "dd if='%s' bs='%s' skip='%s' count='%s' of=efi.img"
    % (config['input']['iso_filename'], iso_bs, iso_efi_skip, iso_efi_size)
)

# as default try to use eltorito boot image
boot_image = "/boot/grub/i386-pc/eltorito.img"

# if eltorito is not available in the iso, fall back to isolinux, strip first slash
if not os.path.exists(os.path.join(TMP_DIR, boot_image.lstrip('/'))):
    with open(os.path.join(TMP_DIR, "isolinux/txt.cfg"), "w") as f:
        f.write(j2.get_template("isolinux.cfg.j2").render(config=config))
    if os.path.exists("/config/splash.pcx"):
        os.system(
            "gfxboot -a '%s/isolinux/bootlogo' --add-files /config/splash.pcx"
            % (TMP_DIR)
        )
    else:
        os.system(
            "gfxboot -a '%s/isolinux/bootlogo' --add-files default/splash.pcx"
            % (TMP_DIR)
        )
    if os.path.exists("/config/access.pcx"):
        os.system(
            "gfxboot -a '%s/isolinux/bootlogo' --add-files /config/access.pcx"
            % (TMP_DIR)
        )
    else:
        os.system(
            "gfxboot -a '%s/isolinux/bootlogo' --add-files default/access.pcx"
            % (TMP_DIR)
        )
    os.system(
        "gfxboot -a '%s/isolinux/bootlogo' --change-config background='%s'"
        % (TMP_DIR, config['isolinux']['txtBackgroundColor'])
    )
    os.system(
        "gfxboot -a '%s/isolinux/bootlogo' --change-config foreground='%s'"
        % (TMP_DIR, config['isolinux']['txtForegroundColor'])
    )
    os.system(
        "gfxboot -a '%s/isolinux/bootlogo' --change-config screen-colour='%s'"
        % (TMP_DIR, config['isolinux']['screenColor'])
    )
    os.system("gfxboot -a '%s/isolinux/bootlogo' --default-language en_US" % (TMP_DIR))
    os.system(
        "gfxboot -a '%s/isolinux/bootlogo' --rm-config hidden-timeout" % (TMP_DIR)
    )
    os.system(
        "gfxboot -a '%s/isolinux/bootlogo' --change-config hidden-timeout=1" % (TMP_DIR)
    )
    boot_image = "isolinux/isolinux.bin"

os.system(
    """xorriso -as mkisofs -r -V '%s' \
-o 'output.iso' \
--grub2-mbr '%s' \
-partition_offset 16 \
--mbr-force-bootable \
-append_partition 2 28732ac11ff8d211ba4b00a0c93ec93b efi.img \
-appended_part_as_gpt \
-iso_mbr_part_type a2a0d0ebe5b9334487c068b6b72699c7 \
-c '/boot.catalog' \
-b '%s' \
-no-emul-boot -boot-load-size 4 -boot-info-table --grub2-boot-info \
-eltorito-alt-boot \
-e '--interval:appended_partition_2:::' \
-no-emul-boot \
'%s'"""
    % (config['client_name']['short'], MBR_FILE, boot_image, TMP_DIR)
)

# remove temp directory
shutil.rmtree(TMP_DIR)

# remove mbr
os.remove(MBR_FILE)

# Move iso to output directory
shutil.move("output.iso", os.path.join("/output/", config['output']['iso_filename']))

# Generate checksum
with open("/output/%s.sha256sum" % (config['output']['iso_filename']), "w") as f:
    f.write(
        subprocess.check_output("sha256sum '/output/%s'" % (config['output']['iso_filename']), shell=True).decode("utf-8").rstrip()
    )

print("Done!")
