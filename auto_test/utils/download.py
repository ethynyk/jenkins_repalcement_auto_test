import os
import re
from typing import List, Generator, Dict
import logging
from stat import S_ISDIR as isdir
from datetime import datetime
import paramiko
from utils.ssh_utils import init_ssh_client


def init_sftp(ip: str,
              user: str,
              pwd: str,
              port: int = 22) -> paramiko.SFTPClient:
    """
    Init SFTPClient and set keepalive=100s

    :param str ip: the server to connect to
    :param str user: the username to authenticate as (defaults to the current local username)
    :param str pwd: used for password authentication
    :param int port: the server port to connect to
    """
    sftp = None
    ssh_client = init_ssh_client(ip=ip, user=user, pwd=pwd, port=port)
    ssh_transport = ssh_client.get_transport()
    ssh_transport.set_keepalive(20)
    sftp = ssh_client.open_sftp()
    return sftp


class FileObj:
    """FileObj class"""
    def __init__(self, name: str, pre_path: str, mtime: datetime, isdir: bool, size: int):
        self.name = name
        self.pre_path = pre_path
        self.mtime = mtime
        self.isdir = isdir
        self.size = size


def walk(sftp: paramiko.SFTPClient, path: str) -> Generator:
    """List all dir"""
    try:
        dirs, nondirs = [], []
        for entry in sftp.listdir_attr(path):
            if isdir(entry.st_mode):
                dirs.append(entry.filename)
            else:
                nondirs.append(entry.filename)
        yield path, dirs, nondirs

        for dir_name in dirs:
            new_path = os.path.join(path, dir_name)
            yield from walk(sftp, new_path)
    except Exception as e:
        logging.warning(f"Skipping {path} | {str(e)}")


def find_from_sftp(sftp: paramiko.SFTPClient,
                   path: str,
                   recursive: bool = False,
                   ret_regex: re.Pattern = None,
                   latest: bool = False) -> List[FileObj]:
    """
    find files or folders in remote path

    :param paramiko.SFTPClient sftp: SFTPClient object
    :param path: remote path to search
    :param recursive: whether search recursively
    :param ret_regex: Regular expressions (strings or compiled regexes) used to extract the output
    :param latest: whether search newest

    :return List[FileObj]: matched FileObj list (name, parent absolute path, timestamp, isdir, size)
    """
    entries = []
    try:
        if recursive:
            for root, _, filenames in walk(sftp, path):
                for filename in filenames:
                    full_path = os.path.join(root, filename)
                    if ret_regex:
                        if not re.fullmatch(ret_regex, filename):
                            continue
                    stat = sftp.stat(full_path)
                    file = FileObj(filename,
                                    root,
                                    datetime.fromtimestamp(stat.st_mtime),
                                    isdir(stat.st_mode),
                                    stat.st_size)
                    entries.append(file)
        else:
            for entry in sftp.listdir_attr(path):
                full_path = os.path.join(path, entry.filename)
                if ret_regex:
                    if not re.fullmatch(ret_regex, entry.filename):
                        continue
                stat = sftp.stat(full_path)
                file = FileObj(entry.filename,
                                path,
                                datetime.fromtimestamp(stat.st_mtime),
                                isdir(stat.st_mode),
                                stat.st_size)
                entries.append(file)

        if latest and entries:
            return [max(entries, key=lambda x: x.mtime)]
        return entries
    except Exception as e:
        logging.error(f'Find from sftp: match \"{ret_regex}\" in \"{path}\" fail | {str(e)}')
        raise


def find_from_local(path: str,
                    recursive: bool = False,
                    ret_regex: re.Pattern = None,
                    latest: bool = False
                    ) -> List[FileObj]:
    """
    find files or folders in local path

    :param str path: remote path to search
    :param bool recursive: whether search recursively
    :param re.Pattern ret_regex: Regular expressions (strings or compiled regexes) used to extract the output
    :param bool latest: whether search newest

    :return List[FileObj]: matched FileObj list (name, parent absolute path, timestamp, isdir, size)
    """
    entries = []
    if not os.path.exists(path):
        return []

    abs_path = os.path.abspath(path)

    pattern = None
    if ret_regex is not None:
        if isinstance(ret_regex, str):
            pattern = re.compile(ret_regex)
        else:
            pattern = ret_regex

    for root, dirs, files in os.walk(abs_path):
        for file in files:
            if pattern is not None or pattern.match(file):
                full_path = os.path.join(root, file)
                mtime = datetime.fromtimestamp(os.path.getmtime(full_path))
                size = os.path.getsize(full_path)
                entries.append(FileObj(file, root, mtime, False, size))

        # 处理当前目录下的文件夹
        for dir_name in dirs:
            if pattern is None or pattern.match(dir_name):
                full_path = os.path.join(root, dir_name)
                mtime = datetime.fromtimestamp(os.path.getmtime(full_path))
                # 文件夹大小设为0（或使用os.path.getsize获取元数据大小）
                size = 0
                entries.append(FileObj(dir_name, root, mtime, True, size))

        # 非递归模式只处理当前目录
        if not recursive:
            break

    # 处理latest参数
    if latest and entries:
        # 按修改时间降序排序
        entries.sort(key=lambda x: x.mtime, reverse=True)
        return [entries[0]]

    return entries


def download_from_sftp(
    sftp: paramiko.SFTPClient,
    remote_path: str,
    local_path: str,
    recursive: bool = True
) -> Dict[str, int]:
    """
    Download files or folders from SFTP

    :param paramiko.SFTPClient sftp: paramiko.SFTPClient
    :param str remote_path: remote path
    :param str local_path: local saved path
    :param bool recursive: whether download recursively

    :return Dict[str, int]: result dictionary
    """
    result = {'success': 0, 'failed': 0}

    try:
        stat = sftp.stat(remote_path)
        if isdir(stat.st_mode):
            os.makedirs(local_path, exist_ok=True)

            entries = sftp.listdir_attr(remote_path)
            logging.info('Attempt to download from sftp')
            logging.info(entries)

            for entry in entries:
                remote_file = os.path.join(remote_path, entry.filename).replace("\\", "/")
                local_file = os.path.join(local_path, entry.filename).replace("\\", "/")
                if isdir(entry.st_mode) and recursive:
                    sub_result = download_from_sftp(sftp=sftp,
                                                    remote_path=remote_file,
                                                    local_path=local_file,
                                                    recursive=recursive)
                    result['success'] += sub_result['success']
                    result['failed'] += sub_result['failed']
                elif not isdir(entry.st_mode):
                    try:
                        sftp.get(remote_file, local_file)
                        # 保持权限
                        os.chmod(local_file, entry.st_mode)
                        result['success'] += 1
                        logging.info(f"Download: {local_path} <== {remote_path}")
                    except Exception as e:
                        result['failed'] += 1
                        logging.error(f"Download: {local_path} <== {remote_path} fail | {e}")
        else:
            filename = os.path.basename(remote_path)
            os.makedirs(local_path, exist_ok=True)
            local_file = os.path.join(local_path, filename).replace("\\", "/")
            sftp.get(remote_path, local_file)
            # 保持权限
            os.chmod(local_file, stat.st_mode)
            result['success'] += 1
            logging.info(f"Download: {local_file} <== {remote_path}")
    except Exception as e:
        result['failed'] += 1
        logging.error(f"Download: {local_path} <== {remote_path} fail | {e}")

    logging.info(
        f"Download Results:\n"
        f" - success: {result['success']} files\n"
        f" - failed: {result['failed']} files"
    )

    return result


def upload_file(src: str,
                dst: str,
                ip: str,
                user: str = "root",
                pwd: str = "cvitek",
                try_times: int = 3):
    """
    Upload file to board by ssh connection

    :param str src: local source file
    :param str dst: remote path
    :param str ip: the ip address of board
    :param str user: the username to authenticate as
    :param str pwd: used for password authentication
    :param int try_times: default try three times
    """
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())
        ssh.connect(hostname=ip, username=user, password=pwd, auth_timeout=5)
        ssh_transport = ssh.get_transport()
        ssh_transport.set_keepalive(20)
        sftp = ssh.open_sftp()
        sftp.put(src, dst)
        sftp.close()
        ssh.close()
        logging.info(f'Upload file from \"{src}\" to \"{ip}:{dst}\" success!')
    except BaseException as e:
        if try_times == 0:
            logging.error(f'Upload file from \"{src}\" to \"{ip}:{dst}\" fail!')
            raise e
        else:
            upload_file(src, dst, ip, user, pwd, try_times - 1)
