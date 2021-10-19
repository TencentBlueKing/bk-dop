# -*- coding:utf-8 -*-
import time

from common.utils.common import compute_metrics_trans, find_last_monitor_data
from common.utils.monitor_sdk import MonitorExecutor
from apps.kafka.models import KafkaBroker


'''
@summary: 定义通过监控平台获取监控数据
@usage:
'''


def get_data_in_cluster_monitor(post_data, bk_username):
    """
        在蓝鲸监控平台获取cluster维度的监控数据
        @param post_data：前端调用时传递的参数体
        @param bk_username: 前端调用时传递的用户名称
    """
    app_id = post_data.get('app_id')
    bk_data_id = post_data.get('bk_data_id')
    start_time = post_data.get('time_range')[0]
    end_time = post_data.get('time_range')[1]
    monitor_api = MonitorExecutor(bk_username)
    select_table = f"{app_id}_bkmonitor_time_series_{bk_data_id}.base"
    sql_global_where = f" where time <= {end_time} and time >= {start_time}"
    # 获取集群上线最久的节点来做集群监控条件
    target_ip = KafkaBroker.objects.filter(cluster_name=post_data.get('cluster_name')).order_by('id')[0].ip

    # 查询集群的信息(只展示最新获取数据)
    cluster_info = find_last_monitor_data(
        metric_list=monitor_api.get_monitor_data(
            sql=f'''select
                    kminion_kafka_cluster_info
                    from {select_table}
                    {sql_global_where}
                    group by broker_count,cluster_version
                    order by time desc limit 1'''))

    # 查询集群的broker信息(根据同步采集ip和采集最新时间，获取最新获取集群所有broker数据)
    broker_info = monitor_api.get_monitor_data(sql=f'''select
                                               kminion_kafka_broker_info
                                               from {select_table}
                                               {sql_global_where} and  target = '{target_ip}'
                                               group by address,port,is_controller,broker_id
                                               order by time desc limit 1''')

    # 查看集群消费者组信息(根据同步采集ip和采集最新时间，获取最新获取集群所有的consumer group数据)
    consumer_group_info = monitor_api.get_monitor_data(sql=f'''select
                                                       kminion_kafka_consumer_group_info
                                                       from {select_table}
                                                       {sql_global_where} and target = '{target_ip}'
                                                       group by group_id
                                                       order by time desc limit 1''')

    # 查看集群topic信息(根据同步采集ip和采集最新时间，获取最新获取集群所有的topic数据)
    topic_info = monitor_api.get_monitor_data(sql=f'''select
                                              kminion_kafka_topic_info
                                              from {select_table}
                                              {sql_global_where} and target = '{target_ip}'
                                              group by topic_name
                                              order by time desc limit 1''')

    # 统计每个broker的日志容量(只展示最新获取数据)
    log_size_info_tmp = monitor_api.get_monitor_data(sql=f'''select
                                                     kminion_kafka_broker_log_dir_size_total_bytes as log_size
                                                     from {select_table}
                                                     {sql_global_where}
                                                     group by address
                                                     order by time desc limit 1 ''')
    log_size_info = [
        {
            "value": round(int(query.get("log_size")) / 1024 / 1024, 2),
            "name": query.get("address")
        }
        for query in log_size_info_tmp
    ]

    # 获取集群最近时间每分钟总产生消息数
    message_in_rate = compute_metrics_trans(
        metric_list=monitor_api.get_monitor_data(
            sql=f'''select
            sum(kminion_kafka_topic_high_water_mark_sum) as metric
            from {select_table}
            {sql_global_where} and target = '{target_ip}'
            group by minute1
            order by  time '''),
        metric_name_list=["metric"],
        is_rate=True)

    # 获取集群的最近时间内每分钟发送请求数
    requests_sent_rate = compute_metrics_trans(
        metric_list=monitor_api.get_monitor_data(
            sql=f'''select
            sum(kafka_requests_sent_total) as metric
            from {select_table}
            {sql_global_where}
            group by minute1
            order by time'''),
        metric_name_list=["metric"],
        is_rate=True)

    # 获取集群的最近时间内每分钟接收请求数
    requests_received_rate = compute_metrics_trans(
        metric_list=monitor_api.get_monitor_data(
            sql=f'''select
                sum(kafka_requests_received_total) as metric
                from {select_table}
                {sql_global_where}
                group by minute1
                order by time'''),
        metric_name_list=["metric"],
        is_rate=True)

    # 获取集群的最近时间内每分钟进入流量
    sent_bytes_rate = compute_metrics_trans(
        metric_list=monitor_api.get_monitor_data(
            sql=f'''select
                sum(kafka_sent_bytes_total) as metric
                from {select_table}
                {sql_global_where}
                group by minute1
                order by time'''),
        metric_name_list=["metric"],
        convert_type='K',
        is_rate=True)

    # 获取集群的最近时间内每分钟流出流量
    received_bytes_rate = compute_metrics_trans(
        metric_list=monitor_api.get_monitor_data(
            sql=f'''select
                sum(kafka_received_bytes_total) as metric
                from {select_table}
                {sql_global_where}
                group by minute1
                order by time'''),
        metric_name_list=["metric"],
        convert_type='K',
        is_rate=True)

    return {
        'cluster_info': cluster_info,
        'online_broker_count': int(cluster_info['broker_count']),
        'cluster_version': cluster_info['cluster_version'],
        'consumer_group_length': len(consumer_group_info),
        'topic_length': len(topic_info),
        'broker_info': broker_info,
        'log_size_info': log_size_info,
        'dimensions': ['time', 'metric_rate'],
        'message_in_rate': message_in_rate,
        'requests_sent_rate': requests_sent_rate,
        'requests_received_rate': requests_received_rate,
        'sent_bytes_rate': sent_bytes_rate,
        'received_bytes_rate': received_bytes_rate,
        'consumer_group_info': consumer_group_info,
        'topic_info': topic_info,
        'last_time': time.strftime("%m/%d %H:%M", time.localtime(float(cluster_info['time']) / 1000))
    }


def get_data_in_topic_monitor(post_data, bk_username):
    """
        在蓝鲸监控平台获取topic维度上的监控数据
        @param post_data：前端调用时传递的参数体
        @param bk_username: 前端调用时传递的用户名称
    """
    app_id = post_data.get('app_id')
    topic_name = post_data.get('topic_name')
    bk_data_id = post_data.get('bk_data_id')
    start_time = post_data.get('time_range')[0]
    end_time = post_data.get('time_range')[1]
    monitor_api = MonitorExecutor(bk_username)
    select_table = f"{app_id}_bkmonitor_time_series_{bk_data_id}.base"
    sql_global_where = f" where topic_name = '{topic_name}' and time <= {end_time} and time >= {start_time}"
    # 获取集群上线最久的节点来做集群监控条件
    target_ip = KafkaBroker.objects.filter(cluster_name=post_data.get('cluster_name')).order_by('id')[0].ip

    # 查询指定的topic的信息(只展示最新获取数据)
    topic_info = find_last_monitor_data(
        metric_list=monitor_api.get_monitor_data(
            sql=f'''select
                    kminion_kafka_topic_info
                    from {select_table}
                    {sql_global_where}
                    group by replication_factor, partition_count, cleanup_policy
                    order by time desc limit 1'''))

    topic_message_in_rate = compute_metrics_trans(
        metric_list=monitor_api.get_monitor_data(
            sql=f'''select
                    kminion_kafka_topic_high_water_mark_sum as metric
                    from {select_table}
                    {sql_global_where} and target = '{target_ip}'
                    order by time'''),
        metric_name_list=["metric"],
        is_rate=True)

    topic_log_size = compute_metrics_trans(
        metric_list=monitor_api.get_monitor_data(
            sql=f'''select
                    kminion_kafka_topic_log_dir_size_total_bytes as topic_log_size
                    from {select_table}
                    {sql_global_where} and target = '{target_ip}'
                     order by time'''),
        metric_name_list=["topic_log_size"],
        convert_type="M",
        is_rate=False)

    return {
        'replication_factor': int(topic_info['replication_factor']),
        'partition_count': int(topic_info['partition_count']),
        'cleanup_policy': topic_info['cleanup_policy'],
        'dimensions': ['time', 'metric_rate'],
        'topic_message_in_rate': topic_message_in_rate,
        'topic_log_size_dimensions': ['time', 'topic_log_size'],
        'topic_log_size': topic_log_size,
        'last_time': time.strftime("%m/%d %H:%M", time.localtime(float(topic_info['time']) / 1000))
    }


def get_data_in_consumer_group_monitor(post_data, bk_username):
    """
        在蓝鲸监控平台获取consumer_group维度上的监控数据
        @param post_data：前端调用时传递的参数体
        @param bk_username: 前端调用时传递的用户名称
    """
    app_id = post_data.get('app_id')
    bk_data_id = post_data.get('bk_data_id')
    topic_name = post_data.get('topic_name')
    consumer_group_name = post_data.get('consumer_group_name')
    start_time = post_data.get('time_range')[0]
    end_time = post_data.get('time_range')[1]
    monitor_api = MonitorExecutor(bk_username)
    select_table = f"{app_id}_bkmonitor_time_series_{bk_data_id}.base"
    sql_global_where = f''' where group_id = '{consumer_group_name}' and time <= {end_time} and time >= {start_time}'''
    # 获取集群上线最久的节点来做集群监控条件
    target_ip = KafkaBroker.objects.filter(cluster_name=post_data.get('cluster_name')).order_by('id')[0].ip

    # 查询指定的topic的信息(只展示最新获取数据)
    consumer_group_info = find_last_monitor_data(
        metric_list=monitor_api.get_monitor_data(
            sql=f'''select
                kminion_kafka_consumer_group_info
                from {select_table}
                {sql_global_where}
                group by state, member_count, protocol, coordinator_id , protocol_type
                order by time desc limit 1'''))

    consumer_lag = compute_metrics_trans(
        metric_list=monitor_api.get_monitor_data(
            sql=f'''select
                kminion_kafka_consumer_group_topic_lag as behind_lag
                from {select_table}
                {sql_global_where} and topic_name = '{topic_name}' and target = '{target_ip}'
                order by time'''),
        metric_name_list=["behind_lag"],
        is_rate=False)

    consumer_lag_per_partition = monitor_api.get_monitor_data(
        sql=f'''select
             kminion_kafka_consumer_group_topic_partition_lag as new_behind_lag_per_partition
             from {select_table}
             {sql_global_where} and topic_name = '{topic_name}' and target = '{target_ip}'
             group by partition_id
             order by time desc limit 1 ''')

    return {
        'state': consumer_group_info['state'],
        'member_count': int(consumer_group_info['member_count']),
        'protocol': consumer_group_info['protocol'],
        'coordinator_id': consumer_group_info['coordinator_id'],
        'protocol_type': consumer_group_info['protocol_type'],
        'dimensions': ['time', 'behind_lag'],
        'consumer_lag': consumer_lag,
        'consumer_lag_per_partition_dimensions': ['partition_id', 'new_behind_lag_per_partition'],
        'consumer_lag_per_partition': consumer_lag_per_partition,
        'last_time': time.strftime("%m/%d %H:%M", time.localtime(float(consumer_group_info['time']) / 1000))
    }
