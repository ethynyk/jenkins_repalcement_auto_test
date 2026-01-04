'''
# Date:     2025/06/14
# File:     upgrade.py
# Project:  LTPU
# Function: Automatically upgrade
# Commad example:
#   python upgrade.py --serial_port=xx --board=xx --sd_src=/path/upgrade.zip
'''

# coding=utf-8

import os
import sys
import shutil
import argparse
import yaml
import logging
import time
from datetime import datetime

sys.path.append('..')
from utils.common_func import print_function, extract_time, is_same_day
from utils.serial_utils import init_serial, ser_run_cmd, get_ip


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.FileHandler("upgrade.log"),
                logging.StreamHandler()],
)


UPGRADE_FILE = os.path.join(
    os.path.dirname(__file__),
    "upgrade.yaml"
)


def sd_upgrade_cmds(board: str):
    print_function()
    with open(UPGRADE_FILE, 'rb') as f:
        raw_data = yaml.safe_load(f)
    upgrade_config = raw_data[board]['upgrade']
    logging.info(upgrade_config['desc'])
    upgrade_cmds = upgrade_config['cmds']
    upgrade_time = upgrade_config['runtime']
    return upgrade_cmds, upgrade_time


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Upgade args')
    parser.add_argument(
        "--serial_port", action="store", type=str, default=None,
        help="Serial port connected to client. (mutually exclusive with --ip)"
    )
    parser.add_argument(
        "--board", action="store", type=str, default=None,
        help="Board name"
    )
    parser.add_argument(
        "--sd_dev", action="store", type=str, default="/dev/mmcblk0p1",
        help="Devices corresponding to SD card slots"
    )
    parser.add_argument(
        "--test_path", action="store", type=str, default="/mnt/nfs",
        help="Directory where execute test commands"
    )
    parser.add_argument(
        "--host_ws", action="store", type=str, default="D:/jenkins",
        help="prepare test files to host workspace"
    )
    parser.add_argument(
        "--nfs_path", action="store", type=str, default="192.168.1.10:/nfs",
        help="NFS mount path in host (require host_ws)"
    )
    parser.add_argument(
        "--daily", action="store_true", default=False,
        help="Whether check board version is today's version"
    )
    parser.add_argument(
        "--skip_date_check", action="store_true", default=False,
        help="Whether check the date"
    )
    parser.add_argument(
        "--reboot", action="store_true", default=False,
        help="whether reboot board before update images"
    )
    parser.add_argument(
        "--sd_src", action="store", type=str, default=None,
        help="upgrade.zip path by SD upgrade"
    )
    parser.add_argument(
        "--ota_src", action="store", type=str, default=None,
        help="OTA filepath"
    )
    args = parser.parse_args()

    ser = init_serial(args.serial_port)

    if args.sd_src:
        print("\n=== Customer Configuration ===\n")
        for opt in args.__dict__:
            value = str(args.__dict__[opt])
            print(f"{opt.ljust(20)}:{value}")

        if args.reboot:
            ser_run_cmd(ser=ser, cmd="reboot", timeout=100)
            time.sleep(3)       # wait for dhcp

        # copy sd_src to host_ws
        host_ws = args.host_ws.replace("\\", "/")
        sd_src = args.sd_src.replace("\\", "/")
        sd_src_zip = os.path.basename(sd_src)
        os.makedirs(host_ws, exist_ok=True)
        assert os.path.exists(sd_src), f"{sd_src} not exists!"
        dest_path = os.path.join(host_ws, os.path.basename(sd_src))
        if host_ws not in sd_src:
            shutil.move(sd_src, dest_path)
            logging.info(f"move {sd_src} to {host_ws}")

        # mount nfs
        test_path = args.test_path.replace("\\", "/")
        nfs_path = args.nfs_path.replace("\\", "/")
        assert ser.isOpen()
        if not args.reboot:
            cmd = "umount " + test_path
            ser_run_cmd(ser=ser, cmd=str(cmd))
        ip = get_ip(ser=ser)
        assert ip, "Cannot get ip"
        cmd = "mkdir -p " + test_path
        ser_run_cmd(ser=ser, cmd=str(cmd))
        cmd = "mount -t nfs -o nolock " + nfs_path + " " + test_path
        ser_run_cmd(ser=ser, cmd=str(cmd))
        log, ret_code, ret = ser_run_cmd(ser=ser, cmd="df -h", ret_regex=nfs_path)
        assert ret, f'Cannot mount {test_path}'

        # mount sd card
        sd_dev = args.sd_dev
        assert ser.isOpen()
        if not args.reboot:
            ser_run_cmd(ser=ser, cmd="umount /mnt/sd")
        cmd = "mount " + sd_dev + " /mnt/sd"
        ser_run_cmd(ser=ser, cmd=str(cmd))
        log, ret_code, ret = ser_run_cmd(ser=ser, cmd="df -h", ret_regex=sd_dev)
        assert ret, f'Cannot mount {sd_dev}'

        # get pre version
        log, _, _ = ser_run_cmd(ser=ser, cmd="uname -v")
        log = ' '.join(log.split('\n')[:])
        pre_version = extract_time(time_str=log, time_format="%a %b %d %H:%M:%S %Y")

        # sd upgrade
        cmd = "mv " + test_path + f"/{sd_src_zip} /mnt/sd/"
        ser_run_cmd(ser=ser, cmd=str(cmd))
        ser_run_cmd(ser=ser, cmd=f"cd /mnt/sd && unzip {sd_src_zip}")
        upgrade_cmds, upgrade_time = sd_upgrade_cmds(board=args.board)
        for cmd, wt in zip(upgrade_cmds, upgrade_time):
            ser_run_cmd(ser=ser, cmd=cmd, timeout=wt)

        # delete images from SD card and reboot
        cmd = "mount " + sd_dev + " /mnt/sd/"
        ser_run_cmd(ser=ser, cmd=str(cmd))
        log, ret_code, ret = ser_run_cmd(ser=ser, cmd="df -h", ret_regex=sd_dev)
        assert ret, f'Cannot mount {sd_dev}'
        cmd = "cd /mnt/sd && find . -maxdepth 1 ! -name 'res*' ! -name '.' -exec rm -rf {} \\;"
        ser_run_cmd(ser=ser, cmd=str(cmd))

        # check version
        log, _, _ = ser_run_cmd(ser=ser, cmd="uname -v")
        log = ' '.join(log.split('\n')[:])
        if not args.skip_date_check:
            if args.daily:
                today = datetime.today().strftime('%Y%m%d')
                assert is_same_day(log, today), "Update Failed"
            else:
                new_version = extract_time(time_str=log, time_format="%a %b %d %H:%M:%S %Y")
                assert pre_version != new_version, "Upgrade Fail!"

        logging.info('Upgrade Success')

    elif args.ota_src:
        print("\n=== OTA Upgrade Configuration ===\n")
        for opt in args.__dict__:
            value = str(args.__dict__[opt])
            print(f"{opt.ljust(20)}:{value}")

        if args.reboot:
            ser_run_cmd(ser=ser, cmd="reboot", timeout=100)
            time.sleep(3)  # Wait for the system to stabilize

        # Prepare the OTA source file on the host
        host_ws = args.host_ws.replace("\\", "/")
        ota_src = args.ota_src.replace("\\", "/")
        ota_src_zip = os.path.basename(ota_src)
        os.makedirs(host_ws, exist_ok=True)
        assert os.path.exists(ota_src), f"{ota_src} does not exist!"

        # Copy ota_src to host workspace if it's not already there
        dest_path = os.path.join(host_ws, ota_src_zip)
        if host_ws not in ota_src:
            shutil.copy2(ota_src, dest_path)
            logging.info(f"Copied {ota_src} to {host_ws}")

        # Mount NFS to transfer the OTA package
        test_path = args.test_path.replace("\\", "/")
        nfs_path = args.nfs_path.replace("\\", "/")
        assert ser.isOpen()
        if not args.reboot:
            cmd = "umount " + test_path
            ser_run_cmd(ser=ser, cmd=str(cmd))
        ip = get_ip(ser=ser)
        assert ip, "Cannot get IP address"
        cmd = "mkdir -p " + test_path
        ser_run_cmd(ser=ser, cmd=str(cmd))
        cmd = "mount -t nfs -o nolock " + nfs_path + " " + test_path
        ser_run_cmd(ser=ser, cmd=str(cmd))
        log, ret_code, ret = ser_run_cmd(ser=ser, cmd="df -h", ret_regex=nfs_path)
        assert ret, f'Cannot mount NFS at {test_path}'

        # Get the pre-upgrade version for comparison
        log, _, _ = ser_run_cmd(ser=ser, cmd="uname -v")
        log = ' '.join(log.split('\n')[:])
        pre_version = extract_time(time_str=log, time_format="%a %b %d %H:%M:%S %Y")

        # OTA Upgrade Specific Steps
        # 1. Create the OTA working directory on the device
        ota_dest_dir = "/mnt/data"
        cmd = f"mkdir -p {ota_dest_dir}"
        ser_run_cmd(ser=ser, cmd=cmd)

        # 2. Copy the OTA package from NFS to the device's OTA directory
        cmd = f"cp {test_path}/{ota_src_zip} {ota_dest_dir}/"
        ser_run_cmd(ser=ser, cmd=cmd)

        # 3. Navigate to the OTA directory and unzip the package
        # The script ota_for_emmc.sh is expected to be in the 'utils' directory after extraction
        cmd = f"cd {ota_dest_dir} && unzip -o {ota_src_zip}"
        ser_run_cmd(ser=ser, cmd=cmd, timeout=60)  # Allow time for unzip

        # 4. Make the OTA update script executable and run it
        ota_script_path = f"{ota_dest_dir}/utils/ota_for_emmc.sh"  # Script path after extraction
        cmd = f"chmod +x {ota_script_path}"
        ser_run_cmd(ser=ser, cmd=cmd)

        # Execute the OTA update script.
        # The timeout should be set generously as the update process may take a significant amount of time.
        logging.info("Starting OTA update script. This may take several minutes...")
        # Consider reading the expected runtime from upgrade.yaml or setting a large default
        ota_script_timeout = 600  # 10 minutes, adjust as necessary based on your board's requirements
        ser_run_cmd(ser=ser, cmd=ota_script_path, timeout=ota_script_timeout)

        # Check version post-upgrade
        log, _, _ = ser_run_cmd(ser=ser, cmd="uname -v")
        log = ' '.join(log.split('\n')[:])
        if not args.skip_date_check:
            if args.daily:
                today = datetime.today().strftime('%Y%m%d')
                assert is_same_day(log, today), "OTA Update Failed: Version date is not today's date."
            else:
                new_version = extract_time(time_str=log, time_format="%a %b %d %H:%M:%S %Y")
                assert pre_version != new_version, "OTA Upgrade Failed: Version did not change."

        logging.info('OTA Upgrade Success')
