## 正式环境部署指南


### 在正式环境准备好需要的资源
- 1：该SaaS的mysql资源
- 2：该SaaS的redis或者rabbitmq资源
- 3：准备一台文件分发机器存放Elasticsearch、Confluent(Kafka)、Hadoop的安装介质，按下面的目录结构存放。
```
/data/package
|-- es
|   |-- TencentKona-11.tar.gz
|   |-- TencentKona-8.tar.gz
|   |-- cerebro-0.9.4.tar.gz
|   |-- confluent-6.0.1.tar.gz
|   |-- elasticsearch-5.4.0.tar.gz
|   |-- elasticsearch-7.10.0.tar.gz
|   |-- kibana-7.10.0.tar.gz
|   |-- pypy-5.9.0.tar.gz
|   `-- supervisor.tar.gz
|-- hadoop
|   |-- hadoop-2.6.0.tar.gz
|   |-- hadoop-3.2.0.tar.gz
|   |-- java-1.8.0.tar.gz
|   `-- zookeeper-3.4.10.tar.gz
|-- kafka
|   |-- TencentKona-11.tar.gz
|   `-- confluent-6.0.1.tar.gz
`-- module
    `-- kazoo-2.8.0.tar.gz
```
安装介质可从 https://share.weiyun.com/ZXBIVDdL 下载， 密码是：32xwnm


将文件服务器的机器在配置平台绑定到其中一个业务上，并在作业平台对文件服务器开启文件分发功能的IP白名单，让全业务可正常调度。
- [设置作业平台的IP白名单的流程参考这里](./set_write_ip.md)


### 环境变量配置说明
- `BKAPP_ES_ADMIN`, ElasticSearch的内置管理员账号，设置为admin。
- `BKAPP_ES_ADMIN_PASSWORD`, ElasticSearch的内置管理员密码，设置为admin。
- `BKAPP_HADOOP_PACKAGE_PATH`, Hadoop安装介质所在路径。
- `BKAPP_KAFKA_PACKAGE_PATH`, Kafka安装介质所在路径。
- `BKAPP_ES_PACKAGE_PATH`, ElasticSearch安装介质所在路径。
- `BKAPP_FILE_SERVER`, 文件服务器的IP。


### 通过在 releases 中获取安装包下载的方式安装
如果你不需要对项目进行二次开发，请直接在 releases 中获取打包好的版本。安装蓝鲸平台的开发者中心上传的"S-mart应用"
中点击"上传部署新应用"，上传对应的包即可。SaaS的环境配置按照蓝鲸指引的配置即可


### 通过下载对应源码方式的安装

如果对项目有二次开发和定制的需求，可以通过 Fork 源代码到自己的仓库进行修改，修改后可放在你的蓝鲸平台部署。

##### 1） 安装依赖包（若以下操作已经执行过则无需执行）

进入项目中frontend/bkx/，执行以下命令安装
```
npm install
```
##### 2）打包前端资源 在frontend/bkx 目录下，继续执行以下命令打包前端静态资源
```
npm config set registry http://mirrors.cloud.tencent.com/npm/
export NODE_OPTIONS=--max_old_space_size=4096
npm install
npm run build:open
```

##### 3）创建应用
前往你部署的蓝鲸PaaS平台，在"开发者中心"点击"应用创建"，填写需要的参数，
注意代码仓库填写你的 Github 仓库地址，账号和密码。
