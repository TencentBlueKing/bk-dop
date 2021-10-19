#!/usr/bin/env bash
# version: 1.0
# modify:
# function:
# 利用蓝鲸JOD平台去快速执行初始化脚本,在目标机器启动namenode server。
# 执行状态码不同错代表不同情况：
# 0  ：脚本执行成功
# 128：启动namenode节点失败
# 129：启动zkfc节点失败

hadoop_user=$1
hadoop_env=$2
node_role=$3
#nn ip信息
nn1_addr=""
nn2_addr=""
if [[ "${node_role}" == "namenode" ]];then
   nn1_addr=$4
else
   nn2_addr=$4
fi

stop_namenode_and_zkfc_server(){
   #每次初始化都去尝试关闭namenode节点和zkfc节点，避免冲突
   su ${hadoop_user} -c "hadoop-daemon.sh stop namenode"  > /dev/null 2>&1
   su ${hadoop_user} -c "hadoop-daemon.sh stop zkfc"  > /dev/null 2>&1

}

init_namenode_server(){
    # 初始化namenode 数据目录（先处理nn1节点，在处理nn2节点，不能并发）
    if [[ -n ${nn1_addr} ]];then

        su ${hadoop_user}  -c "hdfs namenode -format -force"  > /dev/null 2>&1
        su ${hadoop_user}  -c "hadoop-daemon.sh start namenode"  > /dev/null 2>&1
        sleep 1
        su ${hadoop_user}  -c "hdfs zkfc -formatZK -force"  > /dev/null 2>&1

    elif [[ -n ${nn2_addr} ]];then
        su ${hadoop_user}  -c "hdfs namenode -bootstrapStandby -force"  > /dev/null 2>&1
        su ${hadoop_user}  -c "hadoop-daemon.sh start namenode"  > /dev/null 2>&1
    
    fi
    
}
start_zkfc_node(){
    # 初始化zkfc并启动，在nn1和nn2都要执行
    su ${hadoop_user}  -c "hadoop-daemon.sh start zkfc"  > /dev/null 2>&1
}

check_process(){
    # 检测启动的进程是否正常
    if [[ -n ${nn1_addr} ]];then
        check_result=$(su - ${hadoop_user}  -c "hdfs haadmin -getServiceState nn1")
        # 避免重新初始化时候，被就namenode抢占，启动一段时间为standby状态，但初始化是正常的
        if [[ "${check_result}" != "active" && "${check_result}" != "standby" ]];then
            echo "fail"
            exit 128
        fi
    fi
    if [[ -n ${nn2_addr} ]];then
        check_result=$(su - ${hadoop_user}  -c "hdfs haadmin -getServiceState nn2")
        if [[ "${check_result}" != "standby"  ]];then
            echo "fail"
            exit 128
        fi
    fi
    check_sum=$(su - ${hadoop_user}  -c "jps | grep -c DFSZKFailoverController ")
    if [[ ${check_sum} -ne 1 ]];then 
        echo "fail"
        exit 129
    fi 
    

}

main(){
    stop_namenode_and_zkfc_server
    init_namenode_server
    start_zkfc_node
    sleep 1
    check_process
}
main
echo "success"
exit 0 


