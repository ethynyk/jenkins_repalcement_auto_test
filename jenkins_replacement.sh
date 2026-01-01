#!/bin/bash
set -e  # 出现任何错误立即退出

# ============================ 配置区域 ============================
# 基础配置（这些可以改为从环境变量或命令行参数获取）
BUILD_NUMBER=${BUILD_NUMBER:-$(date +%Y%m%d%H%M%S)}
TEST_TASK=${TEST_TASK:-"default"}
TEST_BRANCH=${TEST_BRANCH:-"daily_build"}
AUTO_TEST_BRANCH=${AUTO_TEST_BRANCH:-"LTPU-dev"}
COMMON_TEST_NODE=${COMMON_TEST_NODE:-"dailytest-cv186ah-evb-01"}
IS_CLEAN_HOST_WS=${IS_CLEAN_HOST_WS:-"false"}
IS_CHECK_DAILY=${IS_CHECK_DAILY:-"false"}
IS_OTA=${IS_OTA:-"false"}
CUSTOM_UPGRADE_PATH=${CUSTOM_UPGRADE_PATH:-""}

# 环境变量（需要根据实际情况设置）
BOARD=${BOARD:-""}
SERIAL_PORT=${SERIAL_PORT:-""}
SD_DEV=${SD_DEV:-""}
SENSOR_NUM=${SENSOR_NUM:-"0"}
SENSOR_TYPE=${SENSOR_TYPE:-"null"}
SCREEN_TYPE=${SCREEN_TYPE:-"null"}
HOST_IP=${HOST_IP:-""}
HOST_WORKSPACE=${HOST_WORKSPACE:-"/media/cvitek/ke.yi/nfs_server"}
NFS_WS_PATH=${NFS_WS_PATH:-"/media/cvitek/ke.yi/nfs_server"}
NFS_RESOURCE_PATH=${NFS_RESOURCE_PATH:-"/nfs/a2_device_res/"}

# 计算路径
WORKSPACE=$(pwd)
UPGRADE_SRC="${WORKSPACE}/auto_test/test_upgrade/upgrade.zip"
HOST_WS="${HOST_WORKSPACE}/${BUILD_NUMBER}"
NFS_PATH="${HOST_IP}:${NFS_WS_PATH}/${BUILD_NUMBER}"
NFS_RES_PATH="${HOST_IP}:${NFS_RESOURCE_PATH}"

# ============================ 函数定义 ============================
# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# 错误处理函数
error_exit() {
    log "ERROR: $1"
    exit 1
}

# 升级开发板函数
upgrade_board() {
    local is_daily=$1
    local is_reboot=$2
    local is_ota=$3
    
    log "开始升级开发板: daily=$is_daily, reboot=$is_reboot, ota=$is_ota"
    
    if [ "$is_ota" = "true" ]; then
        python3 ./upgrade.py \
            --serial_port="$SERIAL_PORT" \
            --board="$BOARD" \
            --sd_dev="$SD_DEV" \
            --test_path="/mnt/nfs" \
            --host_ws="$HOST_WS" \
            --nfs_path="$NFS_PATH" \
            --ota_src="$UPGRADE_SRC" \
            $([ "$is_daily" = "true" ] && echo "--daily") \
            $([ "$is_reboot" = "true" ] && echo "--reboot")
    else
        python3 ./upgrade.py \
            --serial_port="$SERIAL_PORT" \
            --board="$BOARD" \
            --sd_dev="$SD_DEV" \
            --test_path="/mnt/nfs" \
            --host_ws="$HOST_WS" \
            --nfs_path="$NFS_PATH" \
            --sd_src="$UPGRADE_SRC" \
            $([ "$is_daily" = "true" ] && echo "--daily") \
            $([ "$is_reboot" = "true" ] && echo "--reboot")
    fi
}

# 运行pytest测试函数
run_pytest() {
    local workspace=$1
    local marker=$2
    local report_entry=$3
    local html_name=$(echo "$marker" | sed 's/ and /-/g')
    
    log "运行pytest测试: workspace=$workspace, marker=$marker"
    
    cd "$workspace" || error_exit "无法进入目录: $workspace"
    
    # 安装依赖
    python3 -m pip install -q -r ../requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    
    # 运行测试
    python3 -m pytest \
        -m "$marker" \
        --html="reports/${html_name}.html" \
        --junit-xml="reports/${html_name}.xml" \
        --serial_port="$SERIAL_PORT" \
        --board="$BOARD" \
        --test_path="/mnt/nfs" \
        --host_ws="$HOST_WS" \
        --nfs_path="$NFS_PATH" \
        --daily \
        --reboot \
        $([ "$IS_CLEAN_HOST_WS" = "true" ] && echo "--clean") \
        --branch="$TEST_BRANCH" \
        --sdk_version="latest_release" \
        --model_ver="<newest>" \
        --cvipqtool_ver="<newest>"
    
    # 处理测试报告
    if [ -f "reports/${html_name}.html" ]; then
        python3 ../scripts/report_process.py "reports/${html_name}.html" "${html_name}.html.tmp"
        if [ $? -eq 0 ]; then
            mv -f "${html_name}.html.tmp" "reports/${html_name}.html"
        fi
    fi
    
    cd - > /dev/null
}

# 检查任务是否应该执行
should_run_task() {
    local task_type=$1
    case "$TEST_TASK" in
        "default"|"all"|*"$task_type"*) return 0 ;;
        *) return 1 ;;
    esac
}

# ============================ 主要执行逻辑 ============================
main() {
    log "开始执行构建任务 #${BUILD_NUMBER}"
    
    # Stage 1: 任务初始化
    log "=== Stage 1: 任务初始化 ==="
    log "构建编号: $BUILD_NUMBER"
    log "测试任务: $TEST_TASK"
    log "测试分支: $TEST_BRANCH"
    log "串口端口: $SERIAL_PORT"
    
    # 打印所有环境变量和参数
    log "环境变量:"
    env | sort
    log "构建参数:"
    echo "TEST_TASK=$TEST_TASK"
    echo "TEST_BRANCH=$TEST_BRANCH"
    echo "AUTO_TEST_BRANCH=$AUTO_TEST_BRANCH"
    echo "IS_CLEAN_HOST_WS=$IS_CLEAN_HOST_WS"
    echo "IS_CHECK_DAILY=$IS_CHECK_DAILY"
    echo "IS_OTA=$IS_OTA"
    echo "CUSTOM_UPGRADE_PATH=$CUSTOM_UPGRADE_PATH"
    
    # Stage 2: 清理工作空间和检出代码
    # Stage 2: 清理工作空间和检出代码
    log "=== Stage 2: 检出代码 ==="

    # 检查auto_test目录是否存在
    if [ -d "auto_test" ]; then
        log "auto_test目录已存在，跳过代码检出"
        cd auto_test
        # 可选：更新已有代码到指定分支
        cd "$WORKSPACE"
    else
        log "auto_test目录不存在，开始检出代码"
         # 这里需要根据您的代码仓库配置git clone命令
         git clone -b "$AUTO_TEST_BRANCH" ssh://ke.yi@gerrit-ai.sophgo.vip:29418/auto_test \
        || error_exit "代码检出失败"
    fi
    
    # Stage 3: 升级开发板
    if should_run_task "multimedia" || should_run_task "auto_test"; then
        log "=== Stage 3: 升级开发板 ==="
        cd auto_test/test_upgrade || error_exit "无法进入升级目录"
        
        # 下载升级文件
        if [ -n "$CUSTOM_UPGRADE_PATH" ]; then
            ftp_url="${CUSTOM_UPGRADE_PATH}/upgrade.zip"
        else
            default_path="/athena2/sophon-img-device-auto/${TEST_BRANCH}/latest_release/images/soc_${BOARD}/upgrade.zip"
            ftp_url="ftp://AI:SophgoRelease2022@172.28.141.89${default_path}"
        fi
        
        log "下载升级文件: $ftp_url"
        wget "$ftp_url" -O "$UPGRADE_SRC" || error_exit "下载升级文件失败"
        
        # 执行升级
        upgrade_board "$IS_CHECK_DAILY" "false" "$IS_OTA"
        
        cd "$WORKSPACE"
    fi
    
    # Stage 4: 执行测试任务
    log "=== Stage 4: 执行测试任务 ==="
    
    # Multimedia - auto_test
    if should_run_task "auto_test"; then
        log "执行 Multimedia auto_test 测试"
        timeout 2h bash -c "
            run_pytest \"auto_test/cv186x\" \"auto_test\" \"Multimedia\"
        " || log "Multimedia auto_test 测试超时或有错误"
    fi
    
    # Multimedia - audio_ut
    if should_run_task "audio_ut"; then
        log "执行 Multimedia audio_ut 测试"
        timeout 1h bash -c "
            run_pytest \"auto_test/cv186x\" \"audio_ut\" \"Multimedia\"
        " || log "Multimedia audio_ut 测试超时或有错误"
    fi
    
    # Multimedia - vc_ut
    if should_run_task "vc_ut"; then
        log "执行 Multimedia vc_ut 测试"
        timeout 4h bash -c "
            run_pytest \"auto_test/cv186x\" \"vc_ut\" \"Multimedia\"
        " || log "Multimedia vc_ut 测试超时或有错误"
    fi
    
    # ISP 测试
    if should_run_task "isp"; then
        log "执行 ISP 测试"
        timeout 1h bash -c "
            run_pytest \"auto_test/cv186x\" \"isp\" \"ISP\"
        " || log "ISP 测试超时或有错误"
    fi
    
    # TDL_SDK 测试
    if should_run_task "tdl_sdk"; then
        log "执行 TDL_SDK 测试"
        timeout 1h bash -c "
            run_pytest \"auto_test/cv186x\" \"tdl_sdk\" \"TDL_SDK\"
        " || log "TDL_SDK 测试超时或有错误"
    fi
    
    log "所有任务执行完成"
}

# ============================ 执行主函数 ============================
main "$@"
