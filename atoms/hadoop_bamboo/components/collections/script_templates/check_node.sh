#!/usr/bin/env bash
# version: 1.0
# modify:
# function: 检测对应机器是否部署在对应的hdfs进程节点
# 执行状态码不同错代表不同情况：
# 0: 执行完成
# 128：节点检测失败

hadoop_user=$1

# 节点类型 namenode/journalnode/datanode/resourcemanager/nodemanager
node_name=$2

check_ops() {
    # 检测操作后是否成功
    if [[ ${node_name} == "standbynamenode" ]];then
        # 若检测zkfc，则重新赋值进程名称
        node_name="namenode"
    fi
    local process_num
    process_num=$(su - ${hadoop_user} -c " jps | grep -c -i '${node_name}' ")
    if [[ process_num -eq 1 ]]; then
        # 进程启动成功
        if [[ ${node_name} == "namenode" ]];then

            process_num=$(su - ${hadoop_user} -c " jps | grep -c -i 'DFSZKFailoverController' ")
            if [[ process_num -ne 1 ]]; then
                echo "failed"
                exit 128
            fi
        fi
    else
        echo "failed"
        exit 128
    fi

}


main() {
      check_ops
}

main
exit 0
