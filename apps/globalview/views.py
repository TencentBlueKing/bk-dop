# -*- coding: utf-8 -*-
from django.dispatch import receiver
from django.http import JsonResponse
from django.shortcuts import render

from pipeline.eri.signals import post_set_state
from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import action

from adapter.api import CCApi
from apps.globalview.bamboo_task_op import get_task_state, op_pipeline_task
from apps.globalview.models import TaskRecord, get_task_statistics
from apps.globalview.serializers import TaskRecordSerializers
from blueapps.utils.logger import logger
from common.utils.bamboo_signal import change_state_by_signal
from common.utils.common import get_cc_app_id_by_user
from common.utils.custom_auth import CsrfExemptSessionAuthentication
from common.utils.utils import ApiMixin


class TaskRecordViewSet(ApiMixin, viewsets.ModelViewSet):
    """
       执行记录RDF视图类，用户可根据集群名称，任务创建时间过滤执行记录数据
    """
    serializer_class = TaskRecordSerializers
    filter_fields = ('db_type', 'cluster_name', 'task_status')
    authentication_classes = (CsrfExemptSessionAuthentication, SessionAuthentication)

    def get_queryset(self):
        """
           重写get_queryset方法，根据用户的业务权限来输出对应记录，用户隔离
        """
        app_id_list = get_cc_app_id_by_user()
        start = self.request.query_params.get('start_time', None)
        stop = self.request.query_params.get('stop_time', None)
        if start and stop:
            return TaskRecord.objects.filter(
                app_id__in=app_id_list).filter(
                create_time__range=[start, stop]
            ).order_by("-create_time")

        return TaskRecord.objects.filter(app_id__in=app_id_list).order_by("-create_time")

    @action(methods=['post'], detail=False)
    def get_task_sum_group_by_db(self, request, *args, **kwargs):
        """
           输出各db组件的的执行记录数
        """
        try:
            app_id_list = get_cc_app_id_by_user()
            task_result = get_task_statistics(app_id_list)
            return JsonResponse({"result": True, "data": task_result, "message": "query success"})

        except Exception as err:
            logger.error(f'查询分组失败:{err}')
            return JsonResponse({'result': False, 'code': 1, 'data': [], 'message': f'{err}'})

    @action(methods=['post'], detail=False)
    def get_task(self, request, *args, **kwargs):
        """
           POST /record/get_task_data 对对应的流程task做详情流程操作，流程详情
        """
        try:
            post_data = request.data
            task_data = get_task_state(post_data)
            return JsonResponse({"result": True, "data": task_data, "message": "query success"})

        except Exception as err:
            logger.error(f'查询任务信息失败:{err}')
            return JsonResponse({'result': False, 'code': 1, 'data': [], 'message': f'{err}'})

    @action(methods=['post'], detail=False)
    def op_task(self, request, *args, **kwargs):
        """
           POST /record/op_task  对对应的流程task做管理操作，流程暂停/流程撤销/流程执行
        """
        try:
            post_data = request.data
            op_data = op_pipeline_task(post_data)
            return JsonResponse(op_data['data'])

        except Exception as err:
            logger.error(f'后台操作该task异常:{err}')
            return JsonResponse({'result': False, 'code': 1, 'data': [], 'message': f'后台操作该task异常{err}'})


def get_app_by_user(request):
    """
       根据用户信息获取配置平台中已有权限的业务信息列表，非RDF视图处理
       @param request: 前端请求
    """
    kwargs = {"fields": ["bk_biz_id", "bk_biz_name"]}
    try:
        result = CCApi.search_business(kwargs, raw=True)
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({"result": False, "code": 1, "data": None, "message": f"{e}"})


@receiver(post_set_state)
def task_handler(sender, node_id, to_state, root_id, **kwargs):
    """
       接收pipeline的signal，同步变更动作
    """
    change_state_by_signal(node_id, to_state, root_id)


def index(request):
    """首页"""

    return render(request, "index.html", {}, )
