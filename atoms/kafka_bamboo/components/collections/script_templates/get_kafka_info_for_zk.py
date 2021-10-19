#!/usr/bin/env python
# -*- coding:utf-8 -*-

import json
import logging
import sys

from kazoo.client import KazooClient


logging.basicConfig()

broker_list = []
topic_list = []
zk_url = ''


def get_broker_info_for_zk(zk_chroot=None):
    global broker_list
    if zk_chroot:
        broker_url = '/{}/brokers/ids'.format(zk_chroot)
    else:
        broker_url = '/brokers/ids'
    try:
        zk = KazooClient(hosts='{}'.format(zk_url), timeout=5)
        zk.start(timeout=5)
        for broker_id in zk.get_children(broker_url):
            data, version = zk.get('{}/{}'.format(broker_url, str(broker_id)))
            broker_list.append((json.loads(data)).get('host'))
        zk.stop()
        return 0

    except Exception as e:
        if str(e):
            print(str(e))
        else:
            print("zookeeper集群查询不到对应的broker信息")
        return 1


def get_topic_info_for_zk(zk_chroot=None):
    global topic_list
    if zk_chroot:
        topic_url = '/{}/config/topics'.format(zk_chroot)
    else:
        topic_url = '/config/topics'
    try:
        zk = KazooClient(hosts='{}'.format(zk_url), timeout=5)
        zk.start(timeout=5)
        topic_list = zk.get_children(topic_url)
        zk.stop()
        return 0

    except Exception as e:
        if str(e):
            print(str(e))
            return 1
        print("zookeeper集群查询不到对应的topic信息")
        return 0


if __name__ == '__main__':
    try:

        zk_url = sys.argv[1]
        if len(sys.argv) == 3:
            chroot = sys.argv[2]
            if get_broker_info_for_zk(chroot) == 0:
                if get_topic_info_for_zk(chroot) == 0:
                    print({'broker_list': broker_list, 'topic_list': topic_list})
                    sys.exit(0)
                else:
                    sys.exit(1)
            else:
                sys.exit(1)
        elif len(sys.argv) > 3:
            print("检测存在多余参数，请核实:{}".format(sys.argv))
        else:
            if get_broker_info_for_zk() == 0:
                if get_topic_info_for_zk() == 0:
                    print({'broker_list': broker_list, 'topic_list': topic_list})
                    sys.exit(0)
                else:
                    sys.exit(1)
            else:
                sys.exit(1)

    except Exception as err:
        print("{}:{}".format(str(err), sys.argv))
        sys.exit(1)
