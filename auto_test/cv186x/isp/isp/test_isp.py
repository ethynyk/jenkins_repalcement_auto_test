# encoding: utf-8

import os
import sys
import logging
import pytest

sys.path.append('../../..')
from utils.common_func import print_function
from utils.cmd import run_cmd, read_cases
from utils.serial_utils import get_ip
from utils.host_utils import host_run_cmd


isp_cmds_file = os.path.join(
    os.path.dirname(__file__),
    "isp.yaml"
)


@pytest.mark.isp
@pytest.mark.parametrize('prepare_ws', [{'env_file': isp_cmds_file}], indirect=True)
@pytest.mark.parametrize(('cmd', 'check_res', 'runtime'), read_cases(isp_cmds_file, "isp"))
def test_isp(cmd, check_res, runtime, setup_session, prepare_ws, request):
    print_function()
    device = setup_session
    if request.config.getoption("--ip"):
        host = request.config.getoption("--ip")
    else:
        host = get_ip(device)

    # run isp-tool-daemon in device
    log, ret_code, ret = run_cmd(client=device,
                                 cmd=cmd,
                                 timeout=runtime,
                                 ret_regex=check_res,
                                 echo=True)

    # run CviPQTool.exe in Windows
    tool_path = os.path.join(request.config.getoption("--host_ws").replace("\\", "/"),
                             "ISPTOOL")
    vlc = "D:/software/VideoLAN/VLC/vlc.exe"
    cmd = f'cd {tool_path} && python autoTest.py CviPQTool.exe log.txt {host} "{vlc}"'
    host_run_cmd(cmd=str(cmd),
                 echo=True,
                 waittime=200)

    log_file = os.path.join(tool_path,
                            'my_log.log')
    log = open(log_file, 'r').read()
    logging.info(f"{log_file}: {log}")
    assert log.find('ISP_PQTOOL test PASS') != -1, 'Test Fail!'
