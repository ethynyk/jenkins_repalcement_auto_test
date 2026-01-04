import os
import re
import tarfile
import zipfile
from typing import List
from stat import S_ISDIR as isdir
import logging
import shutil
import paramiko
import pytest
import yaml

from utils.download import init_sftp, download_from_sftp, find_from_local, find_from_sftp
from utils.cmd import run_cmd
from utils.common_func import print_function


def config_to_dict(config) -> dict:
    """把request.config转化成字典类型"""
    # 提取命令行选项
    options = {name: config.getoption(name) for name in config.option.__dict__.keys()}
    # 提取 ini 配置项
    ini_values = {name: config.getini(name) for name in config._inicache.keys()}
    # 合并为一个字典, 若有重复则命令行的选项值覆盖 ini 配置项
    return ini_values.update(options)


def replace_params(config: list, params: pytest.Config) -> dict:
    """
    动态配置替换: 把config中${var}替换成动态配置params中的值
    """
    # 定义匹配${var}模式的正则表达式
    pattern = r'\$\{([^}]+)\}'
    
    def replacer(match):
        var_name = match.group(1)
        try:
            # 从params中获取变量值
            var_value = params.getoption(var_name)
            return str(var_value) if var_value is not None else match.group(0)
        except (ValueError, AttributeError):
            # 如果变量不存在，保持原样
            return match.group(0)

    for item_cfg in config:
        for field in item_cfg.keys():
            if isinstance(item_cfg[field], str):
                input_str = item_cfg[field]
                item_cfg[field] = re.sub(pattern, replacer, input_str)
    return config


def extract_regex_segments(config: list) -> dict:
    """
    提取路径中的正则表达式的部分

    :return:
    处理后的每个路径字段${field}将添加一个_info后缀的新字段${field}_info
    包含以下数据结构:
        {
            "parts": [
                "路径段1",
                "<正则表达式1>",
                "路径段2",
                "<正则表达式2>"
            ],
            "regex_segments": [
                "正则表达式1",
                "正则表达式2"
            ]
        }
    """
    for item_cfg in config:
        fields = list(item_cfg.keys())
        for field in fields:
            # 跳过不含正则表达式或非字符串的部分
            if not isinstance(item_cfg[field], str):
                continue
            elif '<' not in item_cfg[field] or '>' not in item_cfg[field]:
                continue

            path_str = item_cfg[field]
            parts = []
            regex_segments = []
            current = path_str

            # 循环提取所有正则表达式段
            while '<' in current and '>' in current:
                # 查找每一对 '<' '>'
                start_idx = current.index('<')
                end_idx = current.index('>', start_idx)

                if start_idx > 0:
                    # 添加正则表达式前的普通文本
                    parts.append(current[:start_idx])

                # 提取正则表达式部分（不带尖括号）
                regex_content = current[start_idx + 1:end_idx]
                regex_segments.append(regex_content)
                parts.append(f"<{regex_content}>")  # 保留尖括号

                current = current[end_idx + 1:]

            if current:
                parts.append(current)

            item_cfg.update({
                f"{field}_info": {
                    "parts": parts,
                    "regex_segments": regex_segments
                }
            })
    return config


def parse_url(url: str) -> dict:
    """
    提取路径中的url信息

    :return:
    url_info, 数据结构:
        {
            "protocol": str,
            "hostname": str,
            "port": str,
            "user": str,
            "pwd": str,
            "path": str
        }
    """
    regex = re.compile(
        r"^(?P<protocol>[a-zA-Z][a-zA-Z0-9+.-]*):\/\/"  # 协议
        r"(?:(?P<user>[^:@]+)(?::(?P<pwd>[^@]*))?@)?"  # 用户名和密码
        r"(?P<hostname>[^:\/?#]+)"  # 主机名
        r"(?::(?P<port>\d+))?"  # 端口
        r"(?P<path>\/[^?#]*)?"  # 路径
    )

    match = regex.match(url)
    if match:
        url_info = match.groupdict()
        return url_info
    return None


def find(path_info: dict, sftp: paramiko.SFTPClient = None) -> List[str]:
    """
    筛选符合条件的所有文件

    :param dict path_info:
    path_info 是一个字典类型,数据结构如下:
        {
            "parts": [
                "路径段1",
                "<正则表达式1>",
                "路径段2",
                "<正则表达式2>"
            ],
            "regex_segments": [
                "正则表达式1",
                "正则表达式2"
            ]
        }

    :return List[str]:
    路径列表
    """
    logging.info(path_info['parts'])

    parts = path_info['parts']
    regex_segments = path_info['regex_segments']
    regex_index = 0     # 跟踪当前使用的正则表达式索引

    current_paths = [str(parts[0])]   # 初始当前路径集
    for part in parts[1:]:
        next_paths = []
        if part.startswith('<') and part.endswith('>'):
            # 处理正则表达式部分: 检查当前路径下的所有匹配子路径
            if part == "<newest>":
                latest = True
                pattern = None
            else:
                pattern = re.compile(regex_segments[regex_index])
                latest = False
            regex_index += 1

            for path in current_paths:
                if sftp:
                    matches = find_from_sftp(sftp=sftp,
                                             path=path,
                                             ret_regex=pattern,
                                             latest=latest)
                else:
                    matches = find_from_local(path=path,
                                              ret_regex=pattern,
                                              latest=latest)
                for match in matches:
                    full_path = os.path.join(match.pre_path, match.name)
                    next_paths.append(str(full_path))
        else:
            # 处理路径段部分: 检查当前所有路径的子路径是否存在
            for path in current_paths:
                new_path = path + part      # 可能存在part是'/'的情况, 所以使用+连接, 而不是使用os.path.join()
                if sftp and sftp.stat(new_path):    # sftp.stat可以用来判断远程路径是否存在
                    next_paths.append(new_path)
                elif not sftp and os.path.exists(new_path):     # 如果是本地路径
                    next_paths.append(new_path)
        current_paths = [str(each) for each in next_paths]
    return current_paths


def check_isdir(path: str, sftp: paramiko.SFTPClient = None):
    """检查path的是文件还是文件夹"""
    if sftp:
        stat = sftp.stat(path=path)
        return isdir(stat.st_mode)
    else:
        return os.path.isdir(path)


def action_download(url_info: dict, source, target):
    """下载

    :param dict url_info:
    url_info 数据结构:
    {
        "protocol": str,
        "hostname": str,
        "port": str,
        "user": str,
        "pwd": str,
        "path": str
    }
    """
    print_function()
    result = {'success': 0, 'failed': 0}
    # 如果是ftp的url连接，则使用sftp方式下载
    if url_info['protocol'] in ["ftp"]:
        sftp = init_sftp(ip=url_info['hostname'],
                         user=url_info['user'],
                         pwd=url_info['pwd'])
        if isinstance(source, str):
            files = [source]
        elif isinstance(source, dict):
            files = find(path_info=source, sftp=sftp)
        for file in files:
            result = download_from_sftp(sftp=sftp,
                                        remote_path=file,
                                        local_path=target,
                                        recursive=True)
        sftp.close()
    else:   # TODO: 其他协议待补充
        logging.error("Need to add other download code for other protocal")
    return result['failed'] == 0


def action_extract(source, target):
    """将压缩包提取到taret目录下"""
    print_function()
    if not isinstance(source, str):
        files = find(path_info=source)
    else:
        files = [source]
    for file in files:
        os.makedirs(target, exist_ok=True)
        if zipfile.is_zipfile(file):
            with zipfile.ZipFile(file, "r") as zip_ref:
                zip_ref.extractall(target)
        elif tarfile.is_tarfile(file):
            with tarfile.open(file, "r:*") as tar_ref:
                tar_ref.extractall(target, filter=None)
        else:
            logging.error(f"Extract Fail: {file} => {target}")
            return False
    return True


def action_board_link(device, source, target):
    """在板端执行软连接操作"""
    print_function()
    if not isinstance(source, str):
        logging.error(f"Board link: {source} must be string")
        return False
    source = source.replace("\\", "/")
    target = target.replace("\\", "/")
    cmd = f"ln -sf {source} {target}"
    log, _, _ = run_cmd(client=device, cmd=str(cmd), timeout=3)
    # 常见的一些错误
    log = log.lower()
    if "no such file" in log:
        return False
    elif "permission deny" in log:
        return False
    elif "file exists" in log:
        return False
    return True


def action_board_move(device, source, target):
    """在板端执行移动操作"""
    print_function()
    if not isinstance(source, str):
        logging.error(f"Board link: {source} must be string")
        return False
    source = source.replace("\\", "/")
    target = target.replace("\\", "/")
    cmd = f"mv {source} {target}"
    log, _, _ = run_cmd(client=device, cmd=str(cmd))
    # 常见的一些错误
    log = log.lower()
    if "no such file" in log:
        return False
    return True


def action_board_copy(device, source, target):
    """在板端执行移动操作"""
    print_function()
    if not isinstance(source, str):
        logging.error(f"Board link: {source} must be string")
        return False
    source = source.replace("\\", "/")
    target = target.replace("\\", "/")
    cmd = f"cp -f {source} {target}"
    log, _, _ = run_cmd(client=device, cmd=str(cmd))
    # 常见的一些错误
    log = log.lower()
    if "no such file" in log:
        return False
    return True


def action_move(source, target):
    """移动文件或目录"""
    print_function()
    if not isinstance(source, str):
        files = find(path_info=source)
    else:
        files = [source]
    for file in files:
        os.makedirs(target, exist_ok=True)
        try:
            shutil.move(src=file, dst=target)
        except Exception as e:
            logging.error(f'Move: \"{file}\" to \"{target}\" fail | {e}')
            return False
    return True


def action_rename(source, target):
    """重命名文件或目录"""
    print_function()
    if not isinstance(source, str):
        files = find(path_info=source)
    else:
        files = [source]
    for file in files:
        try:
            os.rename(file, target)
        except Exception as e:
            logging.error(f"Rename: \"{file}\" to \"{target}\" fail | {e}")
            return False
    return True


def action_copy(source, target):
    """拷贝文件或目录"""
    print_function()
    if not isinstance(source, str):
        files = find(path_info=source)
    else:
        files = [source]
    for file in files:
        os.makedirs(target, exist_ok=True)
        try:
            shutil.move(src=file, dst=target)
        except Exception as e:
            logging.error(f"Copy: \"{file}\" to \"{target}\" fail | {e}")
            return False
    return True


def action_delete(source):
    """删除文件或目录"""
    print_function()
    if not isinstance(source, str):
        files = find(path_info=source)
    else:
        files = [source]
    for file in files:
        try:
            if check_isdir(file):
                shutil.rmtree(file)
            else:
                os.remove(file)
        except Exception as e:
            logging.error(f"Delete: \"{file}\" fail | {e}")
            return False
    return True


def action_board_nfs(device, source, target):
    """在板端执行nfs挂载操作"""
    print_function()
    nfs_pattern = r'^\d{1,3}(\.\d{1,3}){3}:/.*$'
    if not re.match(nfs_pattern, source):
        logging.error(f"NFS source format error: {source} should be like x.x.x.x:/path")
        return False
    # 检查板端目标路径是否可用
    cmd = f"mkdir -p {target}"
    log, _, _ = run_cmd(client=device, cmd=str(cmd), timeout=3)
    cmd = f"mount -t nfs -o nolock {source} {target}"
    log, _, _ = run_cmd(client=device, cmd=str(cmd))
    log, _, _ = run_cmd(client=device, cmd="df -h")
    src = source[:-1] if source.endswith("/") else source
    if src not in log:
        return False
    return True


def read_env_file(env_file, request, device):
    """
    解析和处理env_file文件中的测试环境配置

    Logic:
    1. 读取env_file文件;
    2. 替换动态配置, "${}";
    3. 正则路径处理, "<>";
    4. 按照action属性处理文件和目录
    """
    print_function()
    # 读取env_file文件
    with open(env_file, "rb") as f:
        raw_data = yaml.safe_load(f)
    env_config = raw_data['test_environment_configs']       # list

    # 替换动态配置
    env_config = replace_params(config=env_config, params=request.config)

    # 正则路径处理
    env_config = extract_regex_segments(env_config)

    # 按照action属性处理文件和目录
    for env_op in env_config:
        action = env_op['action']
        desc = env_op['desc']
        if 'source_info' in env_op.keys():
            source = env_op['source_info']
        else:
            source = env_op['source']
        target = env_op['target'] if env_op['target'] else None

        logging.info(f'{desc}')
        if action == "download":
            # 下载操作之前，解析url，并从路径字符串中去除ip相关信息
            if isinstance(source, str):
                url_info = parse_url(source)
                source = url_info['path']
            else:
                url_info = parse_url(source['parts'][0])
                source['parts'][0] = url_info['path']
            assert action_download(url_info=url_info,
                                   source=source,
                                   target=target), f"Download {source} fail!"
        elif action == "board_link":
            assert action_board_link(device, source, target), f"Link {source} on board fail!"
        elif action == "board_move":
            assert action_board_move(device, source, target), f"Move {source} on board fail!"
        elif action == "board_copy":
            assert action_board_copy(device, source, target), f"Copy {source} on board fail!"
        elif action == "board_nfs":
            assert action_board_nfs(device, source, target), f"mount nfs dir {source} to {target} on board fail!"
        elif action == "extract":
            assert action_extract(source, target), f"Extract {source} fail!"
        elif action == "move":
            assert action_move(source, target), f"Move {source} fail!"
        elif action == "rename":
            assert action_rename(source, target), f"Rename {source} fail!"
        elif action == "copy":
            assert action_copy(source, target), f"Copy {source} fail!"
        elif action == "delete":
            assert action_delete(source), f"Delete {source} fail!"
        else:   # TODO:其他action待补充
            assert False, f'Read ops fail: Unknown Action "{action}"'
    return True
