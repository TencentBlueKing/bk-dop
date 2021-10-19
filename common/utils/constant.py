# -*- coding: utf-8 -*-
import os


ES_ADMIN = os.getenv('BKAPP_ES_ADMIN')
ES_ADMIN_PASSWORD = os.getenv('BKAPP_ES_ADMIN_PASSWORD')
FILE_SERVER = os.getenv('BKAPP_FILE_SERVER')
HADOOP_PACKAGE_PATH = os.getenv('BKAPP_HADOOP_PACKAGE_PATH')
ES_PACKAGE_PATH = os.getenv('BKAPP_ES_PACKAGE_PATH')
KAFKA_PACKAGE_PATH = os.getenv('BKAPP_KAFKA_PACKAGE_PATH')
JOB_URL = os.getenv('BK_JOB_HOST')

# job bk_cloud_id
bk_cloud_id = 0

# SaaS存储安装包的机器信息
package_source_ip_list = [{"bk_cloud_id": bk_cloud_id, "ip": "{}".format(FILE_SERVER)}]


# es 各版本安装包路径配置
es_package_full_name_dict = {
    "5.4.0": {
        "supervisor": {"package": f"{ES_PACKAGE_PATH}/supervisor.tar.gz"},
        "pypy": {"package": f"{ES_PACKAGE_PATH}/pypy-5.9.0.tar.gz"},
        "TencentKona": {"package": f"{ES_PACKAGE_PATH}/TencentKona-8.tar.gz"},
        "elasticsearch": {"package": f"{ES_PACKAGE_PATH}/elasticsearch-5.4.0.tar.gz"}
    },

    "7.10.0": {
        "supervisor": {"package": f"{ES_PACKAGE_PATH}/supervisor.tar.gz"},
        "pypy": {"package": f"{ES_PACKAGE_PATH}/pypy-5.9.0.tar.gz"},
        "TencentKona": {"package": f"{ES_PACKAGE_PATH}/TencentKona-11.tar.gz"},
        "elasticsearch": {"package": f"{ES_PACKAGE_PATH}/elasticsearch-7.10.0.tar.gz"},
        "cerebro": {"package": f"{ES_PACKAGE_PATH}/cerebro-0.9.4.tar.gz"},
        "kibana": {"package": f"{ES_PACKAGE_PATH}/kibana-7.10.0.tar.gz"}
    },
}

# kafka 各版本安装包路径配置
kafka_package_full_name_dict = {
    "confluent-6.0.1": {
        "TencentKona": {"package": f"{KAFKA_PACKAGE_PATH}/TencentKona-11.tar.gz"},
        "confluent": {"package": f"{KAFKA_PACKAGE_PATH}/confluent-6.0.1.tar.gz"},
        "exporter": {"package": f"{KAFKA_PACKAGE_PATH}/kminion"}
    },
}

# hadoop 各版本安装包路径配置
hadoop_package_full_name_dict = {
    "2.6.0": {
        "hadoop": {"package": f"{HADOOP_PACKAGE_PATH}/hadoop-2.6.0.tar.gz", "version": "2.6.0"},
        "java": {"package": f"{HADOOP_PACKAGE_PATH}/java-1.8.0.tar.gz", "version": "1.8.0"},
        "zookeeper": {"package": f"{HADOOP_PACKAGE_PATH}/zookeeper-3.4.10.tar.gz", "version": "3.4.10"},
        "exporter": {"package": f"{HADOOP_PACKAGE_PATH}/hadoop_exporter.tar.gz", "version": "1.0.0"},
    },
    "3.2.0": {
        "hadoop": {"package": f"{HADOOP_PACKAGE_PATH}/hadoop-3.2.0.tar.gz", "version": "3.2.0"},
        "java": {"package": f"{HADOOP_PACKAGE_PATH}/java-1.8.0.tar.gz", "version": "1.8.0"},
        "zookeeper": {"package": f"{HADOOP_PACKAGE_PATH}/zookeeper-3.4.10.tar.gz", "version": "3.4.10"},
        "exporter": {"package": f"{HADOOP_PACKAGE_PATH}/hadoop_exporter.tar.gz", "version": "1.0.0"},
    },
    "other": {
        "hadoop": {"package": "other", "version": "other"},
        "java": {"package": "other", "version": "other"},
        "zookeeper": {"package": "other", "version": "other"},
        "exporter": {"package": f"{HADOOP_PACKAGE_PATH}/hadoop_exporter.tar.gz", "version": "1.0.0"},
    },
}

# 各组件

# fast_execute_script接口固定参数
fast_execute_script_common_kwargs = {
    "timeout": 1000,
    "account_alias": "root",
    "is_param_sensitive": 0,
    "script_language": 1,
}

# fast_transfer_file接口固定参数
fast_transfer_file_common_kwargs = {
    "account_alias": "root",
}
