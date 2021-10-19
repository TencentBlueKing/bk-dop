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

# 节点类型 resourcemanager / nodemanager
node_name=$4

# 操作版本类型
cluster_version=$5

node_ops_v2() {
    # 3.0之前版本操作
    if [[ "${ops}" == "start" || "${ops}" == "stop" ]]; then
        su - ${hadoop_user} -c "${hadoop_env}/hadoop/sbin/yarn-daemon.sh ${ops} ${node_name}"
        exit 0
    else
        echo "not support ops:[${ops}]"
        exit 130
    fi
}

node_ops_v3() {
    # 3.0之后版本操作
    if [[ "${ops}" == "start" || "${ops}" == "stop" ]]; then
        su - ${hadoop_user}  -c "yarn --daemon ${ops} ${node_name}"
        exit 0
    else
        echo "not support ops:[${ops}]"
        exit 130
    fi
}

check_ops() {
    # 检测操作后是否成功
    local process_num
    process_num=$(su - ${hadoop_user}  -c "jps | grep -c -i '${node_name}' ")
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
    if [[ "${node_name}" == "resourcemanager" || "${node_name}" == "nodemanager" ]]; then
        if [[ "${cluster_version}" == "2.6.0" ]]; then
            node_ops_v2
        elif [[ "${cluster_version}" == "3.2.0" ]]; then
            node_ops_v3
        else
            echo "not support version cluster_version:[${cluster_version}]"
            130
        fi
    else
        echo "not support node_name:[${node_name}]"
        exit 130
    fi
    
    sleep 1    
    check_ops
}

main
exit 0
