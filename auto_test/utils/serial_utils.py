import re
import time
from typing import Union, Tuple, List
import logging
import serial
from serial.tools import list_ports


SEIRAL_STATUS = {
    0: "FREE",
    1: "BUSY",
    2: "UNAVAILABLE",
    3: "BAD_SSH",
    4: "NOT_IN_LINUX",
}


def init_serial(ser_port: str) -> serial.Serial:
    """
    Create a new Serial and connect to it.

    :param str ser_port: serial port
    """
    ser_baudrate = 115200
    ser_timeout = 15
    ser = serial.Serial(
        port=ser_port,
        baudrate=ser_baudrate,
        timeout=ser_timeout
    )
    if ser.isOpen():
        logging.info(f'Serial \"{ser_port}\" connect success!')
        return ser
    ser.close()
    return False


def send_break_signal_serial(ser: serial.Serial):
    """
    Send CTRL+C to Serial.

    :param serial.Serial ser: the serial object
    """
    try:
        logging.warning('Timeout')
        ser.write(b'\x03')
        ser.write(b'\x03')
        time.sleep(0.5)
        logging.info(f'send CTRL+C to \"{ser.port}\" ')
    except Exception as e:
        logging.error(f'send CTRL+C to \"{ser.port}\": fail! {e}')


def raw_to_string(raw_data):
    try:
        # 0. UTF-8 decode
        decoded = raw_data.decode('utf-8', errors='replace')
    except UnicodeDecodeError:
        # 1. GBK decode
        decoded = raw_data.decode('gbk', errors='replace')

    # 2. replace \r\n with \n, replace \r with \n
    cleaned = decoded.replace('\r\n', '\n')

    # 3. remove ANSI escape code
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    chunk_threshold = 100000
    if len(cleaned) <= chunk_threshold:
        # case 1: small data
        return ansi_escape.sub('', cleaned)
    else:
        # case 2: large data
        chunks = [cleaned[i:i + 50000] for i in range(0, len(cleaned), 50000)]
        result_chunks = [ansi_escape.sub('', chunk) for chunk in chunks]
        return ''.join(result_chunks)


def ser_run_cmd(
        ser: serial.Serial,
        cmd: str,
        timeout: int = 5,
        ret_regex: Union[str, re.Pattern] = None,
        echo: bool = True,
        prompt_cmd: str = r"\[root@cvitek\][^\#]+\#") -> Tuple[str, int, list]:
    """
    Executes the command on Serial object, and handles output reading.

    :param serial.Serial ser: serial.Serial type object
    :param str cmd: The command to execute (add '\\n' automatically).
    :param int timeout: (default 5s) Maximum time to wait for execution.
    :param Union[str, re.Pattern] ret_regex: Regular expressions used to extract the output
    :param bool echo: whether read log
    :param str prompt_cmd: Command line prompt.

    :return Tuple[str, int, list]: (log, ret_code, ret)
    """
    # init result variables
    log = ""
    ret_code = 0    # 0: success; 1: fail(contains timeout)
    ret = []

    # clear buffer
    ser.reset_input_buffer()
    ser.reset_output_buffer()

    cmd_bytes = (cmd.strip() + '\r').encode('utf-8')
    start_time = time.time()

    ser.write(cmd_bytes)
    logging.info(f'Serial cmd: send command \"{cmd}\" to {ser.port}')
    logging.info('****** return messages start ******')

    if echo:
        # init temp variables
        full_output = []
        is_timeout = False
        check_time = min(20, timeout)
        time.sleep(0.2)

        while True:
            no_data_count = 0       # change waittime for log dynamically
            max_no_data_count = 10
            while no_data_count < max_no_data_count:
                if time.time() - start_time > timeout:
                    break

                while ser.in_waiting > 0:
                    chrunk_size = min(ser.in_waiting, 8192)
                    raw_data = ser.read(chrunk_size)
                    print(raw_data, end="")
                    full_output.append(raw_data)
                    no_data_count = 0

                no_data_count += 1
                time.sleep(0.05)

            if full_output:
                # check prompt_cmd
                # prompt_cmd: str = r"\[root@cvitek\][^\#]+\#"
                if len(full_output) > 3:
                    raw_data = b''.join(full_output[-3:])
                else:
                    raw_data = b''.join(full_output[:])
                last_output = raw_to_string(raw_data)

                # case 1: timeout and check
                spend_time = time.time() - start_time
                if spend_time > timeout:
                    if prompt_cmd and last_output and re.search(prompt_cmd, last_output):
                        is_timeout = False
                    else:
                        is_timeout = True
                    break

                # case 2: execute at least 20s and check
                if spend_time > check_time:
                    if last_output and re.search(prompt_cmd, last_output):
                        break

        raw_data = b''.join(full_output[:])
        log = raw_to_string(raw_data)
        logging.info(log.encode('utf-8', errors='replace').decode('utf-8', errors='replace'))

        if ret_regex:
            if type(ret_regex) == str:
                ret = re.findall(ret_regex, log)
            else:
                ret = ret_regex.findall(log)

        if is_timeout and cmd.strip().startswith("./"):
            ret_code = 1
            send_break_signal_serial(ser)

    else:
        # For situations where echo is not needed
        if timeout > 0:
            time.sleep(timeout)

    logging.info('****** return messages end ******')
    logging.info(f"Serial cmd: execute {time.time()-start_time:.2f}s")

    return log, ret_code, ret


def get_ip(ser: serial.Serial,
           cmd: str = "ifconfig eth0 | grep 'inet addr:'") -> str:
    """
    Get ip address of Serial object.

    :param serial.Serial ser: serial.Serial type object
    :param str cmd: The command to execute (add '\\n' automatically).

    :return str: ip address
    """
    ip_re = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')     # regular expression for ip address
    for _ in range(3):
        _, _, ret = ser_run_cmd(ser=ser, cmd=cmd, ret_regex=ip_re)
        if len(ret):
            return ret[0]
    return


def list_all_serial() -> List[str]:
    """
    List all serial device

    :return list[str]: serial port list
    """
    ports_list = list_ports.comports()
    assert len(ports_list) <= 0, "No serial device"
    devices = [p for p, _, _ in ports_list]
    return devices


def check_status_serial(serial: Union[str, serial.Serial], prompt_cmd=r"\[root@cvitek\][^\#]+\#"):
    """
    Check serial device status

    :param Union[str, serial.Serial] serial: serial port or Serial object

    :return int status: status code
    SEIRAL_STATUS = {
        0: "FREE",
        1: "BUSY",
        2: "UNAVAILABLE",
        3: "BAD_SSH",
        4: "NOT_IN_LINUX",
    )
    """
    status = -1
    if type(serial) == str:
        ser = init_serial(serial)
        if ser.isOpen():
            log, ret_code, _ = ser_run_cmd(ser=ser, cmd=" ", timeout=1)
            if log and ret_code == 0:
                status = 0
            elif ret_code:
                status = 2
            # prompt_cmd: str = r"\[root@cvitek\][^\#]+\#"
            if status == 0 and prompt_cmd and not re.search(prompt_cmd, log.splitlines()[-1]):
                status = 4
            if status == 0 and not get_ip(ser):
                status = 3
            ser.close()
        else:
            status = 1
        logging.info(f'{serial} status: {SEIRAL_STATUS[status]}')
    elif type(serial) == serial.Serial:
        log, ret_code = ser_run_cmd(ser=serial, cmd=" ", timeout=1)
        if log and ret_code == 0:
            status = 0
        elif ret_code:
            status = 2
        # prompt_cmd: str = r"\[root@cvitek\][^\#]+\#"
        if status == 0 and prompt_cmd and not re.search(prompt_cmd, log.splitlines()[-1]):
            status = 4
        if status == 0 and not get_ip(serial):
            status = 3
        logging.info(f'{serial.port} status: {SEIRAL_STATUS[status]}')
    return status
