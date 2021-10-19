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
KAFKAENV="/data/kafkaenv"
##  暂时不考虑多个路径的情况
KAFKADATA="/data/kafkadata"
ZKDATA="/data/zkdata"
KAFKALOG="/data/kafkalog"
user=kafka


adduser $user
echo -e "kafka soft memlock unlimited\nkafka hard memlock unlimited" >> /etc/security/limits.conf
echo -e "vm.max_map_count=262144\nvm.swappiness=1" >> /etc/sysctl.conf ;sysctl -p
[[ ! -e "$KAFKADATA" ]] && mkdir -p $KAFKADATA && chown -R $user:$user $KAFKADATA
[[ ! -e "$KAFKAENV" ]] && mkdir -p $KAFKAENV  && chown -R $user:$user $KAFKAENV
[[ ! -e "$ZKDATA" ]] && mkdir -p $ZKDATA  && chown -R $user:$user $ZKDATA
[[ ! -e "$KAFKALOG" ]] && mkdir -p $KAFKALOG  && chown -R $user:$user $KAFKALOG

cat << 'EOF' > /data/kafkaenv/kafkaprofile
export JAVA_HOME=/data/kafkaenv/java
export PATH=$JAVA_HOME/bin:$PATH

export CONFLUENT_HOME=/data/kafkaenv/confluent
export PATH=$PATH:$CONFLUENT_HOME/bin
EOF

echo "export KAFKADATA=$KAFKADATA" >> $KAFKAENV/kafkaprofile
echo "export ZKDATA=$ZKDATA" >> $KAFKAENV/kafkaprofile

chown $user  $KAFKAENV/kafkaprofile

sed -i '/kafkaprofile/d' /etc/profile
echo "source /data/kafkaenv/kafkaprofile" >>/etc/profile
env


zklist=$1
version=$2

user="kafka"

nodeip=`ip a|grep eth1|grep inet |awk '{print $2}'| awk -F'/' '{print $1}'`
source /etc/profile
env

zktemplate="/data/kafkaenv/confluent/etc/kafka/zookeeper.properties.template"
zkconfig="/data/kafkaenv/confluent/etc/kafka/zookeeper.properties"
kafkatemplate="/data/kafkaenv/confluent/etc/kafka/server.properties.template"
kafkaconfig="/data/kafkaenv/confluent/etc/kafka/server.properties"

OIFS=$IFS
IFS=","

zkArray=($zklist)
server1=${zkArray[0]}
server2=${zkArray[1]}
server3=${zkArray[2]}
IFS=$OIFS;

zkconnect="$server1:2181,$server2:2181,$server3:2181"


## 解压介质包
mv /data/*.tar.gz /data/kafkaenv
cd /data/kafkaenv
echo "解压kafka介质包"
tar zxf $version.tar.gz && ln -s $version confluent  || job_fail "tar $version.tar.gz  failed"
echo "解压java介质包"
tar zxf TencentKona-11.tar.gz && ln -s TencentKona-11 java || job_fail "tar java failed"
ln -sf  /data/kafkaenv/java/bin/java /usr/bin/java || job_fail "创建java软链接失败"

## 创建模版文件
cat <<'EOF' > $zktemplate
tickTime=2000
dataDir=__ZKDATA__
clientPort=2181
initLimit=5
syncLimit=2
server.1=__SERVER1__:2888:3888
server.2=__SERVER2__:2888:3888
server.3=__SERVER3__:2888:3888
4lw.commands.whitelist=*
EOF

cat <<'EOF' > $kafkatemplate
listeners=PLAINTEXT://:9092
advertised.host.name=__IP__
advertised.listeners=PLAINTEXT://__IP__:9092
num.network.threads=3
num.io.threads=8
socket.send.buffer.bytes=102400
socket.receive.buffer.bytes=102400
socket.request.max.bytes=104857600
log.dirs=__KAFKADATA__
num.partitions=16
num.recovery.threads.per.data.dir=1

offsets.topic.replication.factor=1
transaction.state.log.replication.factor=1
transaction.state.log.min.isr=1
log.retention.hours=168

log.segment.bytes=1073741824

log.retention.check.interval.ms=300000
zookeeper.connect=__ZKCONNECT__

zookeeper.connection.timeout.ms=60000
group.initial.rebalance.delay.ms=0
EOF

echo "修改zk配置"
cp $zktemplate $zkconfig

sed -i  -e "s#__ZKDATA__#$ZKDATA#"  -e \
    "s/__SERVER1__/$server1/" -e \
    "s/__SERVER2__/$server2/"  -e \
    "s/__SERVER3__/$server3/"   $zkconfig


if [ "$nodeip" == "$server1" ];then
  echo "1" > $ZKDATA/myid
elif [ "$nodeip" == "$server2" ]; then
  echo "2" > $ZKDATA/myid
elif [ "$nodeip" == "$server3"  ]; then
  echo "3" > $ZKDATA/myid
fi

echo "zk配置修改完成"

echo "修改kafka配置"
cp $kafkatemplate $kafkaconfig
sed -i  -e "s/__IP__/$nodeip/g"  -e \
    "s#__KAFKADATA__#$KAFKADATA#" -e \
    "s/__ZKCONNECT__/$zkconnect/"   $kafkaconfig

### 启动zookeeper
echo "启动zookeeper"


/data/kafkaenv/confluent/bin/zookeeper-server-start -daemon /data/kafkaenv/confluent/etc/kafka/zookeeper.properties
# sleep 20秒等待zookeeper服务拉起
sleep 20
#kafka-configs  --zookeeper $nodeip:2181 --alter --add-config 'SCRAM-SHA-256=[password=admin-secret],SCRAM-SHA-512=[password=admin-secret]' --entity-type users --entity-name admin

echo "启动kafka..."
sysmem=`cat /proc/meminfo |grep MemTotal|awk '{print $2}'`

if [ "$sysmem" -ge 12000000 ];then
    export KAFKA_HEAP_OPTS="-Xmx6G -Xms6G"
fi
LOG_DIR=/data/kafkalog JMX_PORT=9999  /data/kafkaenv/confluent/bin/kafka-server-start -daemon /data/kafkaenv/confluent/etc/kafka/server.properties