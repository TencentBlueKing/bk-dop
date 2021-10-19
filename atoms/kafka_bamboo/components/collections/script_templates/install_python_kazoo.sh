# 安装kazoo模块，目前让py脚本调用zookeeper集群
cd /data || exit 128
tar -zxvf kazoo-2.8.0.tar.gz
cd /data/kazoo-2.8.0 || exit 128
python setup.py install

# 添加模块后删除安装包
rm -rf /data/kazoo-2.8.0
rm -f /data/kazoo-2.8.0.tar.gz