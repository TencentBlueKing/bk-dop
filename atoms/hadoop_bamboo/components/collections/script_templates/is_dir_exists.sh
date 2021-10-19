#!/usr/bin/env bash
# version: 1.0
# modify:
# function:
# 利用蓝鲸JOD平台去检测添加后的数据目录是否符合规范
# 执行状态码不同错代表不同情况：
# 0: 执行完成
# 150: 目录存在残留数据
# 160: 不存在目录

add_dir_str=$1
hadoop_user=$2
IFS="," read -r -a add_dir_arr <<<"$add_dir_str"

check_datadir_and_update() {

    #先检测新加的目录是否异常，检测通过才能添加到配置中
    #判断指定的数据盘是否有存在残留数据，如果有，则按照clean_data_force变量的
    for hadoop_data in "${add_dir_arr[@]}"; do
        # shellcheck disable=SC2086
        # shellcheck disable=SC2012

        if [[ ! -d ${hadoop_data} ]];then
                echo "${hadoop_data} not exist"
                exit 160

        fi
        chown -R ${hadoop_user}:${hadoop_user} "${hadoop_data}"
    done
}

main() {
    check_datadir_and_update
}

main
echo "success"
exit 0