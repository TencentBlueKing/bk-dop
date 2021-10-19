# -*- coding:utf-8 _*-
import copy
import json

from bamboo_engine import api
from bamboo_engine.builder import Data, EmptyEndEvent, EmptyStartEvent, ServiceActivity, SubProcess, Var, build_tree
from pipeline.eri.runtime import BambooDjangoRuntime

from apps.globalview.models import create_record_detail, update_record_detail
from blueapps.utils.logger import logger


'''
@summary: 定义使用蓝鲸开源的 pipeline-bamboo 的类操作，结合平台需求，耦合后台操作
@usage:
'''


class BambooFlow(object):
    """
       BambooFlow类：创建bamboo流程的对象，活动节点所有的需要参数都是通过流程上下文传递，流程上下文只要一个dict参数，参数名称统一：act_info
       @param act_tree: 流程树字典，默认为空，用于存储流程中每个自定义的活动节点名称，存储于后端数据，方便前端展示并查阅
       @param db_type: 内部定义的db组件id, 每个id都会对应不同的db组件
       @param param_info: 参数字典，存储流程中所需要的参数信息
    """

    def __init__(self, db_type, param_info, act_tree=None):
        if act_tree is None:
            act_tree = {}

        self.start_act = EmptyStartEvent()
        self.end_act = EmptyEndEvent()
        self.db_type = db_type
        self.param_info = param_info
        self.act_tree = act_tree
        self.task_id = 0

        # 定义流程数据上下文
        self.global_data = Data()
        self.global_data.inputs['${act_info}'] = Var(type=Var.PLAIN, value=self.param_info)
        self.pipe = self.start_act

    def check_param(self):
        """
           检测传入param_info 参数是否合法
        """
        if not self.param_info or not isinstance(self.param_info, dict):
            logger.error(f"任务传入参数不规范 param_info:{self.param_info}")
            return False

        return True

    def create_record_detail(self, task_type):
        """
            create_record_detail方法：存储任务记录
            @param task_type: 内部定义的任务流程id, 每个id都会对应不同的任务名称，这样方便后端统一管理，并节省数据库存储字段的长度，优化搜索
        """
        task_info = copy.deepcopy(self.param_info)
        # 屏蔽 password 等字段，防止录入到数据库
        if task_info.get('password'):
            task_info.pop('password')

        self.task_id = create_record_detail(
            {
                "db_type": self.db_type,
                "app_id": self.param_info['app_id'],
                "cluster_name": self.param_info['cluster_name'],
                "task_type": task_type,
                "task_mode": 1,
                "pipeline_id": "000",
                "op_user": self.param_info['bk_username'],
                "task_params": task_info,
            }
        )
        if self.task_id == 0:
            logger.error("task表生成失败，任务结束")
            return False

        return True

    def add_sub(self, sub_flow, act_tree):
        """
           add_sub 方法： 为流程加入子流程
           @param sub_flow: 子流程
           @param act_tree: 子流程树
        """
        self.act_tree = {**self.act_tree, **act_tree}
        self.pipe = self.pipe.extend(sub_flow)
        return self

    def add_act(self, act_name, act_component_code, private_list=None):
        """
           add_act 方法：为流程加入活动节点，并加入流程数字典
           @param act_name: 自定义活动节点名称，最好定义可读性高的名称，方便前端查询
           @param act_component_code: 指定的活动节点的原子名称，原子需要事先创建完成，并且按照规范引入对应参数
           @param private_list: 传递活动节点的私有变量, 内部元素为dict：格式：{'name': xxx , 'value': xxx }
        """
        if not private_list:
            private_list = []

        act = ServiceActivity(name=act_name, component_code=act_component_code)
        self.act_tree[act.id] = act.name
        act.component.inputs.act_info = Var(type=Var.SPLICE, value='${act_info}')

        # 如果定义活动节点的私有变量，则遍历加载
        for private_var in private_list:
            act.component.inputs[private_var['name']] = Var(type=Var.PLAIN, value=private_var['value'])

        self.pipe = self.pipe.extend(act)
        return self

    def build_bamboo(self):
        """
           build_bamboo方法：建立流程任务
        """

        self.pipe.extend(self.end_act)
        bamboo_task = build_tree(self.start_act, data=self.global_data)
        update_record_detail(self.task_id, {"pipeline_id": bamboo_task['id']})
        update_record_detail(self.task_id, {"pipeline_tree": json.dumps(self.act_tree)})

        if not api.run_pipeline(runtime=BambooDjangoRuntime(), pipeline=bamboo_task).result:
            logger.error("部署bamboo流程任务创建失败，任务结束")
            return False

        return True


class BambooSubFlow(BambooFlow):
    """
      BambooFlow类：创建bamboo子流程的对象，活动节点所有的需要参数都是通过流程上下文传递，流程上下文只要一个dict参数，参数名称统一：act_info
    """

    def build_sub_bamboo(self):
        """
           build_sub_bamboo方法: 建立子流程树
        """
        self.pipe.extend(self.end_act)
        return SubProcess(start=self.start_act, data=self.global_data), self.act_tree
