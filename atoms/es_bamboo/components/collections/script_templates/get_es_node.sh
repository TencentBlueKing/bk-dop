#!/usr/bin/env bash
# version: 1.0
# modify:
# function:
# 通过curl 方式获取es集群节点信息，并以json格式返回
# 执行状态码不同错代表不同情况：
# 0  ：脚本执行成功
# 127 ：认证失败
# 128 ：执行命令失败

es_http=$1
es_user=$2
es_pass=$3

get_node_by_curl() {
    if [[ -z ${es_user} || -z ${es_pass} ]];then
        es_node_json=$(curl http://${es_http}/_cat/nodes?format=json 2>/tmp/curl.log)
    else
        es_node_json=$(curl --user "${es_user}":"${es_pass}" http://${es_http}/_cat/nodes?format=json 2>/tmp/curl.log)
    fi
    
    if [[ -z ${es_node_json} ]];then
        # 若没有获取到json数据，默认为获取异常，获取异常日志打印，并code设置为128
       cat /tmp/curl.log
       exit 128
    elif [[ ${es_node_json} == "Unauthorized" ]]; then
       echo "${es_node_json}"
       exit 127

    else 
       echo "${es_node_json}"
    fi

} 
main(){
  get_node_by_curl
}

main
exit 0

