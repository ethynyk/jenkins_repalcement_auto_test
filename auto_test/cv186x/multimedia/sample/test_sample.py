# encoding: utf-8

import os
import sys
import pytest

sys.path.append('../../..')
from utils.common_func import print_function
from utils.cmd import run_cmd, read_cases

sample_cmds_file = os.path.join(
    os.path.dirname(__file__),
    "sample.yaml"
)

pytstmark = [
    pytest.mark.multimedia
]


@pytest.mark.sample
@pytest.mark.sample_audio
@pytest.mark.run(order=1)
@pytest.mark.parametrize('prepare_ws', [{'env_file': sample_cmds_file}], indirect=True)
@pytest.mark.parametrize(('cmd', 'check_res', 'runtime'), read_cases(sample_cmds_file, "sample_audio"))
def test_sample_audio(cmd, check_res, runtime, setup_session, prepare_ws, request):
    print_function()
    device = setup_session
    # ./auto_test.sh sample_audio -1 SCREEN_TYPE BOARD
    params = [cmd, "-1", str(request.config.getoption("--screen_type")), str(request.config.getoption("--board"))]
    cmd = " ".join(params)
    log, ret_code, ret = run_cmd(client=device,
                                 cmd=str(cmd),
                                 timeout=runtime,
                                 ret_regex=check_res,
                                 echo=True)
    assert log, 'Device happens some errors, please check.'
    if not ret:     # test fail, print dmesg
        run_cmd(client=device, cmd="dmesg", timeout=10, echo=True)
        assert ret_code == 0, 'Test Fail! Timeout'
        assert ret, 'Test Fail!'


@pytest.mark.sample
@pytest.mark.sample_gdc
@pytest.mark.run(order=3)
@pytest.mark.parametrize('prepare_ws', [{'env_file': sample_cmds_file}], indirect=True)
@pytest.mark.parametrize(('cmd', 'check_res', 'runtime'), read_cases(sample_cmds_file, "sample_gdc"))
def test_sample_gdc(cmd, check_res, runtime, setup_session, prepare_ws, request):
    print_function()
    device = setup_session
    log, ret_code, ret = run_cmd(client=device,
                                 cmd=cmd,
                                 timeout=runtime,
                                 ret_regex=check_res,
                                 echo=True)
    assert log, 'Device happens some errors, please check.'
    if not ret:     # test fail, print dmesg
        run_cmd(client=device, cmd="dmesg", timeout=10, echo=True)
        assert ret_code == 0, 'Test Fail! Timeout'
        assert ret, 'Test Fail!'


@pytest.mark.sample
@pytest.mark.sample_panel
@pytest.mark.run(order=4)
@pytest.mark.parametrize('prepare_ws', [{'env_file': sample_cmds_file}], indirect=True)
@pytest.mark.parametrize(('cmd', 'check_res', 'runtime'), read_cases(sample_cmds_file, "sample_panel"))
def test_sample_panel(cmd, check_res, runtime, setup_session, prepare_ws, request):
    print_function()
    device = setup_session
    # ./auto_test.sh sample_panel -1 SCREEN_TYPE BOARD
    params = [cmd, "-1", str(request.config.getoption("--screen_type")), str(request.config.getoption("--board"))]
    cmd = " ".join(params)
    log, ret_code, ret = run_cmd(client=device,
                                 cmd=str(cmd),
                                 timeout=runtime,
                                 ret_regex=check_res,
                                 echo=True)
    assert log, 'Device happens some errors, please check.'
    if not ret:     # test fail, print dmesg
        run_cmd(client=device, cmd="dmesg", timeout=10, echo=True)
        assert ret_code == 0, 'Test Fail! Timeout'
        assert ret, 'Test Fail!'


@pytest.mark.sample
@pytest.mark.sample_sensor
@pytest.mark.run(order=6)
@pytest.mark.parametrize('prepare_ws', [{'env_file': sample_cmds_file}], indirect=True)
@pytest.mark.parametrize(('cmd', 'check_res', 'runtime'), read_cases(sample_cmds_file, "sensor_test"))
def test_sample_sensor(cmd, check_res, runtime, setup_session, prepare_ws, request):
    print_function()
    device = setup_session
    # ./auto_test.sh sample_sensor SENROR_NUM null BOARD
    params = [cmd, str(request.config.getoption("--sensor_num")), "null", str(request.config.getoption("--board"))]
    cmd = " ".join(params)
    log, ret_code, ret = run_cmd(client=device,
                                 cmd=str(cmd),
                                 timeout=runtime,
                                 ret_regex=check_res,
                                 echo=True)
    assert log, 'Device happens some errors, please check.'
    if not ret:     # test fail, print dmesg
        run_cmd(client=device, cmd="dmesg", timeout=10, echo=True)
        assert ret_code == 0, 'Test Fail! Timeout'
        assert ret, 'Test Fail!'


@pytest.mark.sample
@pytest.mark.sample_tde
@pytest.mark.run(order=7)
@pytest.mark.parametrize('prepare_ws', [{'env_file': sample_cmds_file}], indirect=True)
@pytest.mark.parametrize(('cmd', 'check_res', 'runtime'), read_cases(sample_cmds_file, "sample_tde"))
def test_sample_tde(cmd, check_res, runtime, setup_session, prepare_ws, request):
    print_function()
    device = setup_session
    log, ret_code, ret = run_cmd(client=device,
                                 cmd=cmd,
                                 timeout=runtime,
                                 ret_regex=check_res,
                                 echo=True)
    assert log, 'Device happens some errors, please check.'
    if not ret:     # test fail, print dmesg
        run_cmd(client=device, cmd="dmesg", timeout=10, echo=True)
        assert ret_code == 0, 'Test Fail! Timeout'
        assert ret, 'Test Fail!'


@pytest.mark.sample
@pytest.mark.sample_vpss
@pytest.mark.run(order=8)
@pytest.mark.parametrize('prepare_ws', [{'env_file': sample_cmds_file}], indirect=True)
@pytest.mark.parametrize(('cmd', 'check_res', 'runtime'), read_cases(sample_cmds_file, "sample_vpss"))
def test_sample_vpss(cmd, check_res, runtime, setup_session, prepare_ws, request):
    print_function()
    device = setup_session
    log, ret_code, ret = run_cmd(client=device,
                                 cmd=cmd,
                                 timeout=runtime,
                                 ret_regex=check_res,
                                 echo=True)
    assert log, 'Device happens some errors, please check.'
    if not ret:     # test fail, print dmesg
        run_cmd(client=device, cmd="dmesg", timeout=10, echo=True)
        assert ret_code == 0, 'Test Fail! Timeout'
        assert ret, 'Test Fail!'


@pytest.mark.sample
@pytest.mark.sample_vio
@pytest.mark.run(order=9)
@pytest.mark.parametrize('prepare_ws', [{'env_file': sample_cmds_file}], indirect=True)
@pytest.mark.parametrize(('cmd', 'check_res', 'runtime'), read_cases(sample_cmds_file, "sample_vio"))
def test_sample_vio(cmd, check_res, runtime, setup_session, prepare_ws, request):
    print_function()
    device = setup_session
    # ./auto_test.sh sample_vio SENROR_NUM SCREEN_TYPE BOARD
    params = [cmd, str(request.config.getoption("--sensor_num")), str(request.config.getoption("--screen_type")), str(request.config.getoption("--board"))]
    cmd = " ".join(params)
    log, ret_code, ret = run_cmd(client=device,
                                 cmd=str(cmd),
                                 timeout=runtime,
                                 ret_regex=check_res,
                                 echo=True)
    assert log, 'Device happens some errors, please check.'
    if not ret:     # test fail, print dmesg
        run_cmd(client=device, cmd="dmesg", timeout=10, echo=True)
        assert ret_code == 0, 'Test Fail! Timeout'
        assert ret, 'Test Fail!'


@pytest.mark.sample
@pytest.mark.sample_region
@pytest.mark.run(order=10)
@pytest.mark.parametrize('prepare_ws', [{'env_file': sample_cmds_file}], indirect=True)
@pytest.mark.parametrize(('cmd', 'check_res', 'runtime'), read_cases(sample_cmds_file, "sample_region"))
def test_sample_region(cmd, check_res, runtime, setup_session, prepare_ws, request):
    print_function()
    device = setup_session
    # ./auto_test.sh sample_region -1 SCREEN_TYPE BOARD
    params = [cmd, "-1", str(request.config.getoption("--screen_type")), str(request.config.getoption("--board"))]
    cmd = " ".join(params)
    log, ret_code, ret = run_cmd(client=device,
                                 cmd=str(cmd),
                                 timeout=runtime,
                                 ret_regex=check_res,
                                 echo=True)
    assert log, 'Device happens some errors, please check.'
    if not ret:     # test fail, print dmesg
        run_cmd(client=device, cmd="dmesg", timeout=10, echo=True)
        assert ret_code == 0, 'Test Fail! Timeout'
        assert ret, 'Test Fail!'
