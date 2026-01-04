# encoding: utf-8

import os
import sys
import pytest

sys.path.append('../..')
from utils.common_func import print_function
from utils.cmd import run_cmd, read_cases

tdl_sdk_cmds_file = os.path.join(
    os.path.dirname(__file__),
    "tdl_sdk.yaml"
)


@pytest.mark.tdl_sdk
@pytest.mark.parametrize('prepare_ws', [{'env_file': tdl_sdk_cmds_file}], indirect=True)
@pytest.mark.parametrize(('cmd', 'check_res', 'runtime'), read_cases(tdl_sdk_cmds_file, "tdl_sdk"))
def test_tdl_sdk(cmd, check_res, runtime, setup_session, prepare_ws, request):
    print_function()
    device = setup_session
    log, ret_code, ret = run_cmd(client=device,
                                 cmd=cmd,
                                 timeout=runtime,
                                 ret_regex=check_res,
                                 echo=True)
    assert log, 'Device happens some errors, please check.'
    assert ret_code == 0, 'Test case execute timeout'
    assert ret, 'Test Fail!'

