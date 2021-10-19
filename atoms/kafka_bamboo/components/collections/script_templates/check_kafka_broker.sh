#!/usr/bin/env bash
# version: 1.0
# modify:
# function: 利用jps检测对应机器是否部署在对应的broker进程节点
# 执行状态码不同错代表不同情况：
# 0: 执行完成
# 128：节点检测失败

check_broker_process() {
    # 检测操作后是否成功
    local process_num
    process_num=$(jps | grep -c -i 'Kafka')
    if [[ process_num -eq 1 ]]; then
        # 进程启动成功
        echo "check success"
    else
        echo "failed"
        exit 128
    fi

}

main() {
      check_broker_process
}

main
exit 0