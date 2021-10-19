#!/bin/bash

###  kafka部署监控脚本

time_format="date +'%Y-%m-%d %H:%M:%S'"
NOW="echo [\`$time_format\`][PID:$$]"

data_id=$1
access_token=$2
broker_port=$3
metric_port=$4
target_ip_list=$5



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

### 添加kminion需要的配置环境信息
add_system_env(){
   sed -i "/KAFKA_BROKERS/d" /etc/profile
   sed -i "/EXPORTER_HOST/d" /etc/profile
   sed -i "/EXPORTER_PORT/d" /etc/profile

   cat >>/etc/profile <<EOF
export KAFKA_BROKERS="127.0.0.1:${broker_port}"
export EXPORTER_HOST="127.0.0.1"
export EXPORTER_PORT="${metric_port}"
EOF
   source /etc/profile
}

### 启动kminion exporter
start_kminion_process(){
    pgrep "kminion" | xargs -i kill -9 {}
    if [[ -f '/data/kminion' ]];then
       mv /data/kminion  /usr/local/
       chmod 775 /usr/local/kminion
       nohup /usr/local/kminion &
    else
       job_fail "not /data/kminion file, check!"
       exit 128

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
###推送采集python脚本
push_get_metric_py(){

  cat >/usr/local/kafka_get_metrics.py <<EOF
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
  sed -i '/# kafka push metrics per min/d' /var/spool/cron/root
  sed -i '/kafka_get_metrics.py/d' /var/spool/cron/root

  cat >>/var/spool/cron/root <<EOF
# kafka push metrics per min
*/1 * * * * python /usr/local/kafka_get_metrics.py
EOF

}

###检测采集脚本执行是否正常
check_script(){
  check_result=$(python /usr/local/kafka_get_metrics.py)
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
add_system_env
start_kminion_process
python_setup_prometheus_client
push_get_metric_py
check_script
add_crontab
exit 0