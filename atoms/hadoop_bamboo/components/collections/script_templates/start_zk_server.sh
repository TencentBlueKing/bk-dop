#!/usr/bin/env bash
# version: 1.0
# modify:
# function:
# 利用蓝鲸JOD平台去快速执行生成hadoop集群需要的配置文件。
# 执行状态码不同错代表不同情况：
# 0  ：脚本执行成功
# 128：找不到对应的myid配置
# 130：启动失败

hadoop_env=$1
hadoop_user=$2
zk_hostname_list_str=$3
IFS="," read -r -a zk_hostname_list <<<"$zk_hostname_list_str"

zk_host1="${zk_hostname_list[0]}"
zk_host2="${zk_hostname_list[1]}"
zk_host3="${zk_hostname_list[2]}"

# 根据IP来生成的zookeeper的myid，保证唯一
myid_1_str="1"
myid_2_str="2"
myid_3_str="3"

cat >${hadoop_env}/zookeeper/conf/zoo.cfg <<EOF
tickTime=2000
initLimit=10
syncLimit=5
clientPort=2181
dataDir=${hadoop_env}/zookeeper/data
server.${myid_1_str}=${zk_host1}:2888:3888
server.${myid_2_str}=${zk_host2}:2888:3888
server.${myid_3_str}=${zk_host3}:2888:3888
EOF

# 创建zookeeper数据目录
if [[ ! -d "${hadoop_env}/zookeeper/data" ]]; then
  mkdir -p ${hadoop_env}/zookeeper/data
fi

# 配置myid
local_hostname=$(hostname)
if [[ "${local_hostname}" == "${zk_host1}" ]]; then
  echo "${myid_1_str}" >${hadoop_env}/zookeeper/data/myid
elif [[ "${local_hostname}" == "${zk_host2}" ]]; then
  echo "${myid_2_str}" >${hadoop_env}/zookeeper/data/myid
elif [[ "${local_hostname}" == "${zk_host3}" ]]; then
  echo "${myid_3_str}" >${hadoop_env}/zookeeper/data/myid
else
  echo "not exist myid"  
  exit 128
fi

# 更改权限
chown -R ${hadoop_user}:${hadoop_user} ${hadoop_env}/

sleep 2
cd ${hadoop_env}/zookeeper/bin/ || exit 128
su ${hadoop_user} -c "${hadoop_env}/zookeeper/bin/zkServer.sh start"

process_num=$(su - ${hadoop_user} -c "jps |grep -c QuorumPeerMain")
if [[ $process_num -eq 1 ]]; then
  echo "QuorumPeerMain check success"
  exit 0
else
  echo "QuorumPeerMain check fail"
  exit 130
fi
