export BOARD="device_wevb_emmc"
export SERIAL_PORT="/dev/ttyUSB0"
export SD_DEV="your_sd_device"
export HOST_IP="10.80.40.30"
export TEST_TASK="default"  # 或其他任务类型



TEST_TASK="all" IS_OTA="true" ./jenkins_replacement.sh


