#!/usr/bin/env bash

# version: 1.0
# modify:
# function:
# 利用蓝鲸JOD平台去快速执行初始化脚本,机器之间建立用户免认证登录。
# 执行状态码不同错代表不同情况：
# 0  ：脚本执行成功



hadoop_user=$1
ssh_port=$2
target_hostname_str=$3

check_ssh_no_pass() {

    IFS="," read -r -a target_hostname_arr <<<"$target_hostname_str"
    for target_hostname in "${target_hostname_arr[@]}"; do
        local check_result
        check_result=$(su - ${hadoop_user} -c "ssh -p ${ssh_port} -o StrictHostKeyChecking=no -o CheckHostIP=no ${hadoop_user}@${target_hostname} -o ConnectTimeout=3 'echo 1'" 2>/dev/null)
        if [[ "$check_result" != "1" ]]; then
            echo "check ssh on pass fail"
            exit 129

        fi
    done

}

main() {
    check_ssh_no_pass
}
main
echo "success"
exit 0
