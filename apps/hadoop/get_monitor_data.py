# -*- coding:utf-8 -*-
import time

from blueapps.utils.logger import logger
from common.utils.common import compute_metrics_trans, find_last_monitor_data
from common.utils.monitor_sdk import MonitorExecutor


'''
@summary: 定义通过监控平台获取监控数据
@usage:
'''


def get_data_in_namenode_monitor(post_data, bk_username):
    """
        在蓝鲸监控平台获取name node维度的监控数据
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

    # 查询 namenode cluster file 数量(只展示最新获取数据)
    namenode_info = find_last_monitor_data(
        metric_list=monitor_api.get_monitor_data(
            sql=f'''select
                    hadoop_namenode_files_total as file_count,
                    hadoop_namenode_blocks_total as block_count,
                    hadoop_namenode_num_live_data_nodes as live_nodes_count,
                    hadoop_namenode_num_dead_data_nodes as dead_nodes_count,
                    hadoop_namenode_stale_data_nodes as stale_nodes_count,
                    hadoop_namenode_capacity_total/1073741824 as capacity_total_GB
                    from {select_table}
                    {sql_global_where}
                    group by target
                    order by time desc limit 1'''))

    target_ip = namenode_info['target']
    target_time = namenode_info['time']

    # 查询 datanode 节点信息
    datanode_info = monitor_api.get_monitor_data(
        sql=f'''select
               hadoop_datanode_up
               from {select_table}
               where time = {target_time} and target = '{target_ip}'
               group by xferaddr
               order by time desc limit 1''')

    capacity_used = compute_metrics_trans(
        metric_list=monitor_api.get_monitor_data(
            sql=f'''select
                    hadoop_namenode_capacity_used as used,
                    hadoop_namenode_capacity_used_non_dfs as used_non_dfs
                    from {select_table}
                    {sql_global_where} and target = '{target_ip}'
                    order by time '''),
        metric_name_list=['used', 'used_non_dfs'],
        convert_type="G",
        is_rate=False)

    # 查询 namenode cluster block 指标情况

    corrupt_blocks = compute_metrics_trans(
        metric_list=monitor_api.get_monitor_data(
            sql=f'''select
                    hadoop_namenode_corrupt_blocks as metric_value
                    from {select_table}
                    {sql_global_where} and target = '{target_ip}'
                    order by time '''),
        metric_name_list=['metric_value'],
        is_rate=False)

    missing_blocks = compute_metrics_trans(
        metric_list=monitor_api.get_monitor_data(
            sql=f'''select
                    hadoop_namenode_missing_blocks as metric_value
                    from {select_table}
                    {sql_global_where} and target = '{target_ip}'
                    order by time '''),
        metric_name_list=['metric_value'],
        is_rate=False)

    pending_replication_blocks = compute_metrics_trans(
        metric_list=monitor_api.get_monitor_data(
            sql=f'''select
                    hadoop_namenode_pending_replication_blocks as metric_value
                    from {select_table}
                    {sql_global_where} and target = '{target_ip}'
                    order by time '''),
        metric_name_list=['metric_value'],
        is_rate=False)

    under_replicated_blocks = compute_metrics_trans(
        metric_list=monitor_api.get_monitor_data(
            sql=f'''select
                    hadoop_namenode_under_replicated_blocks as metric_value
                    from {select_table}
                    {sql_global_where} and target = '{target_ip}'
                    order by time '''),
        metric_name_list=['metric_value'],
        is_rate=False)

    pending_deletion_blocks = compute_metrics_trans(
        metric_list=monitor_api.get_monitor_data(
            sql=f'''select
                    hadoop_namenode_pending_deletion_blocks as metric_value
                    from {select_table}
                    {sql_global_where} and target = '{target_ip}'
                    order by time '''),
        metric_name_list=['metric_value'],
        is_rate=False)

    postponed_misreplicated_blocks = compute_metrics_trans(
        metric_list=monitor_api.get_monitor_data(
            sql=f'''select
                    hadoop_namenode_postponed_misreplicated_blocks as metric_value
                    from {select_table}
                    {sql_global_where} and target = '{target_ip}'
                    order by time '''),
        metric_name_list=['metric_value'],
        is_rate=False)

    # 查询 node manager 信息列表
    node_manager_info = monitor_api.get_monitor_data(
        sql=f'''select
               hadoop_nodemanager_state
               from {select_table}
               where time = {target_time} and target = '{target_ip}'
               group by host
               order by time desc limit 1''')

    return {
        'file_count': namenode_info['file_count'],
        'block_count': namenode_info['block_count'],
        'datanode_info': datanode_info,
        'node_manager_info': node_manager_info,
        'common_dimensions': ['time', 'metric_value'],
        'nodes_mess_dimensions': ['node_state', 'metric_value'],
        'capacity_used_dimensions': ['time', 'used', 'used_non_dfs'],
        'nodes_mess': [{
            'node_state': 'live_nodes',
            'metric_value': namenode_info['live_nodes_count']},
            {'node_state': 'dead_nodes',
             'metric_value': namenode_info['dead_nodes_count']},
            {'node_state': 'stale_nodes',
             'metric_value': namenode_info['stale_nodes_count']},
        ],
        'capacity_total_GB': namenode_info['capacity_total_GB'],
        'capacity_used': capacity_used,
        'corrupt_blocks': corrupt_blocks,
        'missing_blocks': missing_blocks,
        'pending_replication_blocks': pending_replication_blocks,
        'under_replicated_blocks': under_replicated_blocks,
        'pending_deletion_blocks': pending_deletion_blocks,
        'postponed_misreplicated_blocks': postponed_misreplicated_blocks,
        'last_time': time.strftime("%m/%d %H:%M", time.localtime(float(target_time) / 1000))
    }


def get_data_in_datanode_monitor(post_data, bk_username):
    """
        在蓝鲸监控平台获取data node维度的监控数据
        @param post_data：前端调用时传递的参数体
        @param bk_username: 前端调用时传递的用户名称
    """
    app_id = post_data.get('app_id')
    bk_data_id = post_data.get('bk_data_id')
    selected_datanode = post_data.get('selected_datanode')
    start_time = post_data.get('time_range')[0]
    end_time = post_data.get('time_range')[1]
    monitor_api = MonitorExecutor(bk_username)
    select_table = f"{app_id}_bkmonitor_time_series_{bk_data_id}.base"
    sql_global_where = f" where time <= {end_time} and time >= {start_time}"

    # 查询 datanode 节点信息
    datanode_info = find_last_monitor_data(
        metric_list=monitor_api.get_monitor_data(
            sql=f'''select
                   hadoop_datanode_up as state,
                   hadoop_datanode_capacity/1073741824 as capacity_GB,
                   hadoop_datanode_block_pool_used_percent as used_percent
                   from {select_table}
                   {sql_global_where} and xferaddr = '{selected_datanode}'
                   group by target
                   order by time desc limit 1'''))

    target_ip = datanode_info['target']
    target_time = datanode_info['time']

    # 查询 datanode 容量使用情况
    capacity_used = compute_metrics_trans(
        metric_list=monitor_api.get_monitor_data(
            sql=f'''select
                    hadoop_datanode_used as used,
                    hadoop_datanode_non_dfs_used_space as used_non_dfs,
                    hadoop_datanode_num_blocks as blocks_count
                    from {select_table}
                    {sql_global_where} and target = '{target_ip}' and xferaddr = '{selected_datanode}'
                    order by time '''),
        metric_name_list=['used', 'used_non_dfs'],
        convert_type="G",
        is_rate=False)

    # 查询 datanode 心跳应答情况(last_contact)
    last_contact = compute_metrics_trans(
        metric_list=monitor_api.get_monitor_data(
            sql=f'''select
                    hadoop_datanode_last_contact as metric_value
                    from {select_table}
                    {sql_global_where} and target = '{target_ip}' and xferaddr = '{selected_datanode}'
                    order by time '''),
        metric_name_list=['metric_value'],
        is_rate=False)

    return {
        'state': datanode_info['state'],
        'capacity_GB': datanode_info['capacity_GB'],
        'used_percent': round(float(datanode_info['used_percent']), 4),
        'common_dimensions': ['time', 'metric_value'],
        'capacity_used_dimensions': ['time', 'used', 'used_non_dfs'],
        'capacity_used': capacity_used,
        'last_contact': last_contact,
        'last_time': time.strftime("%m/%d %H:%M", time.localtime(float(target_time) / 1000)),
    }


def get_data_in_rm_monitor(post_data, bk_username):
    """
        在蓝鲸监控平台获取yarn resource manager维度的监控数据
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

    # 查询 resource_manager 整体状态信息
    node_manager_state_info = find_last_monitor_data(
        metric_list=monitor_api.get_monitor_data(
            sql=f'''select
                   hadoop_resourcemanager_active_nodes as active_nodes,
                   hadoop_resourcemanager_lost_nodes as lost_nodes ,
                   hadoop_resourcemanager_rebooted_nodes as rebooted_nodes,
                   hadoop_resourcemanager_unhealthy_nodes as unhealthy_nodes ,
                   hadoop_resourcemanager_decommissioned_nodes as decommissioned_nodes,
                   hadoop_resourcemanager_total_nodes as total_nodes,
                   hadoop_resourcemanager_total_virtual_cores as total_virtual_cores,
                   hadoop_resourcemanager_total_mb/1024 as  total_memory_GB
                   from {select_table}
                   {sql_global_where}
                   group by target
                   order by time desc limit 1'''))

    if not node_manager_state_info:
        logger.error("检测到尚未resource manger集群监控指标")
        return {}
    target_ip = node_manager_state_info['target']
    target_time = node_manager_state_info['time']

    # 查询 apps 各种状态统计情况
    apps_state_info = find_last_monitor_data(
        metric_list=monitor_api.get_monitor_data(
            sql=f'''select
                   hadoop_resourcemanager_apps_completed as active_apps,
                   hadoop_resourcemanager_apps_failed as lost_apps ,
                   hadoop_resourcemanager_apps_killed as rebooted_apps,
                   hadoop_resourcemanager_apps_pending as unhealthy_apps,
                   hadoop_resourcemanager_apps_running as  decommissioned_apps,
                   hadoop_resourcemanager_apps_submitted as submitted_apps
                   from {select_table}
                   {sql_global_where}
                   group by target
                   order by time desc limit 1'''))

    # 查询 container 分配数增长情况
    container_allocated = compute_metrics_trans(
        metric_list=monitor_api.get_monitor_data(
            sql=f'''select
                    hadoop_resourcemanager_containers_allocated as metric_value
                    from {select_table}
                    {sql_global_where} and target = '{target_ip}'
                    order by time '''),
        metric_name_list=['metric_value'],
        is_rate=False)

    # 查询 container 预留数增长情况
    container_reserved = compute_metrics_trans(
        metric_list=monitor_api.get_monitor_data(
            sql=f'''select
                    hadoop_resourcemanager_containers_reserved as metric_value
                    from {select_table}
                    {sql_global_where} and target = '{target_ip}'
                    order by time '''),
        metric_name_list=['metric_value'],
        is_rate=False)

    # 查询 container 待处理数增长情况
    container_pending = compute_metrics_trans(
        metric_list=monitor_api.get_monitor_data(
            sql=f'''select
                    hadoop_resourcemanager_containers_pending as metric_value
                    from {select_table}
                    {sql_global_where} and target = '{target_ip}'
                    order by time '''),
        metric_name_list=['metric_value'],
        is_rate=False)

    # 查询 集群内存 可用容量使用情况
    available_mb = compute_metrics_trans(
        metric_list=monitor_api.get_monitor_data(
            sql=f'''select
                    hadoop_resourcemanager_available_mb as metric_value
                    from {select_table}
                    {sql_global_where} and target = '{target_ip}'
                    order by time '''),
        metric_name_list=['metric_value'],
        is_rate=False)

    # 查询 集群内存 预留容量使用情况
    reserved_mb = compute_metrics_trans(
        metric_list=monitor_api.get_monitor_data(
            sql=f'''select
                    hadoop_resourcemanager_reserved_mb as metric_value
                    from {select_table}
                    {sql_global_where} and target = '{target_ip}'
                    order by time '''),
        metric_name_list=['metric_value'],
        is_rate=False)

    # 查询 集群内存 以分配容量使用情况
    allocated_mb = compute_metrics_trans(
        metric_list=monitor_api.get_monitor_data(
            sql=f'''select
                    hadoop_resourcemanager_allocated_mb as metric_value
                    from {select_table}
                    {sql_global_where} and target = '{target_ip}'
                    order by time '''),
        metric_name_list=['metric_value'],
        is_rate=False)

    return {
        'total_nodes': node_manager_state_info['total_nodes'],
        'total_virtual_cores': node_manager_state_info['total_virtual_cores'],
        'total_memory_GB': node_manager_state_info['total_memory_GB'],
        'common_dimensions': ['time', 'metric_value'],
        'nodes_state_dimensions': ['node_state', 'metric_value'],
        'container_allocated': container_allocated,
        'container_reserved': container_reserved,
        'container_pending': container_pending,
        'available_mb': available_mb,
        'reserved_mb': reserved_mb,
        'allocated_mb': allocated_mb,
        'apps_state': [{
            'node_state': 'active',
            'metric_value': apps_state_info['active_apps']},
            {'node_state': 'lost',
             'metric_value': apps_state_info['lost_apps']},
            {'node_state': 'rebooted',
             'metric_value': apps_state_info['rebooted_apps']},
            {'node_state': 'unhealthy',
             'metric_value': apps_state_info['unhealthy_apps']},
            {'node_state': 'decommissioned',
             'metric_value': apps_state_info['decommissioned_apps']},
            {'node_state': 'submitted',
             'metric_value': apps_state_info['submitted_apps']},
        ],
        'nodes_state': [
            {'node_state': 'active',
             'metric_value': node_manager_state_info['active_nodes']},
            {'node_state': 'lost',
             'metric_value': node_manager_state_info['lost_nodes']},
            {'node_state': 'rebooted',
             'metric_value': node_manager_state_info['rebooted_nodes']},
            {'node_state': 'unhealthy',
             'metric_value': node_manager_state_info['unhealthy_nodes']},
            {'node_state': 'decommissioned',
             'metric_value': node_manager_state_info['decommissioned_nodes']},
        ],
        'last_time': time.strftime("%m/%d %H:%M", time.localtime(float(target_time) / 1000)),
    }


def get_data_in_nm_monitor(post_data, bk_username):
    """
        在蓝鲸监控平台获取yarn node manager维度的监控数据
        @param post_data：前端调用时传递的参数体
        @param bk_username: 前端调用时传递的用户名称
    """
    app_id = post_data.get('app_id')
    bk_data_id = post_data.get('bk_data_id')
    selected_node_manager = post_data.get('selected_nm')
    start_time = post_data.get('time_range')[0]
    end_time = post_data.get('time_range')[1]
    monitor_api = MonitorExecutor(bk_username)
    select_table = f"{app_id}_bkmonitor_time_series_{bk_data_id}.base"
    sql_global_where = f" where time <= {end_time} and time >= {start_time}"

    # 查询 node manager 节点信息
    node_manager_info = find_last_monitor_data(
        metric_list=monitor_api.get_monitor_data(
            sql=f'''select
                   hadoop_nodemanager_state as state
                   from {select_table}
                   {sql_global_where} and host = '{selected_node_manager}'
                   group by target
                   order by time desc limit 1'''))

    target_ip = node_manager_info['target']
    target_time = node_manager_info['time']

    # 查询 node manager container数量增长情况
    nm_containers_num = compute_metrics_trans(
        metric_list=monitor_api.get_monitor_data(
            sql=f'''select
                    hadoop_nodemanager_num_containers as metric_value
                    from {select_table}
                    {sql_global_where} and target = '{target_ip}' and host = '{selected_node_manager}'
                    order by time '''),
        metric_name_list=['metric_value'],
        is_rate=False)

    # 查询 node manager 可用内存容量动态情况
    nm_avail_memory_mb = compute_metrics_trans(
        metric_list=monitor_api.get_monitor_data(
            sql=f'''select
                    hadoop_nodemanager_avail_memory_mb as metric_value
                    from {select_table}
                    {sql_global_where} and target = '{target_ip}' and host = '{selected_node_manager}'
                    order by time '''),
        metric_name_list=['metric_value'],
        is_rate=False)

    # 查询 node manager 已使用内存容量动态情况
    nm_used_memory_mb = compute_metrics_trans(
        metric_list=monitor_api.get_monitor_data(
            sql=f'''select
                    hadoop_nodemanager_used_memory_mb as metric_value
                    from {select_table}
                    {sql_global_where} and target = '{target_ip}' and host = '{selected_node_manager}'
                    order by time '''),
        metric_name_list=['metric_value'],
        is_rate=False)

    # 查询 node manager 未分配CPU动态情况
    nm_available_virtual_cores = compute_metrics_trans(
        metric_list=monitor_api.get_monitor_data(
            sql=f'''select
                    hadoop_nodemanager_available_virtual_cores as metric_value
                    from {select_table}
                    {sql_global_where} and target = '{target_ip}' and host = '{selected_node_manager}'
                    order by time '''),
        metric_name_list=['metric_value'],
        is_rate=False)

    # 查询 node manager 已分配的CPU动态情况
    nm_used_virtual_cores = compute_metrics_trans(
        metric_list=monitor_api.get_monitor_data(
            sql=f'''select
                    hadoop_nodemanager_used_virtual_cores as metric_value
                    from {select_table}
                    {sql_global_where} and target = '{target_ip}' and host = '{selected_node_manager}'
                    order by time '''),
        metric_name_list=['metric_value'],
        is_rate=False)

    return {
        'state': node_manager_info['state'],
        'common_dimensions': ['time', 'metric_value'],
        'nm_containers_num': nm_containers_num,
        'nm_avail_memory_mb': nm_avail_memory_mb,
        'nm_used_memory_mb': nm_used_memory_mb,
        'nm_available_virtual_cores': nm_available_virtual_cores,
        'nm_used_virtual_cores': nm_used_virtual_cores,
        'last_time': time.strftime("%m/%d %H:%M", time.localtime(float(target_time) / 1000)),
    }
