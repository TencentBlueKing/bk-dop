#!/bin/bash

###  es环境初始化脚本

anynowtime="date +'%Y-%m-%d %H:%M:%S'"
NOW="echo [\`$anynowtime\`][PID:$$]"

##### 可在脚本开始运行时调用，打印当时的时间戳及PID。
function job_start
{
    echo "`eval $NOW` job_start"
}

##### 可在脚本执行成功的逻辑分支处调用，打印当时的时间戳及PID。
function job_success
{
    MSG="$*"
    echo "`eval $NOW` job_success:[$MSG]"
    exit 0
}

##### 可在脚本执行失败的逻辑分支处调用，打印当时的时间戳及PID。
function job_fail
{
    MSG="$*"
    echo "`eval $NOW` job_fail:[$MSG]"
    exit 1
}

job_start


## 初始化
ESENV="/data/esenv"
##  暂时不考虑多个路径的情况
#ESDATA="/data/esdata"
ESLOG="/data/eslog"
user=elastic

adduser $user
echo -e "elastic soft memlock unlimited\nelastic hard memlock unlimited" >> /etc/security/limits.conf
echo -e "vm.max_map_count=262144\nvm.swappiness=1" >> /etc/sysctl.conf ;sysctl -p

path=`cat /etc/mtab |grep /data |grep -v overlay |awk '{print $2}'`
if [[ "x$path" == "x/data" ||  "x$path" == "x" ]];then
    mkdir -p /data/esdata && chown -R elastic:elastic /data/esdata
    ESDATA="/data/esdata"
else
    for i in $path;do
        mkdir $i/esdata  && chown -R elastic:elastic $i/esdata
        datapath=$i/esdata,$datapath
    done
    ESDATA=`echo $datapath|sed 's/,$//'`
fi

[[ ! -e "$ESENV" ]] && mkdir -p $ESENV  && chown -R $user:$user $ESENV
[[ ! -e "$ESLOG" ]] && mkdir -p $ESLOG  && chown -R $user:$user $ESLOG

cat << 'EOF' > /data/esenv/esprofile
export JAVA_HOME=/data/esenv/java
export JRE=$JAVA_HOME/jre
export PATH=$JAVA_HOME/bin:$JRE_HOME/bin:$PATH
export CLASSPATH=".:$JAVA_HOME/lib:$JRE/lib:$CLASSPATH"
export ES_HOME=/data/esenv/es
export ES_CONF_DIR=$ES_HOME/config
export PATH=$PATH:$ES_HOME/bin
export PATH=$PATH:$ES_HOME/sbin
export PATH=$PATH:${JAVA_HOME}/bin:${ES_HOME}/bin:${ES_HOME}/sbin
EOF

echo "export ESDATA=$ESDATA" >> /data/esenv/esprofile

chown elastic  /data/esenv/esprofile

sed -i '/esprofile/d' /etc/profile
echo "source /data/esenv/esprofile" >>/etc/profile
env
job_success "初始化完成"