# encoding: utf-8

import os
import sys
import pytest

sys.path.append('../../..')
from utils.common_func import print_function
from utils.cmd import run_cmd, read_cases

auto_test_cmds_file = os.path.join(
    os.path.dirname(__file__),
    "auto_test.yaml"
)

pytstmark = [
    pytest.mark.multimedia
]


@pytest.mark.auto_test
@pytest.mark.dpu_ut
@pytest.mark.run(order=1)
@pytest.mark.parametrize('prepare_ws', [{'env_file': auto_test_cmds_file}], indirect=True)
@pytest.mark.parametrize(('cmd', 'check_res', 'runtime'), read_cases(auto_test_cmds_file, "dpu_ut"))
def test_dpu_ut(cmd, check_res, runtime, setup_session, prepare_ws, request):
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


@pytest.mark.auto_test
@pytest.mark.rgn_ut
@pytest.mark.run(order=2)
@pytest.mark.parametrize('prepare_ws', [{'env_file': auto_test_cmds_file}], indirect=True)
@pytest.mark.parametrize(('cmd', 'check_res', 'runtime'), read_cases(auto_test_cmds_file, "rgn_ut"))
def test_rgn_ut(cmd, check_res, runtime, setup_session, prepare_ws, request):
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


@pytest.mark.auto_test
@pytest.mark.vi_ut
@pytest.mark.run(order=3)
@pytest.mark.parametrize('prepare_ws', [{'env_file': auto_test_cmds_file}], indirect=True)
@pytest.mark.parametrize(('cmd', 'check_res', 'runtime'), read_cases(auto_test_cmds_file, "vi_ut"))
def test_vi_ut(cmd, check_res, runtime, setup_session, prepare_ws, request):
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


@pytest.mark.auto_test
@pytest.mark.tde_ut
@pytest.mark.run(order=4)
@pytest.mark.parametrize('prepare_ws', [{'env_file': auto_test_cmds_file}], indirect=True)
@pytest.mark.parametrize(('cmd', 'check_res', 'runtime'), read_cases(auto_test_cmds_file, "tde_ut"))
def test_tde_ut(cmd, check_res, runtime, setup_session, prepare_ws, request):
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


@pytest.mark.auto_test
@pytest.mark.ive_ut
@pytest.mark.run(order=5)
@pytest.mark.parametrize('prepare_ws', [{'env_file': auto_test_cmds_file}], indirect=True)
@pytest.mark.parametrize(('cmd', 'check_res', 'runtime'), read_cases(auto_test_cmds_file, "ive_ut"))
def test_ive_ut(cmd, check_res, runtime, setup_session, prepare_ws, request):
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


@pytest.mark.auto_test
@pytest.mark.sys_ut
@pytest.mark.run(order=6)
@pytest.mark.parametrize('prepare_ws', [{'env_file': auto_test_cmds_file}], indirect=True)
@pytest.mark.parametrize(('cmd', 'check_res', 'runtime'), read_cases(auto_test_cmds_file, "sys_ut"))
def test_sys_ut(cmd, check_res, runtime, setup_session, prepare_ws, request):
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


@pytest.mark.auto_test
@pytest.mark.vb_ut
@pytest.mark.run(order=7)
@pytest.mark.parametrize('prepare_ws', [{'env_file': auto_test_cmds_file}], indirect=True)
@pytest.mark.parametrize(('cmd', 'check_res', 'runtime'), read_cases(auto_test_cmds_file, "vb_ut"))
def test_vb_ut(cmd, check_res, runtime, setup_session, prepare_ws, request):
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


@pytest.mark.auto_test
@pytest.mark.vo_ut
@pytest.mark.run(order=8)
@pytest.mark.parametrize('prepare_ws', [{'env_file': auto_test_cmds_file}], indirect=True)
@pytest.mark.parametrize(('cmd', 'check_res', 'runtime'), read_cases(auto_test_cmds_file, "vo_ut"))
def test_vo_ut(cmd, check_res, runtime, setup_session, prepare_ws, request):
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


@pytest.mark.auto_test
@pytest.mark.stitch_ut
@pytest.mark.run(order=9)
@pytest.mark.parametrize('prepare_ws', [{'env_file': auto_test_cmds_file}], indirect=True)
@pytest.mark.parametrize(('cmd', 'check_res', 'runtime'), read_cases(auto_test_cmds_file, "stitch_ut"))
def test_stitch_ut(cmd, check_res, runtime, setup_session, prepare_ws, request):
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


@pytest.mark.auto_test
@pytest.mark.vpss_ut
@pytest.mark.run(order=10)
@pytest.mark.parametrize('prepare_ws', [{'env_file': auto_test_cmds_file}], indirect=True)
@pytest.mark.parametrize(('cmd', 'check_res', 'runtime'), read_cases(auto_test_cmds_file, "vpss_ut"))
def test_vpss_ut(cmd, check_res, runtime, setup_session, prepare_ws, request):
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


@pytest.mark.auto_test
@pytest.mark.gdc_ut
@pytest.mark.run(order=11)
@pytest.mark.parametrize('prepare_ws', [{'env_file': auto_test_cmds_file}], indirect=True)
@pytest.mark.parametrize(('cmd', 'check_res', 'runtime'), read_cases(auto_test_cmds_file, "gdc_ut"))
def test_gdc_ut(cmd, check_res, runtime, setup_session, prepare_ws, request):
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
