#!/usr/bin/env bash
# version: 1.0
# modify:
# function:
# 利用蓝鲸JOD平台去快速执行初始化脚本,在目标机器启动journal node。
# 执行状态码不同错代表不同情况：
# 0  ：脚本执行成功
# 130 ：启动节点失败

hadoop_env="{hadoop_env_tmp}"
hadoop_user="{hadoop_user_tmp}"

su ${hadoop_user} -c "${hadoop_env}/hadoop/sbin/hadoop-daemon.sh start journalnode"
sleep 1
# 启动检查
process_num=$(su - ${hadoop_user}  -c "jps | grep -c JournalNode")
if [[ $process_num -eq 1 ]]; then
  echo "JournalNode check success"
else
  echo "JournalNode check fail"
  exit 130
fi
