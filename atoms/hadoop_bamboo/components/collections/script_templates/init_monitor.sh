#!/bin/bash

###  hadoop部署监控脚本

time_format="date +'%Y-%m-%d %H:%M:%S'"
NOW="echo [\`$time_format\`][PID:$$]"


data_id=$1
access_token=$2
metric_port=$3
target_ip_list=$4
cluster_name=$5
isAddMonitor=1



##### 可在脚本执行成功的逻辑分支处调用，打印当时的时间戳及PID。
job_success()
{
    MSG="$*"
    echo "$(eval "${NOW}") job_success:[$MSG]"

}

##### 可在脚本执行失败的逻辑分支处调用，打印当时的时间戳及PID。
job_fail()
{
    MSG="$*"
    echo "$(eval "${NOW}") job_fail:[$MSG]"

}

### 检测是否有自定义上报工具bkmonitorbeat
check_bkmonitorbeat(){
  if not [[ -f '/usr/local/gse/plugins/bin/bkmonitorbeat' ]];then
     job_fail "不存在自定义上报工具bkmonitorbeat"
  fi
}

###执行安装依赖
python_setup_prometheus_client(){
   if [[ -f "/data/client_python.tar.gz" ]];then
      cd /data/ || exit 128
      rm -rf client_python/
      tar -zxvf  client_python.tar.gz

      cd /data/client_python || exit 128
      python setup.py install
   else
      job_fail "not module client_python.tar.gz, check"
      exit 128
   fi
   job_success "install module client_python success"

}

python_setup_pyyaml(){
   if [[ -f "/data/pyyaml.tar.gz" ]];then
      cd /data/ || exit 128
      rm -rf pyyaml/
      tar -zxvf  pyyaml.tar.gz

      cd /data/pyyaml || exit 128
      python setup.py install
   else
      job_fail "not module pyyaml.tar.gz, check"
      exit 128
   fi
   job_success "install module pyyaml success"
}

python_setup_requests(){
   if [[ -f "/data/requests.tar.gz" ]];then
      cd /data/ || exit 128
      rm -rf requests/
      tar -zxvf  requests.tar.gz

      cd /data/requests || exit 128
      python setup.py install
   else
      job_fail "not module requests.tar.gz, check"
      exit 128
   fi
   job_success "install module requests success"
}

# 解压hadoop exporter 工具
unzip_exporter_package(){
   if [[ -f "/data/hadoop_exporter.tar.gz" ]];then
      rm -rf /usr/local/hadoop_exporter
      cd /data/ || exit 128
      rm -rf hadoop_exporter/
      tar -zxvf  hadoop_exporter.tar.gz
   else
      job_fail "not exporter hadoop_exporter.tar.gz, check"
      exit 128
   fi
   job_success "unzip exporter success"
}

### 启动hadoop exporter
start_hadoop_exporter_process(){
    local nns
    local rms
    local cluster_startup_params
    host_name=$(hostname)
    ps aux | grep "[h]adoop_exporter.py" | awk '{print $2}' | xargs -i kill -9 {}
    if [[ -d '/data/hadoop_exporter' ]];then
       mv /data/hadoop_exporter  /usr/local/

       jps_list=$(su - hadoop -c "jps  | awk '{print \$2}' ")
       for process_name in $jps_list ;do

           if [[ "${process_name}" == "NameNode" ]];then
               # 添加namenode配置信息
               services_id=$(su - hadoop -c "hdfs getconf -confKey dfs.nameservices")
               nn_id_list=$(su - hadoop -c "hdfs getconf -confKey dfs.ha.namenodes.${services_id}")

               IFS="," read -r -a nn_id_arr <<<"$nn_id_list"
               for nn_id in "${nn_id_arr[@]}"; do
                   nn_http_url=$(su - hadoop -c "hdfs getconf -confKey dfs.namenode.http-address.${services_id}.${nn_id}")
                   if [[ ${nn_http_url} =~ ${host_name} ]];then
                      nns="http://${nn_http_url}/jmx"
                      break
                   fi
               done
               if [[ -n ${nns} ]];then
                  cluster_startup_params="${cluster_startup_params} -nns ${nns}"
               fi
               continue

           elif [[ "${process_name}" == "ResourceManager" ]];then
               # 添加resourcemanger配置信息
               rm1_addr=$(su - hadoop -c "hdfs getconf -confKey yarn.resourcemanager.webapp.address.rm1")
               rm2_addr=$(su - hadoop -c "hdfs getconf -confKey yarn.resourcemanager.webapp.address.rm2")

               if [[ ${rm1_addr} =~ ${host_name} ]];then
                  rms="http://${rm1_addr}"
               else
                  rms="http://${rm2_addr}"
               fi
               if [[ -n ${rms} ]];then
                  cluster_startup_params="${cluster_startup_params} -rms ${rms}"
               fi
               continue
           fi

       done
       if [[ -n ${cluster_startup_params} ]];then
         exporter_exec="python /usr/local/hadoop_exporter/hadoop_exporter.py --cluster ${cluster_name} ${cluster_startup_params} --port ${metric_port} "
         echo ${exporter_exec}
         nohup ${exporter_exec} &
         sleep 5
         job_success "startup exporter success"
       else
         isAddMonitor=0
         job_success "no namenode or resourcemanager, skip !"
       fi

    else
       job_fail "not /data/hadoop_exporter directory, check!"
       exit 128

    fi
}

###推送采集python脚本
push_get_metric_py(){

  cat >/usr/local/hadoop_get_metrics.py <<EOF
# -*- coding: utf-8 -*-
import platform
import commands
import sys
import json
import time
import os
from prometheus_client.parser import text_string_to_metric_families
reload(sys)
sys.setdefaultencoding('utf8')

#  bkmonitorbeat path for Community Edition
bkmonitorbeat_path = "/usr/local/gse/plugins/bin/bkmonitorbeat"

# exporter metrics port
metrics_port = ${metric_port}

# exporter url
metrics_url = 'http://127.0.0.1:{}/metrics'.format(metrics_port)

# data ID
data_id = ${data_id}

# access_token
access_token = '${access_token}'

# push timestamp
timestamp = int(time.time() * 1000)

# local ip
local_ip = '${target_ip}'


def get_metrics_for_python_2():
    import urllib2

    request = urllib2.Request(url=metrics_url)
    result = urllib2.urlopen(request, timeout=30)
    if result.getcode() != 200:
        print("err code: {}".format(result.getcode()))
        return None

    return result.read()


def get_metrics_for_python_3():
    import urllib.request

    request = urllib.request.Request(url=metrics_url)
    result = urllib.request.urlopen(request, timeout=30)

    if result.getcode() != 200:
        print("err code: {}".format(result.getcode()))
        return None

    return result.read()


def push_metrics(metrics_content):
    push_data = []
    for family in text_string_to_metric_families(metrics_content):
        dimension_item = {}
        for sample in family.samples:
            for key in sample.labels.keys():
                dimension_item['_{}'.format(key)] =  sample.labels[key]

            push_data.append({
                "metrics": {
                    sample.name: sample.value
                },
                "target": local_ip,
                "dimension": sample.labels,
                "timestamp": timestamp
            })

        # 为了避免传输的内容过大导致上报失败，分段上报
        message_body = {
                "data_id": data_id,
                "access_token": access_token,
                "data": push_data
            }
        (status, output) = commands.getstatusoutput('''{} -report -report.message.kind timeseries -report.bk_data_id {} -report.type agent -report.message.body '{}' '''.format(bkmonitorbeat_path, data_id, json.dumps(message_body)))
        if status != 0 :
           print("insert error,check!")
           sys.exit(1)

        push_data = []


if __name__ == '__main__':
    try:
        if int(platform.python_version().split('.')[0]) == 2:
            content = get_metrics_for_python_2()
        else:
            content = get_metrics_for_python_3()
        if content:
            push_metrics(content)
            print("insert ok")
            sys.exit(0)
        else:
            print("no metric values in {}".format(metrics_url))
        sys.exit(0)

    except Exception as err:
        print(str(err))
        sys.exit(1)
EOF
   job_success "push script success"
}
###配置crontab的周期任务
add_crontab(){
  sed -i '/# hadoop push metrics per min/d' /var/spool/cron/root
  sed -i '/hadoop_get_metrics.py/d' /var/spool/cron/root

  cat >>/var/spool/cron/root <<EOF
# hadoop push metrics per min
*/1 * * * * python /usr/local/hadoop_get_metrics.py
EOF

}

###检测采集脚本执行是否正常
check_script(){

  check_result=$(python /usr/local/hadoop_get_metrics.py)
  if [[ "${check_result}" == "insert ok" ]];then
     job_success "check success"
  else
     job_fail "${check_result}"
     exit 129
  fi


}

IFS="," read -r -a target_ip_arr <<<"$target_ip_list"
for is_ip in "${target_ip_arr[@]}"; do
    if [[ $(ifconfig -a |grep -c "${is_ip}") == '1' ]];then
       target_ip=${is_ip}
       break
    fi
done
if [[ -z $target_ip ]];then
    job_fail "find local_ip fail"
    exit 120
fi

check_bkmonitorbeat
python_setup_prometheus_client
python_setup_pyyaml
python_setup_requests
unzip_exporter_package
start_hadoop_exporter_process

if [[ ${isAddMonitor} -eq 1 ]];then
    push_get_metric_py
    check_script
    add_crontab
fi
exit 0