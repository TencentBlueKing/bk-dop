## 本地环境部署指南
### 文件服务器准备
准备一台机器存放Elasticsearch、Confluent(Kafka)、Hadoop的安装介质，按下面的目录结构存放。
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

### 运行环境准备
- python-3.6.8 以上
- django-2.2.6
- mysql-5.7 以上
- redis or rabbitmq

### 安装依赖
- pip install -r requirements.txt

### 本地启动项目需要设置的环境变量
- `APP_ID`, 设置为你的蓝鲸智云版项目应用ID
- `APP_TOKEN`, APP_TOKEN 设置为你的蓝鲸智云版项目应用 TOKEN
- `BKAPP_ES_ADMIN`, ElasticSearch的内置管理员账号，设置为admin。
- `BKAPP_ES_ADMIN_PASSWORD`, ElasticSearch的内置管理员密码，设置为admin。
- `BKAPP_HADOOP_PACKAGE_PATH`, Hadoop安装介质所在路径。
- `BKAPP_KAFKA_PACKAGE_PATH`, Kafka安装介质所在路径。
- `BKAPP_ES_PACKAGE_PATH`, ElasticSearch安装介质所在路径。
- `BKAPP_FILE_SERVER`, 文件服务器的IP。
- `BKPAAS_URL`, https://your_bk_paas.com/ ，你的蓝鲸pass环境域名地址。如果你的蓝鲸平台没有配置https，则配置格式为： http://your_bk_paas.com/
- `BK_JOB_HOST` , 你的蓝鲸环境的JOB平台访问域名(示例:http://your_job_paas.com:80) 

### 在项目的config目录下增加local_settings.py文件
```python
# local_settings.py

#如果本地环境使用rabbitmq
BROKER_URL = 'amqp://guest:guest@localhost:5672//'

#如果本地环境使用redis
BROKER_URL = 'redis://localhost:6379/0'

# NAME,USER,PASSWORD,HOST,PORT 这些信息根据你的本地环境自行定义并设置
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "dop_dev",
        "USER": "root",
        "PASSWORD": "your local mysql password",
        "HOST": "localhost",
        "PORT": "3306",
    },
}
```

### 本地运行后端项目

注意： {BK_PAAS_HOST} 是个变量， 代表你的paas的一级域名的内容。比如你pass域名是：bk.xxx.com ，则 BK_PAAS_HOST = xxx.com
```bash
# 在本地MySQL创建数据库
CREATE DATABASE `dop_dev` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;

# 初始化本地数据库
python manage.py migrate
# 运行项目
python manage.py runserver dev.{BK_PAAS_HOST}:8000  
# 启动celery项目
python manage.py celery worker -Q er_execute,er_schedule -l info --concurrency 4
```
本地hosts文件增加
```
windows: 在 C:\Windows\System32\drivers\etc\host 文件中添加“127.0.0.1 dev.{BK_PAAS_HOST}”。
mac/unix: 执行 “sudo vim /etc/hosts”，添加“127.0.0.1 dev.{BK_PAAS_HOST}”。
```
然后访问 http://dev.{BK_PAAS_HOST}:8000 即可访问后端项目(如果访问8000端口过程出现寻找不到index.html文件，则是正常现象。是因为前端项目尚未构建好放出index.html。建议单独启动前端项目后通过访问)

### 本地运行前端项目
- [本地运行前端项目需要参考前端部署指南](./web_dev.md)
