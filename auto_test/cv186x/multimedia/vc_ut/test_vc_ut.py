# encoding: utf-8

import os
import sys
import pytest

sys.path.append('../../..')
from utils.common_func import print_function
from utils.cmd import run_cmd, read_cases

vc_ut_cmds_file = os.path.join(
    os.path.dirname(__file__),
    "vc_ut.yaml"
)

pytstmark = [
    pytest.mark.multimedia
]


@pytest.mark.vc_ut
@pytest.mark.dec
@pytest.mark.run(order=1)
@pytest.mark.parametrize('prepare_ws', [{'env_file': vc_ut_cmds_file}], indirect=True)
@pytest.mark.parametrize(('cmd', 'check_res', 'runtime'), read_cases(vc_ut_cmds_file, "dec"))
def test_dec(cmd, check_res, runtime, setup_session, prepare_ws, request):
    print_function()
    device = setup_session
    log, ret_code, ret = run_cmd(client=device,
                                 cmd=cmd,
                                 timeout=runtime,
                                 ret_regex=check_res,
                                 echo=True)
    assert log, 'Device happens some errors, please check.'
    assert ret_code == 0, 'Test case execute timeout'
    if not ret:     # test fail, print dmesg
        run_cmd(client=device, cmd="dmesg", timeout=10, echo=True)
    assert ret, 'Test Fail!'


@pytest.mark.vc_ut
@pytest.mark.enc
@pytest.mark.run(order=1)
@pytest.mark.parametrize('prepare_ws', [{'env_file': vc_ut_cmds_file}], indirect=True)
@pytest.mark.parametrize(('cmd', 'check_res', 'runtime'), read_cases(vc_ut_cmds_file, "enc"))
def test_enc(cmd, check_res, runtime, setup_session, prepare_ws, request):
    print_function()
    device = setup_session
    log, ret_code, ret = run_cmd(client=device,
                                 cmd=cmd,
                                 timeout=runtime,
                                 ret_regex=check_res,
                                 echo=True)
    assert log, 'Device happens some errors, please check.'
    assert ret_code == 0, 'Test case execute timeout'
    if not ret:     # test fail, print dmesg
        run_cmd(client=device, cmd="dmesg", timeout=10, echo=True)
    assert ret, 'Test Fail!'
