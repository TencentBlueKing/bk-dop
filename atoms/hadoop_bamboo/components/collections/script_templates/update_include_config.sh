#!/usr/bin/env bash
# version: 1.0
# modify:
# function:
# 利用蓝鲸JOD平台去执行所有的集群节点更新include配置，并在集群节点更新hosts
# 执行状态码不同错代表不同情况：
# 0: 执行完成

includes_file=$1
excludes_file=$2
add_includes_str=$3
hadoop_hosts_str=$4
IFS="," read -r -a add_includes_arr <<<"$hadoop_hosts_str"

update_excludes_file() {
    # 更新hdfs的exclude文件，为新加的节点在黑名单移除出去
    IFS="," read -r -a add_includes_arr <<<"$add_includes_str"
    for add_include in "${add_includes_arr[@]}"; do
        if [[ $(grep -c "${add_include}" ${excludes_file}) -ge 1 ]]; then
            sed -i "/${add_include}/d" ${excludes_file}
        fi
    done

}

update_includes_file() {
    # 更新hdfs的include文件，为新加的节点进入白名单
    IFS="," read -r -a add_includes_arr <<<"$add_includes_str"
    for add_include in "${add_includes_arr[@]}"; do
        if [[ $(grep -c "${add_include}" ${includes_file}) -eq 0 ]]; then
            echo "${add_include}" >>${includes_file}
        else
            echo "${add_include} exist in ${includes_file}"
        fi
    done

}

update_hosts() {
    #(xxx:xxx aaa:aaa .....)数组循环
    for host_info in "${hadoop_hosts_list[@]}"; do
        local ip
        local host_name
        ip=$(echo "${host_info}" | awk -F ':' '{print $1}')
        host_name=$(echo "${host_info}" | awk -F ':' '{print $2}')
        if [[ $(grep -c "${host_name}" /etc/hosts) -eq 0 ]]; then
            echo "${ip} ${host_name}" >>/etc/hosts
        else
            echo "${host_name} exist in /etc/hosts"
        fi
    done
}

main() {
    update_excludes_file
    update_includes_file
    update_hosts

}
main
echo "success"
exit 0
