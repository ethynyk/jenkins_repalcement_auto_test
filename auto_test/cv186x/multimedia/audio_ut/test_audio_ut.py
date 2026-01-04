# encoding: utf-8

import os
import sys
import pytest

sys.path.append('../../..')
from utils.common_func import print_function
from utils.cmd import run_cmd, read_cases

audio_ut_cmds_file = os.path.join(
    os.path.dirname(__file__),
    "audio_ut.yaml"
)

pytstmark = [
    pytest.mark.multimedia
]


@pytest.mark.audio_ut
@pytest.mark.aud_in
@pytest.mark.run(order=1)
@pytest.mark.parametrize('prepare_ws', [{'env_file': audio_ut_cmds_file}], indirect=True)
@pytest.mark.parametrize(('cmd', 'check_res', 'runtime'), read_cases(audio_ut_cmds_file, "aud_in"))
def test_aud_in(cmd, check_res, runtime, setup_session, prepare_ws, request):
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


@pytest.mark.audio_ut
@pytest.mark.aud_out
@pytest.mark.run(order=2)
@pytest.mark.parametrize('prepare_ws', [{'env_file': audio_ut_cmds_file}], indirect=True)
@pytest.mark.parametrize(('cmd', 'check_res', 'runtime'), read_cases(audio_ut_cmds_file, "aud_out"))
def test_aud_out(cmd, check_res, runtime, setup_session, prepare_ws, request):
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


@pytest.mark.audio_ut
@pytest.mark.aud_transcode
@pytest.mark.run(order=3)
@pytest.mark.parametrize('prepare_ws', [{'env_file': audio_ut_cmds_file}], indirect=True)
@pytest.mark.parametrize(('cmd', 'check_res', 'runtime'), read_cases(audio_ut_cmds_file, "aud_transcode"))
def test_aud_transcode(cmd, check_res, runtime, setup_session, prepare_ws, request):
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


@pytest.mark.audio_ut
@pytest.mark.aud_resample
@pytest.mark.run(order=4)
@pytest.mark.parametrize('prepare_ws', [{'env_file': audio_ut_cmds_file}], indirect=True)
@pytest.mark.parametrize(('cmd', 'check_res', 'runtime'), read_cases(audio_ut_cmds_file, "aud_resample"))
def test_aud_resample(cmd, check_res, runtime, setup_session, prepare_ws, request):
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


@pytest.mark.audio_ut
@pytest.mark.aud_aec
@pytest.mark.run(order=5)
@pytest.mark.parametrize('prepare_ws', [{'env_file': audio_ut_cmds_file}], indirect=True)
@pytest.mark.parametrize(('cmd', 'check_res', 'runtime'), read_cases(audio_ut_cmds_file, "aud_aec"))
def test_aud_aec(cmd, check_res, runtime, setup_session, prepare_ws, request):
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


@pytest.mark.audio_ut
@pytest.mark.aud_anr
@pytest.mark.run(order=6)
@pytest.mark.parametrize('prepare_ws', [{'env_file': audio_ut_cmds_file}], indirect=True)
@pytest.mark.parametrize(('cmd', 'check_res', 'runtime'), read_cases(audio_ut_cmds_file, "aud_anr"))
def test_aud_anr(cmd, check_res, runtime, setup_session, prepare_ws, request):
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


@pytest.mark.audio_ut
@pytest.mark.aud_up_record
@pytest.mark.run(order=7)
@pytest.mark.parametrize('prepare_ws', [{'env_file': audio_ut_cmds_file}], indirect=True)
@pytest.mark.parametrize(('cmd', 'check_res', 'runtime'), read_cases(audio_ut_cmds_file, "aud_up_record"))
def test_aud_up_record(cmd, check_res, runtime, setup_session, prepare_ws, request):
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


@pytest.mark.audio_ut
@pytest.mark.aud_up_vqe
@pytest.mark.run(order=8)
@pytest.mark.parametrize('prepare_ws', [{'env_file': audio_ut_cmds_file}], indirect=True)
@pytest.mark.parametrize(('cmd', 'check_res', 'runtime'), read_cases(audio_ut_cmds_file, "aud_up_vqe"))
def test_aud_up_vqe(cmd, check_res, runtime, setup_session, prepare_ws, request):
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


@pytest.mark.audio_ut
@pytest.mark.aud_up_enc
@pytest.mark.run(order=9)
@pytest.mark.parametrize('prepare_ws', [{'env_file': audio_ut_cmds_file}], indirect=True)
@pytest.mark.parametrize(('cmd', 'check_res', 'runtime'), read_cases(audio_ut_cmds_file, "aud_up_enc"))
def test_aud_up_enc(cmd, check_res, runtime, setup_session, prepare_ws, request):
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


@pytest.mark.audio_ut
@pytest.mark.aud_up_bind
@pytest.mark.run(order=10)
@pytest.mark.parametrize('prepare_ws', [{'env_file': audio_ut_cmds_file}], indirect=True)
@pytest.mark.parametrize(('cmd', 'check_res', 'runtime'), read_cases(audio_ut_cmds_file, "aud_up_bind"))
def test_aud_up_bind(cmd, check_res, runtime, setup_session, prepare_ws, request):
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


@pytest.mark.audio_ut
@pytest.mark.aud_up_user
@pytest.mark.run(order=11)
@pytest.mark.parametrize('prepare_ws', [{'env_file': audio_ut_cmds_file}], indirect=True)
@pytest.mark.parametrize(('cmd', 'check_res', 'runtime'), read_cases(audio_ut_cmds_file, "aud_up_user"))
def test_aud_up_user(cmd, check_res, runtime, setup_session, prepare_ws, request):
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


@pytest.mark.audio_ut
@pytest.mark.aud_up_vqe_aec
@pytest.mark.run(order=12)
@pytest.mark.parametrize('prepare_ws', [{'env_file': audio_ut_cmds_file}], indirect=True)
@pytest.mark.parametrize(('cmd', 'check_res', 'runtime'), read_cases(audio_ut_cmds_file, "aud_up_vqe_aec"))
def test_aud_up_vqe_aec(cmd, check_res, runtime, setup_session, prepare_ws, request):
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


@pytest.mark.audio_ut
@pytest.mark.aud_play_out
@pytest.mark.run(order=13)
@pytest.mark.parametrize('prepare_ws', [{'env_file': audio_ut_cmds_file}], indirect=True)
@pytest.mark.parametrize(('cmd', 'check_res', 'runtime'), read_cases(audio_ut_cmds_file, "aud_play_out"))
def test_aud_play_out(cmd, check_res, runtime, setup_session, prepare_ws, request):
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


@pytest.mark.audio_ut
@pytest.mark.aud_resample_out
@pytest.mark.run(order=14)
@pytest.mark.parametrize('prepare_ws', [{'env_file': audio_ut_cmds_file}], indirect=True)
@pytest.mark.parametrize(('cmd', 'check_res', 'runtime'), read_cases(audio_ut_cmds_file, "aud_resample_out"))
def test_aud_resample_out(cmd, check_res, runtime, setup_session, prepare_ws, request):
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
