#!/usr/bin/env bash
# version: 1.0
# modify:
# function:
# 利用蓝鲸JOD平台去快速执行生成hadoop集群需要的配置文件。
# 执行状态码不同错代表不同情况：
# 0  ：脚本执行成功
# 128  ：参数不支持

hadoop_user=$1
hadoop_env=$2
hdfs_includes=$3
hdfs_excludes=$4
zk_list_str=$5
journal_list_str=$6
ns1_addr=$7
ns2_addr=$8
datanode_list_str=$9
data_dir_str=${10}
replication_num=${11}
push_type=${12}
resourcemanager_list_str=${13}
nodemanager_list_str=${14}

journal_data_dir=$(echo ${data_dir_str} | awk -F ',' '{print $1}')
tmp_data_dir=$(echo ${data_dir_str} | awk -F ',' '{print $1}')


# 1 hadoop-env.sh
#sed -i "s/\${JAVA_HOME}/\${hadoop_env}\/java/g" ${hadoop_env}/hadoop/etc/hadoop/hadoop-env.sh
# 适配不同版本
#echo "export JAVA_HOME=${hadoop_env}/java" >>${hadoop_env}/hadoop/etc/hadoop/hadoop-env.sh

touch ${hdfs_includes}
touch ${hdfs_excludes}
IFS="," read -r -a zk_list_arr <<<"$zk_list_str"
zk1_addr=${zk_list_arr[0]}
zk2_addr=${zk_list_arr[1]}
zk3_addr=${zk_list_arr[2]}

create_file(){
  # create includes and excludes
  touch ${hdfs_includes}
  touch ${hdfs_excludes}
  if [[ ! -f ${hdfs_includes} || ! -f ${hdfs_includes} ]];then
    echo "白名单/黑名单文件创建失败，请检测配置是否正常"
    exit 130
  fi
}
push_hdfs_config() {
        # core-site.xml
        cat >${hadoop_env}/hadoop/etc/hadoop/core-site.xml <<EOF
<configuration>
        <!-- 指定hdfs的nameservice为ns1 -->
        <property>
                <name>fs.defaultFS</name>
                <value>hdfs://ns1</value>
        </property>

        <!-- 指定HDFS数据存放路径，默认存放在linux的/tmp目录中 -->
        <property>
                <name>hadoop.tmp.dir</name>
                <value>${tmp_data_dir}/tmp</value>
        </property>

        <!-- 指定zookeeper的地址 -->
        <property>
                <name>ha.zookeeper.quorum</name>
                <value>${zk1_addr}:2181,${zk2_addr}:2181,${zk3_addr}:2181</value>
        </property>
</configuration>
EOF

        # hdfs-site.xml
        IFS="," read -r -a journal_list_arr <<<"$journal_list_str"
        journal1_addr=${journal_list_arr[0]}
        journal2_addr=${journal_list_arr[1]}
        journal3_addr=${journal_list_arr[2]}

        cat >${hadoop_env}/hadoop/etc/hadoop/hdfs-site.xml <<EOF
<configuration>
        <!--指定hdfs的nameservice为ns1，需要和core-site.xml中的保持一致 -->
        <property>
                <name>dfs.nameservices</name>
                <value>ns1</value>
        </property>
        <!-- ns1下面有两个NameNode，分别是nn1，nn2 -->
        <property>
                <name>dfs.ha.namenodes.ns1</name>
                <value>nn1,nn2</value>
        </property>
        <!-- nn1的RPC通信地址 -->
        <property>
                <name>dfs.namenode.rpc-address.ns1.nn1</name>
                <value>${ns1_addr}:9000</value>
        </property>
        <!-- nn1的http通信地址 -->
        <property>
                <name>dfs.namenode.http-address.ns1.nn1</name>
                <value>${ns1_addr}:50070</value>
        </property>
        <!-- nn2的RPC通信地址 -->
        <property>
                <name>dfs.namenode.rpc-address.ns1.nn2</name>
                <value>${ns2_addr}:9000</value>
        </property>
        <!-- nn2的http通信地址 -->
        <property>
                <name>dfs.namenode.http-address.ns1.nn2</name>
                <value>${ns2_addr}:50070</value>
        </property>
        <!-- 指定NameNode的日志在JournalNode上的存放位置 -->
        <property>
                <name>dfs.namenode.shared.edits.dir</name>
                <value>qjournal://${journal1_addr}:8485;${journal2_addr}:8485;${journal3_addr}:8485;/ns1</value>
        </property>
        <!-- 指定JournalNode在本地磁盘存放数据的位置 -->
        <property>
                <name>dfs.journalnode.edits.dir</name>
                <value>${journal_data_dir}/journal</value>
        </property>
        <!-- 开启NameNode失败自动切换 -->
        <property>
                <name>dfs.ha.automatic-failover.enabled</name>
                <value>true</value>
        </property>
        <!-- 配置失败自动切换实现方式 -->
        <property>
                <name>dfs.client.failover.proxy.provider.ns1</name>
                <value>org.apache.hadoop.hdfs.server.namenode.ha.ConfiguredFailoverProxyProvider</value>
        </property>
        <!-- 配置隔离机制方法，多个机制用换行分割，即每个机制暂用一行-->
        <property>
                <name>dfs.ha.fencing.methods</name>
                <value>
                sshfence
                shell(/bin/true)
                </value>
        </property>

        <!-- 使用sshfence隔离机制时需要ssh免登陆 -->
        <property>
                <name>dfs.ha.fencing.ssh.private-key-files</name>
                <value>/home/${hadoop_user}/.ssh/id_rsa</value>
        </property>

        <!-- 配置sshfence隔离机制超时时间 -->
        <property>
                <name>dfs.ha.fencing.ssh.connect-timeout</name>
                <value>30000</value>
        </property>

        <!-- 配置退役节点 -->
        <property>
                <name>dfs.hosts.exclude</name>
                <value>${hdfs_excludes}</value>
        </property>
        <!-- 配置白名单节点 -->
        <property>
                <name>dfs.hosts.include</name>
                <value>${hdfs_includes}</value>
        </property>
        <!-- 配置副本数量 -->
        <property>
                <name>dfs.replication</name>
                <value>${replication_num}</value>
        </property>
        <!-- 数据存储位置，按照需求可配置多个目录配置 -->
        <property>
                <name>dfs.datanode.data.dir</name>
                <value>${data_dir_str}</value>
        </property>
        <!-- 平衡策略，推荐使用 -->
        <property>
                <name>dfs.datanode.fsdataset.volume.choosing.policy</name>
                <value>org.apache.hadoop.hdfs.server.datanode.fsdataset.AvailableSpaceVolumeChoosingPolicy</value>
        </property>
</configuration>
EOF

        # dfs.hosts.include
        IFS="," read -r -a datanode_list_arr <<<"$datanode_list_str"
        for datanode_host in "${datanode_list_arr[@]}"; do
                exist_flag=$(grep -c "${datanode_host}" ${hdfs_includes})
                if [[ ${exist_flag} -eq 0 ]];then
                    echo "${datanode_host}" >>${hdfs_includes}
                fi
        done
        chown ${hadoop_user}:${hadoop_user} ${hdfs_includes}
        chown ${hadoop_user}:${hadoop_user} ${hdfs_excludes}
}

push_yarn_config() {
        # yarn-site.xml
        IFS="," read -r -a resourcemanager_list_arr <<<"$resourcemanager_list_str"
        rm1_addr=${resourcemanager_list_arr[0]}
        rm2_addr=${resourcemanager_list_arr[1]}

        cat >${hadoop_env}/hadoop/etc/hadoop/yarn-site.xml <<EOF
<configuration>
        <!-- 开启RM高可靠 -->
        <property>
                <name>yarn.resourcemanager.ha.enabled</name>
                <value>true</value>
        </property>

        <!-- 指定RM的cluster id -->
        <property>
                <name>yarn.resourcemanager.cluster-id</name>
                <value>yrc</value>
        </property>

        <!-- 指定RM的名字 -->
        <property>
                <name>yarn.resourcemanager.ha.rm-ids</name>
                <value>rm1,rm2</value>
        </property>

        <!-- 分别指定RM的地址 -->
        <property>
                <name>yarn.resourcemanager.hostname.rm1</name>
                <value>${rm1_addr}</value>
        </property>
        <property>
                <name>yarn.resourcemanager.hostname.rm2</name>
                <value>${rm2_addr}</value>
        </property>

        <!-- 指定zk集群地址 -->
        <property>
                <name>yarn.resourcemanager.zk-address</name>
                <value>${zk1_addr}:2181,${zk2_addr}:2181,${zk3_addr}:2181</value>
        </property>

        <!-- 增加yarn webapp的端口配置，hadoop3.x以上一定要添加，要不然MapReduce时出现空指针的问题 -->
        <property>
                <name>yarn.resourcemanager.webapp.address.rm1</name>
                <value>${rm1_addr}:9088</value>
        </property>

        <property>
               <name>yarn.resourcemanager.webapp.address.rm2</name>
               <value>${rm2_addr}:9088</value>
        </property>
        <!--启用自动恢复-->
        <property>
              <name>yarn.resourcemanager.recovery.enabled</name>
              <value>true</value>
       </property>
       <!--指定 resourcemanager 的状态信息存储在 zookeeper 集群-->
       <property>
              <name>yarn.resourcemanager.store.class</name>
              <value>org.apache.hadoop.yarn.server.resourcemanager.recovery.ZKRMStateStore</value>
      </property>

       <!-- 开启日志聚合 -->
      <property>
           <name>yarn.log-aggregation-enable</name>
           <value>true</value>
      </property>
       <!-- 日志聚合HDFS目录 -->
       <property>
            <name>yarn.nodemanager.remote-app-log-dir</name>
            <value>/tmp/logs</value>
       </property>
       <!-- 日志保存时间3days,单位秒 -->
       <property>
           <name>yarn.log-aggregation.retain-seconds</name>
           <value>259200</value>
       </property>

        <property>
                <name>yarn.nodemanager.aux-services</name>
                <value>mapreduce_shuffle</value>
        </property>
</configuration>
EOF

        IFS="," read -r -a nodemanager_list_arr <<<"$nodemanager_list_str"
        for nodemanger_host in "${nodemanager_list_arr[@]}"; do
                exist_flag=$(grep -c "${nodemanger_host}" ${hdfs_includes})
                if [[ ${exist_flag} -eq 0 ]];then
                    echo "${nodemanger_host}" >>${hdfs_includes}
                fi
        done
        chown ${hadoop_user}:${hadoop_user} ${hdfs_includes}
        chown ${hadoop_user}:${hadoop_user} ${hdfs_excludes}
}

main() {
        create_file
        if [[ "${push_type}" == "hdfs_yarn" ]]; then
                push_hdfs_config
                push_yarn_config
        elif [[ "${push_type}" == "only_hdfs" ]]; then
                push_hdfs_config
        elif [[ "${push_type}" == "only_yarn" ]]; then
                push_yarn_config
        else
            echo "not support ${push_type}"
            exit 128
        fi
}
main
echo "success"
exit 0
