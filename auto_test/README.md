## Version
Version:  v1.1
Last Updated:     2025/08/22

## 框架概述
本框架用于管理端侧设备的自动化测试（通过串口/SSH控制），支持动态参数配置、多模块测试用例管理和分层级配置覆盖。

这个文件展示测试项目的目录层级关系，通过描述配置文件的层级关系，说明维护和管理测试用例的方法。

与云边测试的主要区别：

- 端侧：依赖主机控制（无法直接部署开发环境）
- 云边：可直接在设备上执行测试（支持环境部署）


## 快速开始

### 执行测试

```plaintext
pytest -m [markers] [parameters]
# 示例： 测试多媒体模块的audio_ut并指定动态参数
pytest -m nor_flash --serial_port=COM3 --report_name=autio_ut --daily
```

## 目录结构

```plaintext
.
├── cv184x                              # 主测试模块
│   ├── __init__.py
│   ├── pytest.ini                      # 全局静态配置
│   ├── conftest.py                     # 动态参数加载 (基于CUSTOMER_OPTIONS)
│   ├── init_conf.py                    # 参数定义 (CUSTOMER_OPTIONS字典)
│   ├── multimedia                      # 子模块测试
│   │   ├── __init__.py
│   │   ├── auto_test
│   │   │   ├── __init__.py
│   │   │   ├── auto_test.yaml          # 模块配置
│   │   │   └── test_auto_test.py       # 测试脚本
│   │   └── ......
│   └── ......
├── scripts                             # 工具脚本
├── test_upgade                         # 固件自动升级
│   ├── upgrade.py
│   └── upgrade.yaml
└── utils                               # 公共工具库
    ├── __init__.py
    ├── cmd.py
    ├── common_func.py
    ├── download.py
    ├── host_utils.py
    ├── prepare.py
    ├── serial_utils.py
    └── ssh_utils.py
```

## 配置文件层级关系

|层级|配置文件|覆盖规则|示例|
|:---|:---|:---|:---|
|1. 命令行参数    |pytest [options]     |最高优先级     |--daily|
|2. 全局动态配置  |cv184x/init_conf.py  |定义默认参数   |CUSTOMER_OPTIONS["--board"].default="cv1842hp_wevb_0014a_spinor"|
|3. 全局静态配置  |cv184x/pytest.ini    |基础静态配置   |addopts = --html=reports/${report_name}.html|
|4. 模块YAML     |cv184x/modules/*.yaml |模块测试配置   |test_environment_configs.source:"${host_ws}/custom_path"|

### 配置原则：
- 子目录的配置覆盖父目录的配置
- 命令行的配置覆盖默认配置

## 核心配置文件说明
### cv184x/pytest.ini - 全局静态配置
本配置文件定义了例如测试报告路径、log格式等全局静态配置

```ini
pytest.ini
[pytest]
markers = 
    ......

addopts = 
    -s
    --html=reports/${report_name}.html
    --self-contained-html
    --junitxml=reports/${report_name}.xml

log......
```

### cv184x/init_conf.py
#### 全局通用动态配置

使用 CUSTOMER_OPTIONS 定义配置参数，包括全局通用动态配置 "Base Test Parameters" 和 "SDK Parameters":

```python
CUSTOMER_OPTIONS = {
    "Base Test Parameters": {
        "--serial_port": {
            "action": "store", "type": str, "default": None,
            "help": "Serial port connected to client (mutually exclusive with --ip)"
        },
        "--ip": { ... },
        ...  # 其他参数见完整文件
    },
    "SDK Parameters": {
        "--daily": { "action": "store_true", "default": False, "help": "Check board version" },
        "--sdk_version": { ... },
        ...
    }
}
```

#### 模块测试动态配置

使用 CUSTOMER_OPTIONS 定义配置参数，包括模块测试动态配置 "Module Test Parameters":

```python
CUSTOMER_OPTIONS = {
    # 空参数组（预留扩展）
    "BSP Test Parameters": {},
    "Multimedia Parameters": { ... },
    "ISP Test Parameters": { ... },
    "TDL_SDK Parameters": { ... },
    "APP Parameters": { ... }
}
```

### cv184x/conftest.py - 参数加载逻辑

利用pytest的hook函数 pytest_addoption(parser) 加载所有动态配置参数, 并通过hook函数 pytest_configure(config) 展示测试指定的配置参数值：

```python
from init_conf import CUSTOMER_OPTIONS

def pytest_addoption(parser):
    for group_name, options in CUSTOMER_OPTIONS.items():
            group = parser.getgroup(group_name)
            for opt, kwargs in options.items():
                group.addoption(opt, **kwargs)

def pytest_configure(config):
    """验证加载的参数"""
    print("\n=== Active Parameters ===")
    for group, opts in CUSTOMER_OPTIONS.items():
        print(f"\n[Group: {group}]")
        for opt in opts:
            print(f"{opt.ljust(20)}: {config.getoption(opt)}")
```


### cv184x/module/\*.yaml - 模块测试的配置文件

本文件使用固定字段和格式定义模块测试的环境准备和测试用例，固定字段目前支持'<newest>'参考格式如下：

```yaml
# test environment
test_environment_configs:
  - action: str, support download/extract/board_link/copy/move/rename/delete...
    desc: str
    source: str, support ${var} or <re.Pattern>
    target: "${host_ws}/"

# test case
test_cases:
  marker:
    - case: str, text command
      check_res: str
      runtime: int
```

## 模块测试用例添加
以case模块测试为例：
### 1. 创建python测试脚本

```python
# cv184x/case/test_case.py
import pytest

case_cmds_file = os.path.join(
    os.path.dirname(__file__),
    "case.yaml"
)

@pytest.mark.case
@pytest.mark.parametrize('prepare_ws', [{'env_file': case_cmds_file}], indirect=True)
@pytest.mark.parametrize(('cmd', 'check_res', 'runtime'), read_cases(case_cmds_file, "case"))
def test_case(cmd, check_res, runtime, setup_session, prepare_ws, request):
    print_function()
    device = setup_session
    log, ret_code, ret = run_cmd(client=device,
                                 cmd=cmd,
                                 timeout=runtime,
                                 ret_regex=check_res,
                                 echo=True)
    assert log, 'Device happens some errors, please check.'
    assert ret_code == 0, 'Test case execute timeout'
    assert ret, 'Test Fail!'
```

### 2. 添加YAML配置

```yaml
# cv184x/case/case.yaml
test_environment_configs:
  - action: "download"
    source: "ftp://example.com/${sdk_version}/toolkit.zip"
    target: "${host_ws}/tools/"

test_cases:
  marker:
    - case: "run_benchmark --mode=perf"
      check_res: "throughput > 100fps"
      runtime: 60
```

### 3. 整理模块测试的动态配置项，更新init_conf.py

```python
# cv184/init_conf.py
CUSTOMER_OPTIONS["CASE Parameters"] = {
    "--case1": {
        "action": "store", "type": str, "default": None,
        "help": "${case} in ./*.yaml"
    }
}
```

### 4. 在pytest.ini文件中注册标记marker

```ini
# cv184x/pytest.ini
markers =
    case

```

## 附录：
1. pytest_addoption(parser)中参数定义参考：<https://blog.csdn.net/waitan2018/article/details/104320927>
2. pytest的conftest.py中的钩子函数参考pytest官方文档：<https://pytest.cn/en/8.2.x/how-to/writing_hook_functions.html#>
3. pytest的markers的定义和使用参考官方文档：<https://docs.pytest.org/en/8.2.x/reference/reference.html#custom-marks>
