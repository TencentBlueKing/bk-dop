# -*- coding:utf-8 _*-
import json
from datetime import datetime

from pytz import timezone

from apps.globalview.models import TaskRecord
from blueapps.utils.logger import logger
from common.utils.bamboo_api import PipelineTaskApi
from common.utils.common import build_fail_result, build_success_result
from common.utils.constant import JOB_URL


'''
@summary:
@usage:
'''


def get_task_state(kwargs, get_fail_node=False):
    """
       根据pipeline_id来获取task的流程树信息
    """
    return_data = []
    fail_node_id = None
    pipeline_id = kwargs.get('pipeline_id')
    pipeline_states = PipelineTaskApi(kwargs).get_task_states()
    pipeline_tree_str = TaskRecord.objects.get(pipeline_id=pipeline_id).pipeline_tree

    try:

        pipeline_tree = json.loads(pipeline_tree_str)
        for node_id in pipeline_tree:

            node_info = {"node_name": f"{format(pipeline_tree[node_id])}"}
            pipeline_child = pipeline_states[pipeline_id]['children']
            job_instance_id = PipelineTaskApi({'node_id': node_id}).get_node_job_id()
            app_id = TaskRecord.objects.get(pipeline_id=pipeline_id).app_id
            node_info['log_url'] = f"{JOB_URL}/{app_id}/execute/step/{job_instance_id}?from=historyList"

            if node_id not in pipeline_child.keys():
                # 节点尚未执行
                node_info['theme'] = 'default'
                node_info['node_status'] = '未执行'
                node_info['exec_time'] = 0
                return_data.append(node_info)
                continue

            if pipeline_child[node_id]['state'] == 'FINISHED':

                node_info['theme'] = 'success'
                # 节点执行成功不查询日志，直接返回"success"
                node_info['node_status'] = '执行完成'
                node_info['exec_time'] = (
                    pipeline_child[node_id]['archived_time']
                    - pipeline_child[node_id]['started_time']).seconds
                return_data.append(node_info)
                continue

            elif pipeline_child[node_id]['state'] == 'FAILED':
                if get_fail_node:
                    # 如果条件为真，表示直接返回失败的node_id信息即可，作为重试任务调用
                    fail_node_id = node_id
                    break

                node_info['theme'] = 'danger'
                node_info['node_status'] = '执行失败'
                node_info['exec_time'] = (
                    pipeline_child[node_id]['archived_time']
                    - pipeline_child[node_id]['started_time']).seconds
                return_data.append(node_info)
                continue

            else:
                # 其他情况代表节点正在执行中
                node_info['theme'] = 'info'
                node_info['node_status'] = '正在执行'
                node_info['content'] = (datetime.now().replace(tzinfo=timezone('UTC'))
                                        - pipeline_child[node_id]['started_time']).seconds

            return_data.append(node_info)

    except Exception as err:
        logger.warning(str(err))

    finally:
        if get_fail_node:
            return fail_node_id
        return return_data


def op_pipeline_task(kwargs):
    """
       对任务做管理操作，目前支持 任务启动，任务撤销，任务暂停, 任务重试
    """
    try:
        pipeline_id = kwargs.get("id")
        op_type = kwargs.get('op_type')
        if op_type == 'retry':
            fail_node_id = get_task_state({'pipeline_id': pipeline_id}, get_fail_node=True)
            if not fail_node_id:
                # 如果返回的node_id 为空，则重试任务失败，直接退出
                return build_fail_result("检测不到失败的node_id")

            task = PipelineTaskApi({'pipeline_id': pipeline_id, 'node_id': fail_node_id})
        else:
            task = PipelineTaskApi({'pipeline_id': pipeline_id})

        if op_type == 'revoke':
            if task.task_revoke():
                return build_success_result("操作成功")
            else:
                return build_fail_result("操作失败")

        elif op_type == 'resume':
            if task.task_resume():
                return build_success_result("操作成功")
            else:
                return build_fail_result("操作失败")

        elif op_type == 'pause':
            if task.task_pause():
                return build_success_result("操作成功")
            else:
                return build_fail_result("操作失败")

        elif op_type == 'retry':
            if task.task_retry():
                return build_success_result("操作成功")
            else:
                return build_fail_result("操作失败")
        else:
            return build_fail_result("后端暂不执行该类型操作:{}".format(op_type))

    except Exception as err:
        logger.error(str(err))
