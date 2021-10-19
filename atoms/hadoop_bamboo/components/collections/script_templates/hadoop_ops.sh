#!/usr/bin/env bash
# version: 1.0
# modify:
# function:
# 利用蓝鲸JOD平台去执行对节点管理
# 执行状态码不同错代表不同情况：
# 0  ：脚本执行成功
# 128：脚本执行失败
# 130：传入参数不支持

hadoop_env=$1
hadoop_user=$2

# 传入的操作指令 start/stop
ops=$3

# 节点类型 namenode/zkfc/journalnode/datanode
node_name=$4

node_ops() {
    if [[ "${ops}" == "start" || "${ops}" == "stop" ]]; then
        su - ${hadoop_user} -c "${hadoop_env}/hadoop/sbin/hadoop-daemon.sh ${ops} ${node_name}" > /dev/null 2>&1
        # 动态刷新datanode map
        if [[ "${node_name}" == "datanode" ]];then
           su - ${hadoop_user} -c 'hdfs dfsadmin -refreshNodes'
        fi
    else
        echo "not support ops:[${ops}]"
        exit 130
    fi
}

check_ops() {
    # 检测操作后是否成功
    if [[ ${node_name} == "zkfc" ]];then
        # 若检测zkfc，则重新赋值进程名称
        node_name="DFSZKFailoverController"
    fi

    local process_num
    process_num=$(su - ${hadoop_user} -c " jps | grep -c -i '${node_name}' ")
    if [[ "${ops}" == "start" && process_num -eq 1 ]]; then
        # 进程启动成功
        echo "success"
    elif [[ "${ops}" == "stop" && process_num -eq 0 ]]; then
        # 进程关闭成功
        echo "success"
    else
        echo "failed"
        exit 128
    fi

}


main() {
    if [[ "${node_name}" == "namenode" || "${node_name}" == "zkfc" || "${node_name}" == "journalnode" || "${node_name}" == "datanode" ]]; then
        node_ops
    else
        echo "not support ${node_name}"
        exit 128
    fi
    sleep 2
    check_ops
}

main
exit 0
