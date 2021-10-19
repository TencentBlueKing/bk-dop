#!/usr/bin/env bash
# version: 1.0
# modify:
# function:
# 利用蓝鲸JOD平台去执行根据更新配置
# 执行状态码不同错代表不同情况：
# 0: 执行完成
# 150: 新增目录有残留数据存在
# 160: 不存在目录

includes_file=$1
excludes_file=$2
remove_includes_str=$3

remove_hostname_config() {
    # 移除hdfs的includes文件，删除白名单
    # 并增加到hdfs的exclude，删除黑名单

    IFS="," read -r -a remove_includes_arr <<<"$remove_includes_str"
    for remove_include in "${remove_includes_arr[@]}"; do
        if [[ $(grep -c "${remove_include}" ${includes_file}) -ge 1 ]]; then
            sed -i "/${remove_include}/d" ${includes_file}
        else
            echo "${remove_include} not exist in ${includes_file}"
        fi
        
        if [[ $(grep -c "${remove_include}" ${excludes_file}) -eq 0 ]]; then
            echo "${remove_include}" >> ${excludes_file}
        else
            echo "${remove_include} exist in ${excludes_file}"
        fi

    done


}


main(){
    remove_hostname_config
}

main
echo "success"
exit 0
