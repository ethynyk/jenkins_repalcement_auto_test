import re
from typing import Union, Tuple
import paramiko
import serial
from yaml import load as yaml_load
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

from utils.serial_utils import ser_run_cmd
from utils.ssh_utils import ssh_run_cmd
from utils.host_utils import host_run_cmd


def run_cmd(client: Union[paramiko.SSHClient, serial.Serial] = None,
            cmd: str = "",
            timeout: int = 5,
            ret_regex: Union[str, re.Pattern] = None,
            echo=True) -> Tuple[str, int, list]:
    """
    Run command.

    :param Union[paramiko.SSHClient, serial.Serial] client: commands executor for host-client mode
    :param str cmd: The commands
    :param int timeout: The command execution timeout period (seconds) which is 5 seconds by default
    :param Union[str, re.Pattern] ret_regex: Regular expressions used to extract the output
    :param bool echo: Whether to print out logs in real time, True by default

    :return Tuple[str, int, list]:  (log, ret_code, ret)
    """
    # ret_code: 0: success; 1: fail(include timeout)
    if type(client) == paramiko.Channel:
        log, ret_code, ret = ssh_run_cmd(ssh_channel=client,
                                         cmd=cmd,
                                         timeout=timeout,
                                         ret_regex=ret_regex,
                                         echo=echo)
    elif type(client) == serial.Serial:
        log, ret_code, ret = ser_run_cmd(ser=client,
                                         cmd=cmd,
                                         timeout=timeout,
                                         ret_regex=ret_regex,
                                         echo=echo)
    else:
        log, ret_code, ret = host_run_cmd(cmd=cmd,
                                          timeout=timeout,
                                          ret_regex=ret_regex,
                                          echo=echo)
    return log, ret_code, ret


def read_cases(cases_file: str, marker: str):
    """
    Read test cases from *.yaml

    :param str case_file: *.yaml
    :param str marker: see in pytest.ini
    """
    with open(cases_file, 'r', encoding='utf-8') as f:
        cases = yaml_load(f, Loader=Loader)
        if 'test_cases' in cases:
            test_marker_cases = cases['test_cases'][marker]
            return [(x['case'],
                     x.get('check_res', 'PASS'),
                     x.get('runtime', 1)) for x in test_marker_cases]
        else:
            assert False, f'No valid \"testcase\" or \"cmds\" key found in the \"{cases_file}\"'
