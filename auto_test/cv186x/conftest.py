# encoding: utf-8

import os
import sys
import time
from datetime import datetime
import shutil
import logging
import pytest

sys.path.append('.')
from init_conf import CUSTOMER_OPTIONS  # 导入自定义配置
sys.path.append('..')
from utils.common_func import print_function, is_same_day
from utils.cmd import run_cmd
from utils.prepare import read_env_file
from utils.serial_utils import init_serial, get_ip
from utils.ssh_utils import init_ssh_channel


def pytest_html_results_summary(prefix, summary, postfix):
    """报告增加log格式"""
    prefix.extend([
        '<style>',
        '.log-info { color: green; }',
        '.log-warning { color: orange; }',
        '.log-error { color: red; font-weight: bold; }',
        '</style>'
    ])


# pylint: disable=fixme
def pytest_addoption(parser):
    """添加自定义命令行参数"""
    for group_name, options in CUSTOMER_OPTIONS.items():
        group = parser.getgroup(group_name)
        for opt, kwargs in options.items():
            # 过滤掉 None 值(例如 type=None 的 store_true 动作)
            filtered_kwargs = {k: v for k, v in kwargs.items() if v is not None}
            group.addoption(opt, **filtered_kwargs)


def pytest_configure(config):
    """配置阶段"""
    # 打印接收到的参数
    print("\n=== Customer Configuration ===\n")
    for group_name, options in CUSTOMER_OPTIONS.items():
        print(f"\n[Group: {group_name}]")
        for opt in options:
            value = config.getoption(opt)
            print(f"{opt.ljust(20)}:{value}")


@pytest.fixture(scope="session", autouse=True)
def setup_session(request):
    """
    Function: Establish Connection to Device

    Logic:
    1. LTPU device using host-device mode
    2. establish serial connection or ssh connection according options;
    3. mkdir test_path and change to test_path for device
    4. return serial.Serial or paramiko.Channel
    """
    print_function()
    device = None

    serial_port = request.config.getoption("--serial_port")
    device_ip = request.config.getoption("--ip")
    if serial_port:
        device = init_serial(serial_port)
        assert device, f'{serial_port}: connect fail!'
    elif device_ip:
        user = request.config.getoption("--user")
        pwd = request.config.getoption("--pwd")
        device = init_ssh_channel(ip=device_ip, user=user, pwd=pwd)
        assert device, f'{device_ip}: connect fail!'

    if request.config.getoption("--reboot"):
        run_cmd(client=device, cmd="reboot", timeout=100)
        time.sleep(3)       # wait for dhcp
        ip = get_ip(ser=device)
        assert ip, "Cannot get ip"

    test_path = request.config.getoption("--test_path").replace("\\", "/")
    cmd = "mkdir -p " + test_path + " && cd " + test_path + " && pwd"
    run_cmd(client=device,
            cmd=str(cmd),
            timeout=3)
    sd_dev = request.config.getoption("--sd_dev")
    cmd = "mount " + sd_dev + " /mnt/sd"
    run_cmd(client=device,
            cmd=str(cmd),
            timeout=3)

    def teardown_setup_session():
        print_function()
        run_cmd(client=device, cmd="cd ~", timeout=1)
        device.close()

    return device


@pytest.fixture(scope="session", autouse=True)
def check_img_ver(setup_session, request):
    """
    Function: Check SDK Version
    Logic:
    If --daily is specified, check if the board has updated to the latest SDK.
    """
    print_function()
    if request.config.getoption("--daily"):
        today = datetime.today().strftime('%Y%m%d')

        device = setup_session
        log, _, _ = run_cmd(client=device, cmd="uname -v", timeout=3)
        log = ' '.join(log.split('\n')[:])
        assert is_same_day(log, today), "Update Failed"
    else:
        logging.info('Not check image version')
        return


_module_workspaces = {}


@pytest.fixture(scope="module")
def prepare_ws(setup_session, request):
    """
    Function: Organize the test space
    Logic:
    1. Create independent workspace for each test module;
    2. Read "env_file" and prepare test workspace.
    3. clean workspace after module test
    """
    print_function()
    module_id = id(request.module)
    logging.info(f"module_id:{module_id}")

    # 如果该模块的工作空间不存在则创建
    if module_id not in _module_workspaces:
        # 获取参数化配置
        request_keys = request.param.keys() if hasattr(request, 'param') else ''
        env_file = request.param["env_file"] if 'env_file' in request_keys else ''
        logging.info(f"Creating workspace for module: {request.module.__name__}")

        # 创建主机上的工作目录
        workspace_path_pc = request.config.getoption("--host_ws").replace("\\", "/")
        os.makedirs(workspace_path_pc, exist_ok=True)

        # nfs 挂载
        device = setup_session
        nfs_path = request.config.getoption("--nfs_path").replace("\\", "/")
        test_path = request.config.getoption("--test_path").replace("\\", "/")
        src = nfs_path[:-1] if nfs_path.endswith("/") else nfs_path
        log, _, _ = run_cmd(client=device, cmd="df -h", timeout=3)
        if src not in log:
            cmd = f"mount -t nfs -o nolock {nfs_path} {test_path}"
            run_cmd(client=device, cmd=str(cmd))
        log, _, _ = run_cmd(client=device, cmd="df -h", timeout=3)
        assert src in log, 'mount nfs fail'

        # 初始化环境
        read_env_file(env_file, request, device)

        # 存储工作空间
        _module_workspaces[module_id] = {
            "path": workspace_path_pc,
            "env": env_file,
            "status": "ready"
        }

    yield _module_workspaces[module_id]

    if module_id in _module_workspaces:
        cmd = "umount " + test_path
        run_cmd(client=device, cmd=str(cmd), timeout=3)
        # 模块测试结束后清理工作空间
        if request.config.getoption("--clean"):
            logging.warning(f"Cleaning workspace for module: {request.module.__name__}")
            workspace_path_pc = _module_workspaces[module_id]["path"]
            if os.path.exists(workspace_path_pc):
                shutil.rmtree(workspace_path_pc)
            del _module_workspaces[module_id]


@pytest.fixture(scope="function", autouse=True)
def change_workspace(setup_session, request):
    """
    Function: change test workspace
    """
    print_function()
    device = setup_session
    test_path = request.config.getoption("--test_path").replace("\\", "/")
    cmd = "cd " + test_path + " && pwd"
    run_cmd(client=device, cmd=str(cmd), timeout=3)

    def return_cwd():
        run_cmd(client=device,
                cmd="cd ~ && pwd",
                timeout=3)

    request.addfinalizer(return_cwd)
