#!/usr/bin/env bash
# version: 1.0
# modify:
# function:
# 利用蓝鲸JOD平台去执行所有的集群节点根据情况更新hosts配置
# 执行状态码不同错代表不同情况：
# 0: 执行完成

# 更新模式参数：add/remove 添加或者删除
ops_type=$1

hadoop_hosts_str=$2
IFS="," read -r -a hadoop_hosts_list <<<"$hadoop_hosts_str"

update_hosts() {
    #(xxx:xxx aaa:aaa .....)数组循环
    for host_info in "${hadoop_hosts_list[@]}"; do
        local ip
        local host_name
        ip=$(echo "${host_info}" | awk -F ':' '{print $1}')
        host_name=$(echo "${host_info}" | awk -F ':' '{print $2}')

        if [[ "${ops_type}" == "add" ]]; then
            if [[ $(grep -c "${ip} ${host_name}" /etc/hosts) -eq 0 ]]; then
               echo "${ip} ${host_name}" >>/etc/hosts
            fi

        elif [[ "${ops_type}" == "remove" ]]; then
            if [[ $(grep -c "${host_name}" /etc/hosts) -ne 0 ]]; then
                sed -i "/${host_name}/d" /etc/hosts
            else
                echo "${host_name} not exist in /etc/hosts"
            fi
            
        else
            echo "not support ops_type : ${ops_type}"
        fi
    done
}

main() {
    update_hosts
}
main
echo "success"
exit 0
