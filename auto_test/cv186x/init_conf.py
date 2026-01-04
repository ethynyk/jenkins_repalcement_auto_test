CUSTOMER_OPTIONS = {
    "Base Test Parameters": {
        "--serial_port": {
            "action": "store",
            "type": str,
            "default": None,
            "help": "Serial port connected to client. (mutually exclusive with --ip)"
        },
        "--ip": {
            "action": "store",
            "type": str,
            "default": None,
            "help": "IP address connected to client. (mutually exclusive with --serial_port)"
        },
        "--user": {
            "action": "store",
            "type": str,
            "default": "root",
            "help": "User name logining to client. (require --ip)"
        },
        "--pwd": {
            "action": "store",
            "type": str,
            "default": "cvitek",
            "help": "Password logining to client. (require --ip)"
        },
        "--board": {
            "action": "store",
            "type": str,
            "default": "device_wevb_emmc",
            "help": "Board"
        },
        "--sd_dev": {
            "action": "store",
            "type": str,
            "default": "/dev/mmcblk1p1",
            "help": "Devices corresponding to SD card slots"
        },
        "--test_path": {
            "action": "store",
            "type": str,
            "default": "/mnt/nfs",
            "help": "Directory where execute test commands"
        },
        "--host_ws": {
            "action": "store",
            "type": str,
            "default": "D:/jenkins",
            "help": "prepare test files to host workspace"
        },
        "--nfs_path": {
            "action": "store",
            "type": str,
            "default": "192.168.1.10:/nfs",
            "help": "NFS mount path in host (require --host_ws)"
        },
        "--clean": {
            "action": "store_true",
            "default": False,
            "help": "clean host_ws"
        },
        "--reboot": {
            "action": "store_true",
            "default": False,
            "help": "whether reboot board"
        }
    },
    "SDK Parameters": {
        "--daily": {
            "action": "store_true",
            "default": False,
            "help": "Whether check board version"
        },
        "--branch": {
            "action": "store",
            "type": str,
            "default": "dailly_build",
            "choices": ["daily_build", "release_build", "hk_release"],
            "help": "${branch} in *.yaml"
        },
        "--sdk_version": {
            "action": "store",
            "type": str,
            "default": "latest_release",
            "help": "${sdk_version} in *.yaml"
        }
    },
    "BSP Test Parameters": {},  # 空参数组
    "Multimedia Test Parameters": {},   # 空参数组
    "ISP Test Parameters": {
        "--cvipqtool_ver": {
            "action": "store",
            "type": str,
            "default": "<newest>",
            "help": "${cvipqtool_ver}in *.yaml"
        }
    },
    "TDL_SDK Test Parameters": {
        "--model_ver": {
            "action": "store",
            "type": str,
            "default": "latest_release",
            "help": "${model_ver}in *.yaml"
        }
    }
}
