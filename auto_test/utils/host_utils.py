import sys
import re
import logging
import subprocess
import threading
import time
from typing import Union, Tuple


def host_run_cmd(cmd: str,
                 timeout: int = 5,
                 ret_regex: Union[str, re.Pattern] = None,
                 echo: bool = True,
                 waittime: int = 0,
                 prompt_cmd: str = r"\[root@cvitek\][^\#]+\#") -> Tuple[str, int, list]:
    """
    Cross-platform command execution functions

    :param str cmd: The string of commands to be executed
    :param int timeout: The command execution timeout period (seconds), which is 5 seconds by default
    :param Union[str, re.Pattern] ret_regex: Regular expressions (strings or compiled regexes) used to extract the output
    :param bool echo: Whether to print out logs in real time, True by default
    :param str prompt_cmd: Command line prompt.

    :return Tuple[str, int, list]:  (log, ret_code, ret)
    """
    # init result variables
    log = ""
    ret_code = 0    # 0: success; 1: fail(contains timeout)
    ret = []

    # check platform
    is_windows = sys.platform.startswith('win')

    # Windows path process
    if is_windows:
        cmd = re.sub(r'/(\w+)/', r'\\\1\\', cmd)  # 替换路径分隔符
        cmd = re.sub(r'^/(\w+)', r'\1:', cmd)      # 替换根路径格式

    # prepare save log
    full_log = []
    # Timeout control variables
    timed_out = [False]

    def kill_process(process, timeout_flag):
        """Timeout process function"""
        time.sleep(timeout)
        if process.poll() is None:  # check the process is running
            timeout_flag[0] = True
            try:
                process.terminate()  # try to terminate
                time.sleep(0.5)
                if process.poll() is None:
                    process.kill()   # kill process
            except Exception as e:
                logging.error(f"Error terminating process: {e}")

    # execute command
    logging.debug(f'Running command: {cmd}')
    proc = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,  # text mode
        bufsize=1,  # rows buffer
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if is_windows else 0
    )

    if waittime:
        time.sleep(waittime)

    # Start timeout monitor thread
    timeout_thread = threading.Thread(
        target=kill_process,
        args=(proc, timed_out),
        daemon=True
    )
    timeout_thread.start()

    start_time = time.time()
    logging.info('****** return messages start ******')
    # read realtime output
    for line in proc.stdout:
        # process each line of output
        line = line.rstrip('\n').rstrip('\r')
        full_log.append(line)

        # # prompt_cmd: str = r"\[root@cvitek\][^\#]+\#"
        if prompt_cmd and line and re.search(prompt_cmd, line):
            break

        # match ret_regex
        if ret_regex:
            try:
                if isinstance(ret_regex, str):
                    found = re.findall(ret_regex, line)
                else:
                    found = ret_regex.findall(line)

                if found:
                    # 处理多个匹配结果
                    if isinstance(found, list):
                        ret.extend(found)
                    else:
                        ret.append(found)
            except Exception as e:
                logging.error(f"Regex error: {e}")

    # wait for process ending
    try:
        proc.wait(timeout=1)  # 短时间等待确保进程退出
    except subprocess.TimeoutExpired:
        pass

    # full log
    if echo:
        log = "\n".join(full_log)
        logging.info(log)

    # clear timeout threads
    if timeout_thread.is_alive():
        timeout_thread.join(0.1)

    if timed_out[0]:
        logging.warning('Timeout')
        ret_code = 1

    logging.info('****** return messages end ******')
    logging.info(f"Host device: execute in {time.time()-start_time:.2f}s")

    return log, ret_code, None
