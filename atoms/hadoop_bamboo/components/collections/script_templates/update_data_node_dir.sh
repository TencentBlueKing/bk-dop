#!/usr/bin/env bash
# version: 1.0
# modify:
# function:
# 利用蓝鲸JOD平台去执行根据更新配置
# 执行状态码不同错代表不同情况：
# 0: 执行完成
# 150: 新增目录有残留数据存在
# 160: 不存在目录

hadoop_user=$1
hadoop_env=$2
new_dir_str=$3
config_file="${hadoop_env}/hadoop/etc/hadoop/hdfs-site.xml"

re_config() {
    sed -i "/>dfs.datanode.data.dir</{n;s#.*#        <value>${new_dir_str}</value>#}" ${config_file}
    datanode_rpc_port=$(hdfs getconf -confKey dfs.datanode.ipc.address | awk -F ':' '{print $2}')
    process_num=$(su - ${hadoop_user} -c "${hadoop_env}/java/bin/jps | grep -c -i datanode ")
    if [[ process_num -eq 1 ]]; then
        su - ${hadoop_user} -c "hdfs dfsadmin -reconfig datanode localhost:${datanode_rpc_port} start "
    fi

}

main() {
    re_config
}

main
echo "success"
exit 0