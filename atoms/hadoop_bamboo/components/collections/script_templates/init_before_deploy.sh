#!/usr/bin/env bash
# version: 1.0
# modify:
# function:
# 利用蓝鲸JOD平台去快速执行初始化脚本。
# 执行状态码不同错代表不同情况：
# 120：hadoop用户不存在
# 128：必要要安装包没有下载好
# 130：数据目录或者运行目录不存在或者授权不正确
# 140：本机新分配的hostname不存在，检查传入的hostinfo配置
# 150：数据目录存在残留数据
# 250：未知错误
# 0  ：脚本执行成功

#hadoop集群启动用户
hadoop_user=$1

#hadoop安装包的运行目录
hadoop_env=$2

#本地的hadoop压缩包
hadoop_file=$3

#本地的java压缩包
java_file=$4

#本部的zookeeper压缩包
zookeeper_file=$5

#hadoop集群存储数据盘，每个节点应统一命名，可以支持多目录配置，平台替换代入
#例如: hadoop_data_list=('/data/001' '/data/002')
# shellcheck disable=SC1083
hadoop_data_str=$6
IFS="," read -r -a hadoop_data_list <<<"$hadoop_data_str"

#hosts文件新增的域名，平台代替代入
#例如:hadoop_hosts_list=('1.1.1.1:test.hadoop001' '2.2.2.2:test.hadoop002')
hadoop_hosts_str=$7
IFS="," read -r -a hadoop_hosts_list <<<"$hadoop_hosts_str"

clean_config() {

    #清理相关/etc/profile 的关于hadoop的配置
    #检测数据盘是否有数据产生。
    sed -i '/hadoopprofile/d' /etc/profile
    sed -i '/ulimit/d' /etc/profile

}

add_hadoop_user_group() {

    #如果之前机器存在启动用户，则先删除
    if [[ $(id -u ${hadoop_user} 2>/dev/null) ]]; then
        userdel -r ${hadoop_user}
    fi

    #创建启动用户
    groupadd ${hadoop_user}
    useradd ${hadoop_user} -g ${hadoop_user}

}

create_base_dir_and_data_dir() {
    #创建对应的数据目录和运行目录

    if [[ ! -d ${hadoop_env} ]]; then
        mkdir -p ${hadoop_env}
    fi

    chown -R ${hadoop_user}:${hadoop_user} ${hadoop_env}

    for hadoop_data in "${hadoop_data_list[@]}"; do
        if [[ ! -d ${hadoop_data} ]]; then
            mkdir -p "${hadoop_data}"
        fi
        chown -R ${hadoop_user}:${hadoop_user} "${hadoop_data}"

    done

}

add_hosts() {

    #清理之前的相关hadoop 残留的域名解析记录
    sed -i '/hadoop/d' /etc/hosts

    #(xxx:xxx aaa:aaa .....)数组循环
    for host_info in "${hadoop_hosts_list[@]}"; do
        local ip
        local host_name
        ip=$(echo "${host_info}" | awk -F ':' '{print $1}')
        host_name=$(echo "${host_info}" | awk -F ':' '{print $2}')
        echo "${ip} ${host_name}" >>/etc/hosts

    done
}

modify_hosts_name() {

    # 获取目前机器的hostname信息
    local old_host_name
    local check_ip
    local host_name
    old_host_name=$(hostname)
    # 找出新分配的hostname信息，和ip信息匹配
    for host_info in "${hadoop_hosts_list[@]}"; do
        check_ip=$(echo "${host_info}" | awk -F ':' '{print $1}')
        if [[ $(ifconfig | grep -c "${check_ip}") -ge 1 ]]; then
            host_name=$(echo "${host_info}" | awk -F ':' '{print $2}')
            break
        fi
    done
    if [[ ! ${host_name} ]]; then

        echo "hostname does not exist,check!"
        exit 140

    fi
    # 删除旧hostname的配置
    set -i "/${old_host_name}/d" /etc/hosts

    #修改hostname
    hostname "${host_name}"
    sed -i '/HOSTNAME/d' /etc/sysconfig/network
    echo "HOSTNAME=${host_name}" >>/etc/sysconfig/network
    if [[ -f "/etc/hostname" ]]; then
        echo "${host_name}" >/etc/hostname
    fi

    #复制rsa文件，方便传输
    cp /home/"${hadoop_user}"/.ssh/id_rsa.pub  /home/"${hadoop_user}"/.ssh/id_rsa.pub."${check_ip}"
}

add_rsa_key() {

    # 本地生成公钥
    local hadoop_ssh_id_rsa="/home/${hadoop_user}/.ssh/id_rsa"
    if [[ ! -f ${hadoop_ssh_id_rsa} ]]; then
        su - ${hadoop_user} -c "ssh-keygen -f ${hadoop_ssh_id_rsa} -t rsa -N ''" >/dev/null 2>&1
    fi

}

add_special_user() {

    local tjj_sshd_file="/etc/sshd_special_user"
    if [ -f ${tjj_sshd_file} ]; then
        exist_flag=$(grep -c ${hadoop_user} ${tjj_sshd_file})
        if [[ "${exist_flag}" -lt 1 ]]; then
            echo "${hadoop_user}" >>${tjj_sshd_file}
        fi
    fi
}

unzip_package() {

    #解压对应的安装包到指定目录

    if [[ ! -f ${java_file} || ! -f ${hadoop_file} || ! -f ${zookeeper_file} ]]; then
        echo "The file does not exist ! java:${java_file} hadoop:${hadoop_file} zookeeper:${zookeeper_file}"
        exit 128
    fi

    rm -rf "${hadoop_env:?}/"*
    # 情况内部已存在文件
    # jdk解压
    mkdir -p ${hadoop_env}/java
    tar -xzvf ${java_file} -C ${hadoop_env}/java --strip-components 1 >/dev/null 2>&1
    

    # hadoop解压
    mkdir -p ${hadoop_env}/hadoop
    tar -xzvf ${hadoop_file} -C ${hadoop_env}/hadoop --strip-components 1 >/dev/null 2>&1


    # zookeeper解压
    mkdir -p ${hadoop_env}/zookeeper
    tar -xzvf ${zookeeper_file} -C ${hadoop_env}/zookeeper --strip-components 1 >/dev/null 2>&1
    

    # 创建软链
    if [ -f "/usr/bin/java" ]; then
        rm -f /usr/bin/java
    fi
    if [ -f "/usr/bin/hadoop" ]; then
        rm -f /usr/bin/hadoop
    fi
    cd /usr/bin/ || exit 250
    ln -s ${hadoop_env}/java/bin/java /usr/bin/java
    ln -s ${hadoop_env}/hadoop/bin/hadoop /usr/bin/hadoop

    # 添加环境变量到/etc/profile
    cat >${hadoop_env}/hadoopprofile <<EOF
    export JAVA_HOME=${hadoop_env}/java
    export HADOOP_HOME=${hadoop_env}/hadoop
    export ZOOKEEPER_HOME=${hadoop_env}/zookeeper
    export PATH=${hadoop_env}/hadoop/bin/:${hadoop_env}/hadoop/sbin/:${hadoop_env}/java/bin/:${hadoop_env}/zookeeper/bin/:$PATH 
EOF
    exist_flag=$(grep -c hadoopprofile /etc/profile)

    if [ "$exist_flag" -lt 1 ]; then
        echo "source ${hadoop_env}/hadoopprofile" >>/etc/profile
    fi

    #修改ulimit参数
    echo -e "ulimit -SHn 65535 \nulimit  -l unlimited\nulimit  -c unlimited" >>/etc/profile

    # shellcheck disable=SC1091
    source /etc/profile

    # 修改文件夹所属用户和用户组
    chown -R ${hadoop_user}:${hadoop_user} "${hadoop_env}"
}

check_result() {

    # 检测上述操作是否，如果存在操作尚未执行成功，返回对应的状态码和输出结果

    if [[ ! $(id -u "${hadoop_user}" 2>/dev/null) ]]; then
        echo "The hadoop user does not exist,check！"
        exit 120
    fi
    # shellcheck disable=SC2012
    if [[ ! -d ${hadoop_env}/java || $(ls -dl "${hadoop_env}" | awk '{print $3}') != "${hadoop_user}" ]]; then
        echo "The ${hadoop_env}/java directory was not handled properly,check!"
        exit 130
    fi
    # shellcheck disable=SC2012
    if [[ ! -d ${hadoop_env}/hadoop || $(ls -dl "${hadoop_env}/hadoop" | awk '{print $3}') != "${hadoop_user}" ]]; then
        echo "The ${hadoop_env}/hadoop javadirectory was not handled properly,check!"
        exit 130
    fi
    # shellcheck disable=SC2012
    if [[ ! -d ${hadoop_env}/zookeeper || $(ls -dl "${hadoop_env}/zookeeper" | awk '{print $3}') != "${hadoop_user}" ]]; then
        echo "The ${hadoop_env}/zookeeper directory was not handled properly,check!"
        exit 130
    fi

    for hadoop_data in "${hadoop_data_list[@]}"; do
        # shellcheck disable=SC2012
        if [[ ! -d ${hadoop_data} || $(ls -dl "${hadoop_data}" | awk '{print $3}') != "${hadoop_user}" ]]; then
            echo "The hadoop_data directory was not handled properly,check!"
            exit 130
        fi

    done

}

main() {
    clean_config
    add_hadoop_user_group
    create_base_dir_and_data_dir
    #add_hosts
    add_rsa_key
    modify_hosts_name
    add_special_user
    unzip_package
    check_result

}

main
echo "success"
exit 0
