# encoding: utf-8

import os
import sys
import datetime
import logging
import pytest

sys.path.append('../../..')
from utils.common_func import print_function
from utils.cmd import run_cmd, read_cases
from utils.download import upload_file
from utils.download import find_from_local


isp_raw_replay_cmds_file = os.path.join(
    os.path.dirname(__file__),
    "isp_raw_replay.yaml"
)


@pytest.mark.isp_raw_replay
@pytest.mark.parametrize('prepare_ws', [{'env_file': isp_raw_replay_cmds_file}], indirect=True)
@pytest.mark.parametrize(('cmd', 'check_res', 'runtime'), read_cases(isp_raw_replay_cmds_file, "isp_raw_replay"))
def test_isp_raw_replay(cmd, check_res, runtime, setup_session, prepare_ws, request):
    print_function()
    device = setup_session
    log, ret_code, ret = run_cmd(client=device,
                                 cmd=cmd,
                                 timeout=runtime,
                                 ret_regex=check_res,
                                 echo=True)

    host_ws = request.config.getoption("--host_ws").replace("\\", "/")
    LOG_FILE = find_from_local(path=host_ws, recursive=True, ret_regex="rawReplayTest_*.log")
    assert len(LOG_FILE), 'Test Fail!'
    assert ret_code == 0, 'Test case execute timeout'

    # read log file
    log_path = LOG_FILE[0].pre_path + "/" + LOG_FILE[0].name
    log = open(log_path, 'r').read()
    logging.info(log)
    if log.find(check_res) == -1:
        # test fail: upload result
        date = datetime.today().strftime('%Y%m%d')
        yuv_files = find_from_local(path=host_ws, recursive=True, ret_regex=f"image_0_0_{date}.yuv")
        assert len(yuv_files), 'Test Fail!'
        yuv_file_path = yuv_files[0].pre_path + "/" + yuv_files[0].name
        upload_file(src=yuv_file_path, dst="/data/isp_mw/isp_test_data/images/", host="10.80.40.1", user="isp_mw", pwd="123456")
        assert ret, 'Test Fail!'
