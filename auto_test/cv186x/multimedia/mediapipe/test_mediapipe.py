import os
import sys
import pytest

sys.path.append('../..')
from utils.common_func import print_function
from utils.cmd import run_cmd, read_cases

mediapipe_cmds_file = os.path.join(
    os.path.dirname(__file__),
    "mediapipe.yaml"
)


# ./auto_test.sh TEST_APP INI_NAME TIMEOUT SENSOR_NUM SCREEN_TYPE BOARD

@pytest.mark.mediapipe
@pytest.mark.basic_ini
@pytest.mark.run(order=1)
@pytest.mark.parametrize('prepare_ws', [{'env_file': mediapipe_cmds_file}], indirect=True)
@pytest.mark.parametrize(('cmd', 'check_res', 'runtime'), read_cases(mediapipe_cmds_file, "basic_ini"))
def test_basic_ini(cmd, check_res, runtime, setup_session, prepare_ws, request):
    print_function()
    device = setup_session
    params = [cmd, "-1", "null", "null"]
    cmd = " ".join(params)
    log, ret_code, ret = run_cmd(client=device,
                                 cmd=str(cmd),
                                 timeout=runtime,
                                 ret_regex=check_res,
                                 echo=True)
    assert log, 'Device happens some errors, please check.'
    assert ret_code == 0, 'Test case execute timeout'
    assert ret, 'Test Fail!'
