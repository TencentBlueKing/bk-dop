# -*- coding: utf-8 -*-
from django.http import JsonResponse

from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import action

from apps.kafka.flow.kafka_flow import (
    add_node_flow,
    deploy_cluster_flow,
    input_cluster_flow,
    install_kafka_cluster_monitor_flow,
    destroy_cluster_flow,
)
from apps.kafka.get_monitor_data import (
    get_data_in_cluster_monitor,
    get_data_in_consumer_group_monitor,
    get_data_in_topic_monitor,
)
from apps.kafka.models import KafkaBroker, KafkaCluster, Topic
from apps.kafka.parameter import (
    retrieval_kafka_add_node_param,
    retrieval_kafka_deploy_param,
    retrieval_kafka_input_param,
    retrieval_kafka_install_monitor_param, retrieval_kafka_destroy_param,
)
from apps.kafka.serializers import KafkaBrokerSerializers, KafkaClusterSerializers, TopicSerializers
from apps.kafka.topic_ops import check_topic_param, create_topic
from blueapps.utils.logger import logger
from common.utils.common import get_cc_app_id_by_user, machine_statistics, machine_statistics_group_app_id_top_five
from common.utils.custom_auth import CsrfExemptSessionAuthentication
from common.utils.utils import ApiMixin


class KafkaClusterViewSet(ApiMixin, viewsets.ModelViewSet):
    """
        kafka集群表视图
    """
    serializer_class = KafkaClusterSerializers
    filter_fields = ('id', 'cluster_name',)
    authentication_classes = (CsrfExemptSessionAuthentication, SessionAuthentication)

    def get_queryset(self):
        """
            重写get_queryset方法，根据用户的业务权限来输出对应记录，用户隔离
        """
        app_id_list = self.request.query_params.get('selectedAppList')
        if not app_id_list:
            app_id_list = get_cc_app_id_by_user()
        else:
            app_id_list = app_id_list.split(',')

        return KafkaCluster.objects.filter(app_id__in=app_id_list).order_by("-create_time")

    @action(methods=['post'], detail=False)
    def create_cluster(self, request, *args, **kwargs):
        """
           POST /kafka/create_cluster  kafka集群创建
        """
        try:
            post_data = request.data
            bk_username = request.user.username
            info = retrieval_kafka_deploy_param(post_data=post_data, bk_username=bk_username)
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
    def add_broker(self, request):
        """
           POST /kafka/add_node  kafka broker节点创建
        """
        try:
            post_data = request.data
            bk_username = request.user.username
            info = retrieval_kafka_add_node_param(post_data=post_data, bk_username=bk_username)
            if info['code'] == 0:
                # 参数存在异常返回失败
                return JsonResponse(info['data'])

            add_node_parameter = info['data']
            # 部署任务，检测是否正常
            if add_node_flow(add_node_parameter):
                return JsonResponse({"result": True, "data": [], "code": 0, "message": "扩容任务已启动"})

            return JsonResponse({"result": False, "data": [], "code": 1, "message": "扩容任务失败"})

        except Exception as e:
            logger.error(f'create pipeline failed:{e}')
            return JsonResponse({'result': False, 'code': 1, 'data': [], 'message': f'{e}'})

    @action(methods=['post'], detail=False)
    def destroy_cluster(self, request, *args, **kwargs):
        """
           POST /kafka/destroy_cluster es集群回收
           集群回收操作只清空后端数据，不作进程回收
        """
        try:
            post_data = request.data
            bk_username = request.user.username
            info = retrieval_kafka_destroy_param(post_data=post_data, bk_username=bk_username)
            if info['code'] == 0:
                # 参数存在异常返回失败
                return JsonResponse(info['data'])

            destroy_parameter = info['data']
            # 部署任务，检测是否正常
            if destroy_cluster_flow(destroy_parameter):
                return JsonResponse({"result": True, "data": [], "code": 0, "message": "集群回收已启动，但不会关闭集群"})

            return JsonResponse({"result": False, "data": [], "code": 1, "message": "集群回收已启动失败"})

        except Exception as e:
            logger.error(f'create pipeline failed:{e}')
            return JsonResponse({'result': False, 'code': 1, 'data': [], 'message': f'{e}'})

    @action(methods=['post'], detail=False)
    def input_cluster(self, request, *args, **kwargs):
        """
           POST /kafka/input_cluster es集群录入
        """
        try:
            post_data = request.data
            bk_username = request.user.username
            info = retrieval_kafka_input_param(post_data=post_data, bk_username=bk_username)
            if info['code'] == 0:
                # 参数存在异常返回失败
                return JsonResponse(info['data'])

            input_parameter = info['data']
            # 部署任务，检测是否正常
            if input_cluster_flow(input_parameter):
                return JsonResponse({"result": True, "data": [], "code": 0, "message": "录入任务已启动"})

            return JsonResponse({"result": False, "data": [], "code": 1, "message": "录入任务失败"})

        except Exception as e:
            logger.error(f'create pipeline failed:{e}')
            return JsonResponse({'result': False, 'code': 1, 'data': [], 'message': f'{e}'})


class KafkaBrokerViewSet(ApiMixin, viewsets.ModelViewSet):
    """
        kafka broker信息表视图
    """
    queryset = KafkaBroker.objects.all()
    serializer_class = KafkaBrokerSerializers
    filter_fields = ('cluster_name',)
    authentication_classes = (CsrfExemptSessionAuthentication, SessionAuthentication)

    @action(methods=['post'], detail=False)
    def get_machine_statistics(self, request, *args, **kwargs):
        """
           POST /kafka/brokers/get_machine_statistics 统计kafka投入已使用的机器数量
        """
        try:
            app_id_list = get_cc_app_id_by_user()
            data_result = machine_statistics(table_set=KafkaBroker, field='ip', app_id_list=app_id_list)
            return JsonResponse({"result": True, "code": 0, "data": data_result, "message": "query success"})

        except Exception as err:
            logger.error(f'kafka机器查询汇总失败:{err}')
            return JsonResponse({'result': False, 'code': 1, 'data': '0', 'message': f'{err}'})

    @action(methods=['post'], detail=False)
    def get_machine_statistics_top_five(self, request, *args, **kwargs):
        """
           POST /kafka/brokers/get_machine_statistics_top_five
           根据用户已有业务权限，查询每个业务的机器投入数量，输出TOP5
        """
        try:
            app_dict = get_cc_app_id_by_user(res="print_name")
            data_result = machine_statistics_group_app_id_top_five(
                table_set=KafkaBroker,
                field='ip',
                app_dict=app_dict)

            return JsonResponse({"result": True, "code": 0, "data": data_result, "message": "query success"})

        except Exception as err:
            logger.error(f'查询前5位业务的kafka机器使用数量汇总失败:{err}')
            return JsonResponse({'result': False, 'code': 1, 'data': [], 'message': f'{err}'})

    @action(methods=['post'], detail=False)
    def get_kafka_monitor_data(self, request, *args, **kwargs):
        """
            POST /kafka/brokers/monitor_data
            根据用户返回过滤条件，查询监控平台的监控数据并汇总到前端
            返回字典格式
        """
        try:
            post_data = request.data
            bk_username = request.user.username
            get_type = post_data.get("get_type")
            if get_type == "cluster":
                # 根据cluster维度来获取监控数据
                data_result = get_data_in_cluster_monitor(post_data, bk_username)
            elif get_type == "topic":
                # 根据topic维度来获取监控数据
                data_result = get_data_in_topic_monitor(post_data, bk_username)
            elif get_type == "consumer_group":
                # 根据consumer_group维度来获取监控数据
                data_result = get_data_in_consumer_group_monitor(post_data, bk_username)
            else:
                logger.warning(f"匹配不到传入的维度，请检测: get_type:{get_type}")
                data_result = []

            return JsonResponse({"result": True, "code": 0, "data": data_result, "message": "query success"})

        except Exception as err:
            logger.error(f'查询并汇总监控数据失败:{err}')
            return JsonResponse({'result': False, 'code': 1, 'data': [], 'message': f'查询并汇总监控数据失败:{err}'})

    @action(methods=['post'], detail=False)
    def create_monitor(self, request, *args, **kwargs):
        """
            POST /kafka/brokers/create_monitor
            部署集群监控
        """
        try:
            post_data = request.data
            bk_username = request.user.username
            info = retrieval_kafka_install_monitor_param(post_data=post_data, bk_username=bk_username)
            if info['code'] == 0:
                # 参数存在异常返回失败
                return JsonResponse(info['data'])

            install_parameter = info['data']
            if install_kafka_cluster_monitor_flow(install_parameter):
                return JsonResponse({"result": True, "data": [], "code": 0, "message": "监控部署任务已启动"})

            return JsonResponse({"result": False, "data": [], "code": 1, "message": "监控部署任务失败"})

        except Exception as err:
            logger.error(f'创建集群监控失败:{err}')
            return JsonResponse({"result": False, "data": [], "message": f'{err}', "code": 1})


class KafkaTopicViewSet(ApiMixin, viewsets.ModelViewSet):
    """
        kafka topic信息表视图
    """
    queryset = Topic.objects.all()
    serializer_class = TopicSerializers
    filter_fields = ('cluster_name',)
    authentication_classes = (CsrfExemptSessionAuthentication, SessionAuthentication)

    @action(methods=['post'], detail=False)
    def create_topic(self, request, *args, **kwargs):
        """
           /kafka/create_topic 创建kafka topic信息
        """
        try:
            post_data = request.data
            bk_username = request.user.username
            if create_topic(post_data, bk_username):
                return JsonResponse({'result': True, 'code': 0, 'data': [], 'message': 'topic创建成功'})
            else:
                return JsonResponse({'result': False, 'code': 1, 'data': [], 'message': 'topic创建失败'})
        except Exception as e:
            logger.error(f'create failed:{e}')
            return JsonResponse({'result': False, 'code': 1, 'data': [], 'message': f'{e}'})

    @action(methods=['post'], detail=False)
    def check_topic(self, request, *args, **kwargs):
        """
           /kafka/check_topic 后台查询kafka topic状态信息
        """
        try:
            post_data = request.data
            bk_username = request.user.username
            param_data = check_topic_param(post_data, bk_username)
            return JsonResponse({'result': True, 'code': 0, 'data': param_data, 'message': 'topic查询成功'})

        except Exception as e:
            logger.error(f'query failed:{e}')
            return JsonResponse({'result': False, 'code': 1, 'data': [], 'message': f'{e}'})
