import re
import time
from typing import Union, Tuple
import logging
import paramiko


def init_ssh_client(ip: str,
                    user: str,
                    pwd: str,
                    port: int = 22) -> paramiko.SSHClient:
    """
    Create a new SSHClient and connect to it.

    :param str ip: the server to connect to
    :param str user: the username to authenticate as (defaults to the current local username)
    :param str pwd: used for password authentication
    :param int port: the server port to connect to
    """
    max_retries = 3
    ssh_client = None

    for attempt in range(max_retries):
        try:
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(hostname=ip, username=user, password=pwd, port=port, timeout=10)
            logging.info(f'SSHClient: \"{ip}\" connect success!')
            return ssh_client
        except (paramiko.AuthenticationException, paramiko.SSHException) as e:
            logging.error(f'SSHClient: \"{ip}\" | {str(e)}')
            break   # 认证失败, 无需再试
        except Exception as e:
            logging.error(f'SSHClient: \"{ip}\" connect fail ({attempt+1}/{max_retries}) | {str(e)}')
            if attempt < max_retries - 1:
                logging.warning('Retry after 3s...')
                time.sleep(3)
        finally:
            # connect fail and clean resource
            if attempt > 0 and ssh_client and not ssh_client.get_transport().is_active():
                ssh_client.close()
    return None


def init_ssh_channel(ip: str,
                     user: str,
                     pwd: str,
                     port: int = 22) -> paramiko.Channel:
    """
    Start an interactive shell session on the SSH server.

    :param str ip: the server to connect to
    :param str user: the username to authenticate as (defaults to the current local username)
    :param str pwd: used for password authentication
    :param int port: the server port to connect to
    """
    ssh_channel = None
    ssh_client = init_ssh_client(ip=ip, user=user, pwd=pwd, port=port)
    ssh_channel = ssh_client.invoke_shell()
    ssh_channel.settimeout(30)
    return ssh_channel


def send_break_signal_ssh(ssh_channel: paramiko.Channel):
    """
    Send CTRL+C to SSH server.

    :param paramiko.Channel ssh_channel: the interactive shell session.
    """
    try:
        logging.warning('Timeout')
        ssh_channel.send('\x03')
        ssh_channel.send('\x03')
        time.sleep(0.5)
        logging.debug(f'send CTRL+C to \"{ssh_channel}\" ')
    except Exception as e:
        logging.error(f'send CTRL+C to \"{ssh_channel}\": fail! {e}')


def raw_to_string(raw_data):
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    output = ""
    try:
        decoded = raw_data.decode('utf-8', errors='replace')
        output = ansi_escape.sub('', decoded).replace('\r\n', '\n')
    except UnicodeDecodeError:
        try:
            decoded = raw_data.decode('gbk', errors='replace')
            output = ansi_escape.sub('', decoded).replace('\r\n', '\n')
        except:
            output = str(raw_data)
    return output


def ssh_run_cmd(ssh_channel: paramiko.Channel,
                cmd: str,
                timeout: int = 5,
                ret_regex: Union[str, re.Pattern] = None,
                echo=True,
                prompt_cmd: str = r"\[root@cvitek\][^\#]+\#") -> Tuple[str, int, list]:
    """
    Executes the command on SSH server, and handles output reading.

    :param paramiko.Channel ssh_channel: paramiko.Channel type object
    :param str cmd: The command to execute (add '\\n' automatically).
    :param int timeout: Maximum time to wait for execution.
    :param Union[str, re.Pattern] ret_regex: Regular expressions used to extract the output
    :param bool echo: whether read log
    :param str prompt_cmd: Command line prompt.

    :return Tuple[str, int, list]: (log, ret_code, ret)
    """
    # init result variables
    log = ""
    ret_code = 0    # 0: success; 1: fail(include timeout)
    ret = []

    # init temp variables
    full_output = []
    is_timeout = False
    check_time = min(20, timeout)

    # clear buffer
    while ssh_channel.recv_ready():
        ssh_channel.recv(1024)

    cmd = cmd.strip() if cmd.strip().endswith("\n") else cmd.strip() + '\n'
    start_time = time.time()

    ssh_channel.send(cmd)
    logging.info(f'SSH Channel: send command \"{cmd}\" to {ssh_channel}')
    logging.info('****** return messages start ******')

    while True and echo:
        time.sleep(1)
        while ssh_channel.recv_ready():
            raw_data = ssh_channel.recv(4096)
            full_output.append(raw_data)
            time.sleep(0.2)

        spend_time = time.time() - start_time
        last_output = raw_to_string(full_output[-1]) if full_output else ""

        if spend_time > timeout:
            if prompt_cmd and last_output and re.search(prompt_cmd, last_output):
                is_timeout = False
            else:
                is_timeout = True
            break

        # prompt_cmd: str = r"\[root@cvitek\][^\#]+\#"
        if spend_time > check_time and prompt_cmd:
            if last_output and re.search(prompt_cmd, last_output):
                break

    if echo:
        for item in full_output:
            log += raw_to_string(item)
        logging.info(log.encode('utf-8', errors='replace').decode('utf-8'))

        if ret_regex:
            if type(ret_regex) == str:
                ret = re.findall(ret_regex, log)
            else:
                ret = ret_regex.findall(log)

        if is_timeout and cmd.strip().startswith("./"):
            ret_code = 1
            send_break_signal_ssh(ssh_channel)

    if not echo and timeout > 0:
        time.sleep(timeout)

    logging.info('****** return messages end ******')
    logging.info(f"SSH Channel: execute {time.time() - start_time:.2f}s")

    return log, ret_code, ret
