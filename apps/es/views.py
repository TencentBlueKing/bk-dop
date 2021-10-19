# -*- coding: utf-8 -*-
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from proxy.views import proxy_view
from rest_framework import viewsets
from rest_framework.authentication import BasicAuthentication
from rest_framework.decorators import action

from apps.es.flow.es_flow import add_node_flow, deploy_cluster_flow, input_cluster_flow, reduce_node_flow
from apps.es.models import EsCluster, EsNodeInfo, EsRule, delete_es_cluster
from apps.es.parameter import (
    retrieval_es_add_node_param,
    retrieval_es_deploy_param,
    retrieval_es_input_param,
    retrieval_es_reduce_node_param,
)
from apps.es.serializers import EsClusterSerializers, EsNodeSerializers, EsRuleSerializers
from blueapps.utils.logger import logger
from common.utils.common import get_cc_app_id_by_user, machine_statistics, machine_statistics_group_app_id_top_five
from common.utils.custom_auth import CsrfExemptSessionAuthentication
from common.utils.utils import ApiMixin


class EsClusterViewSet(ApiMixin, viewsets.ModelViewSet):
    """
       es集群表视图
    """
    serializer_class = EsClusterSerializers
    filter_fields = ('cluster_name', 'add_type',)
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

    def get_queryset(self):
        """
            重写get_queryset方法，根据用户的业务权限来输出对应记录，用户隔离
        """
        app_id_list = self.request.query_params.get('selectedAppList')
        if not app_id_list:
            app_id_list = get_cc_app_id_by_user()
        else:
            app_id_list = app_id_list.split(',')

        return EsCluster.objects.filter(app_id__in=app_id_list).order_by("-create_time")

    @action(methods=['post'], detail=False)
    def create_cluster(self, request, *args, **kwargs):
        """
           POST /es/create_cluster es集群创建
        """
        try:
            post_data = request.data
            bk_username = request.user.username
            info = retrieval_es_deploy_param(post_data=post_data, bk_username=bk_username)
            if info['code'] == 0:
                # 参数存在异常返回失败
                return JsonResponse(info['data'])

            deploy_parameter = info['data']
            # 部署任务，检测是否正常
            if deploy_cluster_flow(deploy_parameter):
                return JsonResponse({"result": True, "data": [], "code": 0, "message": "部署任务已启动"})

            return JsonResponse({"result": False, "data": [], "code": 1, "message": "部署任务失败"})

        except Exception as e:
            logger.error(f'create pipeline failed:{e}')
            return JsonResponse({'result': False, 'code': 1, 'data': [], 'message': f'{e}'})

    @action(methods=['post'], detail=False)
    def add_node(self, request):
        """
           POST /api/es/add_node es节点扩容
        """
        try:
            post_data = request.data
            bk_username = request.user.username
            info = retrieval_es_add_node_param(post_data=post_data, bk_username=bk_username)
            if info['code'] == 0:
                # 参数存在异常返回失败
                return JsonResponse(info['data'])

            add_node_parameter = info['data']
            # 部署任务，检测是否正常
            if add_node_flow(add_node_parameter):
                return JsonResponse({"result": True, "data": [], "code": 0, "message": "扩容任务已启动"})

            return JsonResponse({"result": False, "data": [], "code": 1, "message": "扩容任务启动失败"})

        except Exception as e:
            logger.error(f'create pipeline failed:{e}')
            return JsonResponse({'result': False, 'code': 1, 'data': [], 'message': f'{e}'})

    @action(methods=['post'], detail=False)
    def reduce_node(self, request, *args, **kwargs):
        """
           POST /api/es/reduce_node es节点缩容
        """
        try:
            post_data = request.data
            bk_username = request.user.username
            info = retrieval_es_reduce_node_param(post_data=post_data, bk_username=bk_username)
            if info['code'] == 0:
                # 参数存在异常返回失败
                return JsonResponse(info['data'])

            reduce_node_parameter = info['data']
            # 部署任务，检测是否正常
            if reduce_node_flow(reduce_node_parameter):
                return JsonResponse({"result": True, "data": [], "code": 0, "message": "缩容任务已启动"})

            return JsonResponse({"result": False, "data": [], "code": 1, "message": "缩容任务启动失败"})

        except Exception as e:
            logger.error(f'create pipeline failed:{e}')
            return JsonResponse({'result': False, 'code': 1, 'data': [], 'message': f'{e}'})

    @action(methods=['post'], detail=False)
    def destroy_cluster(self, request, *args, **kwargs):
        """
           POST /api/es/destroy_cluster es集群回收
           集群回收操作只清空后端数据，不作进程回收
        """
        try:
            cluster_name = request.data['cluster_name']
            if delete_es_cluster(cluster_name=cluster_name):
                return JsonResponse({"result": True, "data": [], "code": 0, "message": "集群信息删除成功"})

            return JsonResponse({"result": False, "data": [], "code": 1, "message": "集群信息删除失败"})

        except Exception as e:
            logger.error(f'create pipeline failed:{e}')
            return JsonResponse({'result': False, 'code': 1, 'data': [], 'message': f'{e}'})

    @action(methods=['post'], detail=False)
    def input_cluster(self, request, *args, **kwargs):
        """
           POST /es/input_cluster es集群录入
        """
        try:
            post_data = request.data
            bk_username = request.user.username
            info = retrieval_es_input_param(post_data=post_data, bk_username=bk_username)
            if info['code'] == 0:
                # 参数存在异常返回失败
                return JsonResponse(info['data'])

            input_parameter = info['data']
            # 部署任务，检测是否正常
            if input_cluster_flow(input_parameter):
                return JsonResponse({"result": True, "data": [], "code": 0, "message": "集群录入任务已启动"})

            return JsonResponse({"result": False, "data": [], "code": 1, "message": "集群录入任务启动失败"})

        except Exception as e:
            logger.error(f'create pipeline failed:{e}')
            return JsonResponse({'result': False, 'code': 1, 'data': [], 'message': f'{e}'})


class EsNodeViewSet(ApiMixin, viewsets.ModelViewSet):
    """
        es用户信息表视图
    """
    queryset = EsNodeInfo.objects.all()
    serializer_class = EsNodeSerializers
    filter_fields = ('cluster_name',)
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

    @action(methods=['post'], detail=False)
    def get_machine_statistics(self, request, *args, **kwargs):
        """
           POST /es/nodes/get_machine_statistics 统计es投入已使用的机器数量
        """
        try:
            app_id_list = get_cc_app_id_by_user()
            data_result = machine_statistics(table_set=EsNodeInfo, field='ip', app_id_list=app_id_list)
            return JsonResponse({"result": True, "code": 0, "data": data_result, "message": "query success"})

        except Exception as err:
            logger.error(f'es机器查询汇总失败:{err}')
            return JsonResponse({'result': False, 'code': 1, 'data': '0', 'message': f'{err}'})

    @action(methods=['post'], detail=False)
    def get_machine_statistics_top_five(self, request, *args, **kwargs):
        """
           POST /es/nodes/get_machine_statistics_top_five
           根据用户已有业务权限，查询每个业务的机器投入数量，输出TOP5
        """
        try:
            app_dict = get_cc_app_id_by_user(res="print_name")
            data_result = machine_statistics_group_app_id_top_five(
                table_set=EsNodeInfo,
                field='ip',
                app_dict=app_dict)

            return JsonResponse({"result": True, "code": 0, "data": data_result, "message": "query success"})

        except Exception as err:
            logger.error(f'查询前5位业务的es机器使用数量汇总失败:{err}')
            return JsonResponse({'result': False, 'code': 1, 'data': [], 'message': f'{err}'})


class EsRuleViewSet(ApiMixin, viewsets.ModelViewSet):
    """
        es用户信息表视图
    """

    queryset = EsRule.objects.all()
    serializer_class = EsRuleSerializers
    filter_fields = ('cluster_name',)
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)


@csrf_exempt
def kibana_view(request, cluster, path):
    """
        Kibana反向代理
    """
    global kibana_cluster
    global kibana_ip
    kibana_cluster = cluster
    if locals().get('kibana_ip', globals().get('kibana_ip')) is None:
        logger.debug('Do db query')
        cluster = EsNodeInfo.objects.filter(cluster_name=kibana_cluster)[:1].get()
        kibana_ip = cluster.ip
    remote_url = f'http://{kibana_ip}:5603/es/kibana/{kibana_cluster}/{path}'
    logger.info(f'remote_url: {remote_url}')
    return proxy_view(request, remote_url)


@csrf_exempt
def cerebro_view(request, cluster, path):
    """
        Cerebro反向代理
    """
    global cerebro_cluster
    global cerebro_ip
    cerebro_cluster = cluster
    if locals().get('cerebro_ip', globals().get('cerebro_ip')) is None:
        logger.debug('Do db query')
        cluster = EsNodeInfo.objects.filter(cluster_name=cerebro_cluster)[:1].get()
        cerebro_ip = cluster.ip
    remote_url = f'http://{cerebro_ip}:1234/es/cerebro/{cerebro_cluster}/{path}'
    logger.info(f'remote_url: {remote_url}')
    return proxy_view(request, remote_url)
